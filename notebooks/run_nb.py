# %% [markdown]
# ---
# title: GWF workflow to run a notebook
# subtitle: Each target is a new notebook to run
# execute: 
#   eval: false
# ---

# %% [markdown]
"""
## Usage:

Run a specific notebook with the following command:

`gwf -f run_nb.py run <notebook_name>`
where `<notebook_name>` is the name of the notebook you want to run without the `.ipynb` extension.
"""


# %% [markdown]
"""
## Imports and utility functions
"""

# %%
import os
from pathlib import Path
from gwf import Workflow, AnonymousTarget
import glob

def run_notebook(path, memory='8g', walltime='00:10:00', cores=1):    
    """
    Executes a notebook inplace and saves the output.
    """
    # path of output sentinel file
    sentinel = f'.{str(Path(path).name)}.sentinel'

    inputs = [path]
    outputs = {'sentinel': sentinel}
    options = {'memory': memory, 'walltime': walltime, 'cores': cores, 
               'mail_type': 'END,FAIL', 'mail_user': '201906763@post.au.dk'} 

    # commands to run in task (bash script)
    spec = f"""
# source $(conda info --base)/etc/profile.d/conda.sh
# conda activate hic
jupyter nbconvert --to notebook --execute --inplace --allow-errors --ExecutePreprocessor.iopub_timeout=600 {path} && touch {sentinel}
"""
    # return target
    return AnonymousTarget(inputs=inputs, outputs=outputs, options=options, spec=spec)

# %% [markdown]
"""
## List the available notebooks to run
""" 

# %%
# list all notebooks in the current directory
notebooks = glob.glob('*.ipynb')

# %% [markdown]
"""
## Loop through notebooks and generate a target for each
""" 

# %% 
# Create a GWF workflow object
gwf = Workflow(defaults={'account': 'hic-spermatogenesis'})

for notebook in notebooks:
    # Define the name
    par, nb = os.path.split(notebook)
    nb = nb.split('.')[0]

    gwf.target_from_template(
        name='run_'+nb,
        template=run_notebook(notebook, memory='64g', walltime='12:00:00', cores=8)
    )