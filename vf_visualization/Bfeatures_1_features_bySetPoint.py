'''
Plot bout features - UD separated by set point

zeitgeber time? Yes
jackknifed? Yes
sampled? Yes - one sample number for day and night
- change the var DAY_RESAMPLE to select the number of bouts sampled per condition per repeat. 
- to disable sampling, change DAY_RESAMPLE to 0 
- If ztime == all, day and night count as 2 conditions
- for the pd.sample function, replace = True
'''

#%%
# import sys
import os
import pandas as pd
import numpy as np # numpy
import seaborn as sns
import matplotlib.pyplot as plt
from plot_functions.get_data_dir import (get_data_dir, get_figure_dir)
from plot_functions.get_bout_features import get_bout_features
from plot_functions.get_bout_kinetics import get_kinetics
from plot_functions.get_IBIangles import get_IBIangles
from plot_functions.plt_tools import (jackknife_mean_by_col,set_font_type, defaultPlotting)
import matplotlib as mpl

set_font_type()
mpl.rc('figure', max_open_warning = 0)

# %%
# Select data and create figure folder
pick_data = 'tau_long'
which_ztime = 'day'
DAY_RESAMPLE = 1000

# %%
root, FRAME_RATE = get_data_dir(pick_data)

folder_name = f'BF1_bySetPoint_z{which_ztime}_sample{DAY_RESAMPLE}'
folder_dir = get_figure_dir(pick_data)
fig_dir = os.path.join(folder_dir, folder_name)

try:
    os.makedirs(fig_dir)
    print(f'fig folder created: {folder_name}')
except:
    print('Notes: re-writing old figures')

# %% get features
all_feature_cond, all_cond1, all_cond2 = get_bout_features(root, FRAME_RATE, ztime=which_ztime)
# all_ibi_cond, _, _  = get_IBIangles(root, FRAME_RATE, ztime=which_ztime)
# %% tidy data
# all_feature_cond = all_feature_cond.loc[all_feature_cond['spd_peak']>4]
all_feature_cond = all_feature_cond.sort_values(by=['condition','expNum']).reset_index(drop=True)
# all_ibi_cond = all_ibi_cond.sort_values(by=['condition','expNum']).reset_index(drop=True)

# all_ibi_cond = all_ibi_cond.assign(y_boutFreq=1/all_ibi_cond['propBoutIEI'],
                                    # direction = pd.cut(all_ibi_cond['propBoutIEI_pitch'],[-90,7.5,90],labels=['dive','climb']))


# %%

# assign up and down 

all_feature_UD = pd.DataFrame()
all_feature_cond = all_feature_cond.assign(direction=np.nan)
for (this_dpf,this_cond,this_ztime), group in all_feature_cond.groupby(['dpf','condition','ztime']):
    set_point = get_kinetics(group)['set_point']
    group['direction'] = pd.cut(group['pitch_pre_bout'],
                                bins=[-90,set_point,90],
                                labels=['dn','up'])
    group = group.assign(
        dpf = this_dpf,
        condition = this_cond,
        ztime = this_ztime
    )
    all_feature_UD = pd.concat([all_feature_UD,group],ignore_index=True) 

# %%
# Plots

# %%
#mean
cat_cols = ['condition','expNum','direction','dpf','bout_time','ztime']
feature_to_plt = [c for c in all_feature_UD.columns if c not in cat_cols]
feature_for_comp = feature_to_plt + ['expNum']
# jackknife
all_feature_sampled = all_feature_UD

if DAY_RESAMPLE != 0:
    all_feature_sampled = all_feature_sampled.groupby(
            ['dpf','condition','expNum','direction']
            ).sample(
                    n=DAY_RESAMPLE,
                    replace=True
                    )

cat_cols = ['dpf','condition','direction','expNum']
mean_data = all_feature_sampled.groupby(cat_cols).mean()
mean_data = mean_data.reset_index()

cat_cols = ['dpf','condition','direction']

mean_data_jackknife = all_feature_sampled.groupby(cat_cols)[feature_for_comp].apply(
    lambda x: jackknife_mean_by_col(x,'expNum')
 )
mean_data_jackknife = mean_data_jackknife.reset_index()
# %%plot
toplt = mean_data_jackknife

for feature in feature_to_plt:
    
    g = sns.catplot(data=toplt, 
                    y = feature,
                    x='condition',
                    col="dpf", col_order=all_cond1,
                    row="direction",hue='condition',
                    sharey=False,
                    kind='point', marker=['d','d'],
                    aspect=.8,
                )
    (g.map(sns.lineplot,'condition',feature,
          estimator=None,
          units='jackknife_idx',
          data = toplt,
        #   hue='expNum',
          color='grey',
          alpha=0.2,))
    sns.despine(offset=10, trim=False)
    filename = os.path.join(fig_dir,f"jackknifed val {feature}.pdf")
    plt.savefig(filename,format='PDF')
    plt.close()
    
# %%
toplt = mean_data

for feature in feature_to_plt:
    
    g = sns.catplot(data=toplt, 
                    y = feature,
                    x='condition',
                    col="dpf", row="direction",col_order=all_cond1,
                    hue='condition',
                    sharey=False,
                    kind='point', 
                    # marker=['d','d'],
                    aspect=.8,
                )
    (g.map(sns.lineplot,'condition',feature,
          estimator=None,
          units='expNum',
          data = toplt,
          color='grey',
          alpha=0.2,))
    sns.despine(offset=10, trim=False)
    filename = os.path.join(fig_dir,f"raw val {feature}.pdf")
    plt.savefig(filename,format='PDF')
    plt.close()
# %%
