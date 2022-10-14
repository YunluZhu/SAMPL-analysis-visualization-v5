# Vertical Fish Analysis

This code is for analysis and visualization of data generated using free-swimming apparatus. 

The VF analysis package reads LabView .dlm files generated by free swimming vertical fish apparatus (preprocessing), extracts and analyzes bouts (bout_analysis), and makes figures (visualization).

Run `vf_analysis/vf_analysis_....py` to analyze .dlm files. Then, run individual visualization scripts under `vf_visualization/` to make figures. See below for detailed instructions.

**Warning:** This is repo contains my working visualization code, which means you may have to modify visualization scripts to work for your dataset (ana scripts should work out of the box though). Check the  [sister repo](https://github.com/YunluZhu/zebrafish_vertical_behavior) for a simplified version that plots basic plot.

## Version notes

**v4.1.220610**

1. Shortened aligned bout duration
2. Added arrangement scripts
3. Visualization code streamlined. Added functions to get features and kinetics
4. New Fin-Body algorithm
5. Visualization code now takes zeitgeber time (ztime) as a second input (other than `root`). Legal inputs are: `'day'`, `'night'`, and `'all'`.

**v4.3.220826**

1. Fixed a filter error on angular acceleration in analyze_dlm_v4.py. Now yields 50-80% more bouts
2. Added logging function. One log file will be generated the first time you run the ana code and will be updated every time you analyze a dataset.
3. Added the ability to skip dlm with no alignable bouts. With this version, to prevent error during ana process, just search under the root folder for “dlm”, delete any dlm file that are <1MB. Then you are safe to run the ana code.
4. Metadata handling updated. Can read ini files directly in the grab_fish_angle script and export metadata as a csv in parent folder
5. New visualization scripts.

**v4.4 221013**

1. Parameters redefined. See parameter table below for details
2. Fixed a bug in `get_bout_features()` `get_bout_kinetics()` `get_IBIangles()` causing oversampling of bouts

**To dos**

- change condition names to cond1 and cond2 from dpf/condition

## Prerequisites and tips

Build with Python3.8. See `environment.yml` for required packages.

1. Conda environment is recommended. Download miniconda here: <https://docs.conda.io/en/latest/miniconda.html>
2. Setting up conda envs can be the most time-consuming step. Be patient and prepare to Google a lot.
3. Visual Studio Code is a good IDE and is compatible with Jupyter Notebook
4. VS code Python Extension supports Interactive Window
    - You can create cells on a Python file by typing `# %%`
    - Use `Shift`+`Enter` to run a cell, the output will be shown in an interactive window

### Required packages

1. Essential packages can be found in `docs/environment_clean.yml`
2. Below is a list of essential packages:
  - numpy
  - pandas
  - tqdm
  - scipy
  - matplotlib
  - seaborn
  - scikit-learn
  - astropy
  - pytables

## Usage

### Contents

`docs` contains a copy of catalog files generated after running `.../vf_analysis/vf_analysis_by_folder_v4.py`, the conda env file, and expected number of swim bouts captured over 24 hrs per box in constant dark.

`docs/VF_analysis_paper` contains code for the behavior mechod manuscript that should work out of the box.

`vf_analysis` folder contains all the scripts for data analysis.

`vf_visualization` includes all scripts for plotting.

`vf_dataARR` contains code for raw data arrangement. These scripts read metadata files (.ini) and arrange raw data collected from multiple boxes into organized structure (see Data arrangement section below). Arrangement scripts are specific to the experiments so you may want to write your own code that works for your experimental conditions.

### Data arrangement

1. Organize .dlm files. Each folder with .dlm files will be recognized as one "experiment (exp)" during jackknife analysis. Therefore, if you want to combine all data from a certain clutch, put them into the same folder. See below for a sample structure. For the folders representing experimental conditions, 2 conditions separated by "_" are taken as inputs. e.g. `cond1_cond2`. For consistency, it is recommended to use `cond1` for the age of the fish and/or light-dark condition and mark the experimental condition using `cond2`.
2. However, for the analysis code to work, your data doesn't have to be in this structure. `vf_analysis/vf_analysis....py` looks for all .dlm under the directory and subfolders in the directory the user specifies. Therefore, it can be used to analyze data generated from a single experiment by giving it (in the example below) `root/7dd_ctrl/200607 ***` as the root directory. Again, all .dlm files under the same folder will be combined for analysis, if you want to treat them as different "conditions", move them into different parent folders and name the parent folders as described above.
3. It is recommended to wirte an arrangement code that reads metadata files (.ini) and organizes your .dlm data instead of moving files manually. See `vf_dataARR` for some sample scripts.
4. For Jackknife resampling to work properly, make sure the exp folders under each conditions can be sorted in the same alphabetical order. In the example below, (if intended to compare against each other,) experiment folders in `7dd_ctrl` correspond with those under `7dd_condition`. Folder names for experiment folders under each conditions don't need to be the same but should be in the same alphabetical order. If multiple repeats (experiment folders) are generated in a single day, one may name the experiment folders as `exp1`, `exp2` etc.

```bash
├── root
    ├── 07dd_ctrl
    │   ├── 200607 ***
    │   │   ├── ****.dlm
    │   │   ├── ****.dlm
    │   │   ├── ****.dlm
    │   ├── 200611 ***
    │   │   ├── ****.dlm
    │   │   ├── ****.dlm
    │   │   ├── ****.dlm
    ├── 07dd_condition
    │   ├── 200607 ***
    │   │   ├── ****.dlm
    │   │   ├── ****.dlm
    │   │   ├── ****.dlm
    │   ├── 200611 ***
    │   │   ├── ****.dlm
    │   │   ├── ****.dlm
    │   │   ├── ****.dlm
    └── 04dd_ctrl
        └── 20**** ***
            └── ****.dlm
```

### Analyze raw data files

To analyze data generated using the free-swimming apparatus:

1. Run `vf_analysis/vf_analysis_....py`.
2. Follow the instruction and input the root path that contains data files (.dlm) and corresponding metadata files (.ini). Data can be directly under the root directory or under subfolders within the root directory. See notes for details.
3. Follow the instruction and input the frame rate (in integer). See notes for details.
4. The program will go through every data file in each subfolder (if there is any) and extract swim attributes.

When done, there will be three hdf5 files (.h5) under each directory that contains data file(s) together with catalog files that explains the parameters extracted. A copy of catalog files can be found under `docs`.

All the extracted swim bouts under `bout_data.h5` are aligned at the time of the peak speed. Each aligned bout contains swim parameters from 500 ms before to 300 ms after the time of the peak speed.

**Notes** on data analysis

- All the .dlm data files under the same directory will be combined for bout extraction. To analyze data separately, please move data files (.dlm) and corresponding metadata files (.ini) into subfolders under the root path.
- Analysis program will stop if it fails to detect any swim bout in a data file (.dlm). To avoid this, please make sure all data files to be analyzed are reasonably large so that it contains at least one swim bout. Generally, we found > 10 MB being a good criteria.
- Please input the correct frame rate as this affects calculation of parameters. This program only accepts one frame rate number for each run. Therefore, all data files under the root path need to be acquired under the same frame rate.

### Make figures

1. **IMPORTANT** update `vf_visualization/plot_functions/get_data_dir.py` to specify the names of your datasets and the directory of it. `get_data_dir(pick_data)` is called by every *visualization script*. Therefore, instead of typing directories for different datasets to plot everytime, specifying the name of your dataset in *visualization scripts* `pick_data = '<NAME OF YOUR DATASET>'` tells the script which data to plot. Also update the `get_figure_dir()` function in `get_data_dir.py`. This should be the root folder to save all plotted figures. Subfolders named by the name of your datadsets (input to `pick_data`) will be created under your `get_figure_dir(pick_data)` directory.
2. Run individual scripts under `vf_visualization/`.
    - each visualization script takes a root directory including all analyzed data, which should be same as the one fed to the analysis code. Visualization scripts calls `get_data_dir.py` to look for data directories.
    - all visualization scripts get experimental conditions and age info from folder names
    - jackknife is used for resampling in some scripts

**Visualization scripts and function** explained

1. Plot bout time series data
    - `Btimeseries_1_bySpdUD.py` plot bout features as a function of time (time series). Bouts are segmented by peak swim speed & separated by pitch up vs down.
    - `Btimeseries_2_pearsonr_angvel.py` plot Pearson correlation coefficient of angular velocity at each time point agains pre_bout pitch or initial pitch.
    - `Etimeseries_single_epoch.py` plot features vs time of a single epoch containing one or multiple bouts
2. Plot bout features
    - `Bfeatures_1_features.py` plot individual bout features.
    - `Bfeatures_3_distribution.py` looks at distribution of features. Also allows you to plot one feature against another in 2D histogram.
    - `Bfeatures_4_byPitch_UD_noJackknife.py` calculates binned average features by pitch and plot the mean as a function of pitch.
    - `Bfeatures_4_by....py`. Similarly, all other plot-by-feature scripts plot binned average of one feature against another.
3. Plot bout kinetics
    - `Bkinetics_fin_body_coor_ztime.py` plot fin-body coordination.
    - `Bkinetics_ztime.py` plot bout kinetics.
    - `Bkinetics_sigmoidRightingFit.py` plot righting fit in an x/y axis swapped manner and fit with a sigmoid. Compared to the original righting fit, this fit is more robust and displays the raw data
    - `IBI_pitch_mean_ztime.py` plot pitch distribution and its std() during inter bout interval (IBI).
    - `IBI_timing_ztime.py` plot bout frequency (reverse of IBI duration) as a function of pitch and fits it with a parabola.
    - `B_righting_fit.py` plot pre-pitch vs. decel rotation and fit with a sigmoid
    - `Bfeatures_corr.py` clusterred/correlation/heatmap for bout features
4. Inter bout interval plots
    - `IBI_pitch_mean_ztime` plot IBI pitch
    - `IBI_timing_ztime` plot bout rate vs IBI pitch

### Parameters

| Parameters                | Unit | Definition                                                                                |
| ------------------------- | ---- | ----------------------------------------------------------------------------------------- |
| Pitch angle               | deg  | Angle of the fish on the pitch axis relative to horizonal                                 |
| Peak speed                | mm/s | Peak speed of swim bouts                                                                  |
| Initial pitch             | deg  | Pitch angle at 250 ms before the peak speed                                               |
| Post-bout pitch           | deg  | Pitch angle at 100 ms after the peak speed                                                |
| End pitch                 | deg  | Pitch angle at 200 ms after the peak speed                                                |
| Acceleration phase        |      | Before time of the peak speed                                                             |
| Deceleration phase        |      | After time of the peak speed                                                              |
| Total rotation            | deg  | Pitch change from initial (250 ms before) to end (200 ms after) time of the peak speed    |
| Bout trajectory           | deg  | Tangential angle of the trajectory at the time of the peak speed                          |
| Bout displacement         | mm   | Displacement of fish from pre-bout to post-bout                                           |
| Inter-bout interval       | s    | Duration between two adjacent swim bouts                                                  |
| Inter-bout-interval pitch | deg  | Mean pitch angle during inter-bout interval                                               |
| Trajectory deviation      | deg  | Deviation of bout trajectory from initial pitch (250 ms before)                           |
| Steering rotation         | deg  | Change of pitch angle from initial (250 ms before) to the time of the peak speed          |
| Steering gain             |      | Slope of best fitted line of posture vs trajectory at the time of the peak speed          |
| Early rotation            | deg  | Change of pitch angle from initial (250 ms before) to 50 ms before time of the peak speed |
| Attack angle              | deg  | Deviation of bout trajectory from pitch at time of the peak speed                         |
| Fin-body ratio            |      | Maximal slope of best fitted sigmoid of attack angle vs early rotation                    |
| Righting rotation         | deg  | Change of pitch angle from time of the peak speed to post bout (100 ms after peak speed)  |
| Righting gain             |      | Numeric inversion of the slope of best fitted line of righting rotation vs initial pitch  |
| Set piont                 | deg  | x intersect of best fitted line of righting rotation vs initial pitch                     |

## Guides

### On analysis

1. Data analysis (running `vf_analysis_by_folder_v4.py`) takes time. Since the script goes through all the subfolders under root directory, be smart with the root input. There's no need to re-analyze the dataset if the .dlm files haven't been changed. In another word, if you've added new .dlm files into an analyzed folder containing old .dlm files, make sure to re-analyze this folder.
2. Always take the .ini metadata file when moving .dlm around or generate a metadata table containing experiment info for all the .dlm files.

### On plotting

1. Conditions (`cond1` `cond2`) are taken from parent folder names and sorted alphabetically. If you want them to be in a specific order, the easiest way to do is to add number before each condition, e.g.: `07dpf_1ctrl` `07dpf_2cond`.
2. Some scripts only compare data with different `cond2`, feel free to edit the scripts and make the comparison across other conditions.
3. Bouts are separated into "nose-up" and "nose-down" bouts based on their initial pitch. The cut point is at a fixed 10 deg for all the ages/conditions. This is generally true across all the dataset I've look at, YMMV. An alternative way is to calculate the set point for each condition and split bouts by their set points. This can be easily done by `groupby(['conditions', 'age', 'repeats', 'whatever']).apply(get_kinetics())` or looping through every sub-condition to apply `pd.cut()`.

### On data interpretation

1. Take any results based on <1000 bouts with a grain of salt. Some parameters (such as bout timing parabola fit and righting gain) require a large number of bouts (>5000) to start to converge.  
2. Always look at the time series plots first. Strong phenotypes can be seen on averaged time series results.
3. Then, look at distributions of parameters.
4. `Inter-bout interval pitch` shows posture/stability of fish. The timing parabola fit tells you their "preferred" posture, baseline bout rate (which can also be seen in IEI distribution plots), and sensitivity to posture changes.
5. Kinetics tells you how fish coordinate propulsion and rotation in general. `fin_body` and `steering gain` demonstrate fin engagement.
6. Lastly, check bout features (`Bfeatures_features` and `Bfeatures_4_by...`). Any subtle differences in the way fish swims can be picked up here. However, Jackknife resampling may "exaggerate" differences across fish with different backgrounds, so pay attention to the y-axis range.