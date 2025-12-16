# %% [markdown]
# ---
# title: "Create sex_chrom-specific coolers"
# subtitle: "Sex chromosome-specific .cool files from single-cell Hi-C pairs"
# author: Søren Jørgensen
# date: last-modified
# execute:
#   enabled: false
# ---

#######################################

# `gwf` workflow for creating .scool files from single-cell Hi-C pairs
# of sperm samples, originating from DOI 10.1038/s41467-025-59055-z.
# Matrices are separated based on metadata sheet defining the X/Y sex_chrom —
# (Supplementary Table 1).


# How to run:
# conda activate hic
# gwf status

# Pipeline:
# 0: Process the metadata sheet to create a list of samples and grouping (Pandas) 
# 1: Create .cool files from all single cells (including balancing)
# 2: Create merged .cool files from all single cells (including balancing)

#######################################

#%% [python]
from gwf import Workflow, AnonymousTarget
import os
from pathlib import Path
import pandas as pd
from glob import glob

# Create a workflow object
gwf = Workflow(defaults={'nodes': 1, 'queue':"normal", 'account':"hic-spermatogenesis"})


#############################################
############### Templates ###################
#############################################

# Template for creating .cool files from pairs
def pairs2cool(path, cool_out, chromsizes) -> AnonymousTarget:
    """
    Template to create a .cool file from pairs.
    
    Parameters:
    - pairs: Path to the input pairs file.
    - cooler: Path where the output .cool file will be saved.
    - chromsizes: Path to the chromosome sizes file.
    - balanced: Whether to balance the matrix or not.
    """
    inputs = {'pairs': f"steps/pairs/{path}",
              'chromsizes': chromsizes}
    outputs = {'cooler': cool_out}
    options = {
        'memory': '4g',
        'walltime': '00:10:00',
        'cores': 1 
    }
    spec = f"""
    pixi run cooler cload pairs \
        -c1 2 -p1 3 -c2 4 -p2 5 \
        --assembly 'GRCh38' \
        --chunksize 200000 \
        {inputs['chromsizes']}:1000 \
        {inputs['pairs']} \
        {outputs['cooler']}
    """
    return AnonymousTarget(inputs=inputs,outputs=outputs,options=options,spec=spec)

def merge_zoom_dir(dir: str, dependencies: dict) -> AnonymousTarget:
    """
    Template to merge .cool files from a directory into a single .cool file.
    
    Parameters:
    - dir: Directory containing the .cool files to merge.
    - out: Path where the merged .cool file will be saved.
    """
    dirname = Path(dir).name
    cores = 8
    inputs = {'dir': dir,
              'dependencies': dependencies}
    outputs = {'merged_cooler': f"steps/merged/sperm_{dirname}.merged.cool",
               'mcool': f"steps/merged/sperm_{dirname}.merged.mcool"}
    options = {
        'memory': '16g',
        'walltime': '02:00:00',
        'cores': cores 
    }
    spec = f"""
    mkdir -p steps/merged
    pixi run cooler merge {outputs['merged_cooler']} {os.path.join(inputs['dir'],'*.cool')} && \
    cooler zoomify --nproc {cores} \
    --resolutions 1000,5000,10000,50000,100000,500000 \
    --balance \
    --balance-args '--nproc {cores}' \
    -o {outputs['mcool']} \
    {outputs['merged_cooler']}
    """
    return AnonymousTarget(inputs=inputs,outputs=outputs,options=options,spec=spec)

#############################################
######### Process metadata and group ########
#############################################

# Chromsizes for the human genome GRCh38
chromsizes = "data/supplementary/GRCh38.chrom.sizes"

# Load metadata from the supplementary Excel file
meta = pd.read_excel("data/supplementary/41467_2025_59055_MOESM4_ESM.xlsx", sheet_name=0)

# Rename columns for easier access
meta.rename(columns={
    "Cell name": "name", 
    "QC passed": "qc_passed",
    "Structure valid": "structure_valid",
    "X/Y sample (haploid only)": "sex_chrom"
}, inplace=True)

# Queries for filtering
human = "Species == 'Homo sapiens'"
qc_passed = "qc_passed == True"
structure_valid = "structure_valid == True"
x_y_assigned = "sex_chrom.isin(['X', 'Y'])"

# Filter metadata for valid samples
valid = meta.query(f"{human} & {qc_passed} & {structure_valid} & {x_y_assigned}")

# Merge the sex_chrom onto the valid sample names and their filenames
filenames = pd.Series([os.path.basename(file) for file in glob("steps/pairs/*")])

pairs = pd.DataFrame({'path':filenames})
pairs[['GSM', 'name']] = filenames.str.split("_", expand=True)
pairs[['name', 'ext']] = pairs['name'].str.split('.',n=1, expand=True)

# Finally, filter the valid samples and merge the sex_chrom onto the pairs DataFrame
pairs = pairs.query("name in @valid.name")
pairs = pairs.merge(valid[['name','sex_chrom']], on='name', how='inner', )
pairs['cool_out'] = pairs.apply(
    lambda row: f"steps/coolers/{row['sex_chrom']}/{row['name']}.cool", axis=1)
pairs['chromsizes'] = chromsizes


#############################################
################# Targets ###################
#############################################

# Create coolers in folders matching the sex_chrom

pairs_X = pairs.query("sex_chrom == 'X'").filter(['path', 'cool_out', 'chromsizes']).to_dict(orient='records')
cool_X = gwf.map(pairs2cool, pairs_X,
                 name = lambda idx, _: f"pair2cool_X_{idx}")

pairs_Y = pairs.query("sex_chrom == 'Y'").filter(['path', 'cool_out', 'chromsizes']).to_dict(orient='records')
cool_Y = gwf.map(pairs2cool, pairs_Y,
                 name = lambda idx, _: f"pair2cool_Y_{idx}")

t2_inputs = [{'dir': 'steps/coolers/X/','dependencies': cool_X.outputs}, 
             {'dir':'steps/coolers/Y/', 'dependencies': cool_Y.outputs}]
T2 = gwf.map(merge_zoom_dir, t2_inputs,
            name = lambda idx, _: f"merge_zoom_{Path(t2_inputs[idx]['dir']).name}")


# %%
