-- Structure --
1. grid_run: Parameterized version of TARDIS which is configured to use slurm batch scripts and accept grids of model parameters to run.
2. interpolator: Takes the output from grid_run, consisting of the SEDs folder and parameters.log, and interpolates for new parameters.
3. spectral_calib: Flux calibrate spectra using photometric data, which can then be used by the interpolator to infer distance.
4. tardis_sandbox: Sandboxed version of TARDIS, to verify final model parameters independently from the emulator.

-- Pre-Run Sequence --
1. Ensure grid_run/tardis_data/base_config.yml is correct
2. Ensure grid_run/run/run.py has correct output location and units
3. Create grid_run/run/grid.csv
4. If modifying shell structure, update grid_run/make_csvy.py
5. Update sbatch script to match grid length
6. Update total threads in grid_run/run_tardis.py and base_config.yml if needed
7. Run sbatch script with tardis conda environment active

You can run individually by placing your grid in the run folder and using 'python run.py index'. Index refers to the literal line number in grid.csv, this is different from the ID which is first seen in each grid row then later stored in parameters.log and used to identify the SED files.