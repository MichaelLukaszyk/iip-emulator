-- Structure --
1. grid_run: Parameterized version of TARDIS which is configured to use slurm batch scripts and accept grids of model parameters to run.
2. interpolator: Takes the output from grid_run, consisting of the SEDs folder and parameters.log, and interpolates for new parameters.
3. sandbox: Various utilities to verify final model parameters independently from the emulator and construct extra outputs.
4. spectral_calib: Flux calibrate spectra using photometric data, which can then be used by the interpolator to infer distance.

-- Install Steps --
1. Ensure there is a conda environment titled 'tardis' with TARDIS installed.
2. Run 'conda activate tardis', then 'pip install -e .' inside the directory containing the file 'pyproject.toml'.
3. Update parallel.sbatch with your credentials.

-- Pre-Run Sequence --
Inside the folder emulator/grid_run:
1. Create run/grid.csv using run/make_grid.ipynb
2. Ensure tardis_data/base_config.yml is correct.
3. If modifying shell structure, update make_csvy.py
4. Run 'bash run/submit.sh'

You can run individually by placing your grid in the run folder and using 'python run.py index'. Index refers to the literal line number in grid.csv, this is different from the ID which is first seen in each grid row then later stored in parameters.log and used to identify the SED files. Running 'python run.py -1' initializes the code, which is necessary to prevent issues at the start of parallel runs, this is done automatically by the submit.sh script.