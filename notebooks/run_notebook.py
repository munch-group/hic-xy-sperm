# %% [markdown]
# ---
# title: GWF workflow to run a notebook
# subtitle: Generate a notebook executor (inplace and save the output)
# execute:
#   eval: false
# ---

# %% [markdown]
"""
## Usage:

Run a specific notebook with the following command:

`gwf -f run_notebook.py:run.<notebook_name> run`

where `<notebook_name>` is the name of the notebook you want to run without the `.ipynb` extension.
For example, to run `example_notebook.ipynb`, use:
`gwf -f run_notebook.py:run.example_notebook run`
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


# %% [markdown]
"""
## Template function to run a notebook
""" 

# %% 
def run_notebook(path, memory='8g', walltime='00:10:00', cores=1):    
    """
    Executes a notebook inplace and saves the output.
    """
    # path of output sentinel file
    sentinel = f'.{str(Path(path).name)}.sentinel'

    inputs = [path]
    outputs = {'sentinel': sentinel}
    options = {'memory': memory, 'walltime': walltime, 'cores': cores} 

    # commands to run in task (bash script)
    spec = f"""
source $(conda info --base)/etc/profile.d/conda.sh
conda activate pymc
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
## Set up dynamic workflow generator
""" 

# %%
# loop through notebooks and generate a workflow object for each
for notebook in notebooks:
    # Define the name
    par, nb = os.path.split(notebook)
    nb = nb.split('.')[0]
    workflow_name = f"run.{nb}"

    wf = Workflow(defaults={'account': 'hic-spermatogenesis'})
    wf.target_from_template(
        name=f'run_{nb}',
        template=run_notebook(notebook, memory='32g', walltime='04:00:00', cores=8)
    )

    globals()[workflow_name] = wf
