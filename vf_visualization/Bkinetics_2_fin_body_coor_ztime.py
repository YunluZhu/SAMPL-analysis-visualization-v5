'''
Fin-body ratio with new definitions slightly different from eLife 2019. Works well.

plot attack angle vs. early body change (-250 to -50 ms), fit with a sigmoid w/ 4-free parameters

zeitgeber time? Yes
'''

#%%
import os
import pandas as pd # pandas library
import numpy as np # numpy
import seaborn as sns
import matplotlib.pyplot as plt
from astropy.stats import jackknife_resampling
from scipy.optimize import curve_fit
from plot_functions.get_data_dir import (get_data_dir,get_figure_dir)
from plot_functions.get_bout_features import get_bout_features
from plot_functions.plt_tools import (jackknife_mean,set_font_type, defaultPlotting,distribution_binned_average)

set_font_type()
defaultPlotting(size=16)
# %%
pick_data = 'wt_fin'
which_zeitgeber = 'day' # day / night / all
which_atk_ang = 'atk_ang_phased' # atk_ang or 'atk_ang_phased'
DAY_RESAMPLE = 0
NIGHT_RESAMPLE = 500
# %%
def sigmoid_fit(df, x_range_to_fit,func,**kwargs):
    lower_bounds = [0.1,-20,-100,1]
    upper_bounds = [5,20,2,100]
    x0=[0.1, 1, -1, 20]
    
    for key, value in kwargs.items():
        if key == 'a':
            x0[0] = value
            lower_bounds[0] = value-0.01
            upper_bounds[0] = value+0.01
        elif key == 'b':
            x0[1] = value
            lower_bounds[1] = value-0.01
            upper_bounds[1] = value+0.01
        elif key == 'c':
            x0[2] = value
            lower_bounds[2] = value-0.01
            upper_bounds[2] = value+0.01
        elif key =='d':
            x0[3] = value
            lower_bounds[3] = value-0.01
            upper_bounds[3] = value+0.01
            
    p0 = tuple(x0)
    popt, pcov = curve_fit(func, df['rot_early_body_change'], df[which_atk_ang], 
                        #    maxfev=2000, 
                           p0 = p0,
                           bounds=(lower_bounds,upper_bounds))
    y = func(x_range_to_fit,*popt)
    output_coef = pd.DataFrame(data=popt).transpose()
    output_fitted = pd.DataFrame(data=y).assign(x=x_range_to_fit)
    p_sigma = np.sqrt(np.diag(pcov))
    return output_coef, output_fitted, p_sigma

def sigfunc_4free(x, a, b, c, d):
    y = c + (d)/(1 + np.exp(-(a*(x + b))))
    return y

# %%
# Select data and create figure folder
root, FRAME_RATE = get_data_dir(pick_data)

X_RANGE = np.arange(-5,10.01,0.01)
BIN_WIDTH = 0.5
AVERAGE_BIN = np.arange(min(X_RANGE),max(X_RANGE),BIN_WIDTH)

folder_name = f'BK2_fin_body_z{which_zeitgeber}'
folder_dir = get_figure_dir(pick_data)
fig_dir = os.path.join(folder_dir, folder_name)

try:
    os.makedirs(fig_dir)
    print(f'fig folder created: {folder_name}')
except:
    print('Notes: re-writing old figures')

# %% get features
all_feature_cond, all_cond1, all_cond2 = get_bout_features(root, FRAME_RATE, ztime = which_zeitgeber)

# %% tidy data
df_toplt = all_feature_cond.sort_values(by=['condition','expNum']).reset_index(drop=True)
if FRAME_RATE > 100:
    df_toplt.drop(df_toplt[df_toplt['spd_peak']<7].index, inplace=True)
elif FRAME_RATE == 40:
    df_toplt.drop(df_toplt[df_toplt['spd_peak']<4].index, inplace=True)

# df_toplt.drop(df_toplt[df_toplt['pitch_pre_bout']<0].index, inplace=True)
# %%
angles_day_resampled = pd.DataFrame()
angles_night_resampled = pd.DataFrame()

if which_zeitgeber != 'night':
    angles_day_resampled = df_toplt.loc[
        df_toplt['ztime']=='day',:
            ]
    if DAY_RESAMPLE != 0:  # if resampled
        angles_day_resampled = angles_day_resampled.groupby(
                ['dpf','condition','expNum']
                ).sample(
                        n=DAY_RESAMPLE,
                        replace=True
                        )
if which_zeitgeber != 'day':
    angles_night_resampled = df_toplt.loc[
        df_toplt['ztime']=='night',:
            ]
    if NIGHT_RESAMPLE != 0:  # if resampled
        angles_night_resampled = angles_night_resampled.groupby(
                ['dpf','condition','expNum']
                ).sample(
                        n=NIGHT_RESAMPLE,
                        replace=True
                        )
df_toplt = pd.concat([angles_day_resampled,angles_night_resampled],ignore_index=True)
# %% fit sigmoid - master
all_coef = pd.DataFrame()
all_y = pd.DataFrame()
all_binned_average = pd.DataFrame()


for (cond_abla,cond_dpf,cond_ztime), for_fit in df_toplt.groupby(['condition','dpf','ztime']):
    expNum = for_fit['expNum'].max()
    jackknife_idx = jackknife_resampling(np.array(list(range(expNum+1))))
    for excluded_exp, idx_group in enumerate(jackknife_idx):
        coef, fitted_y, sigma = sigmoid_fit(
            for_fit.loc[for_fit['expNum'].isin(idx_group)], X_RANGE, func=sigfunc_4free
        )
        slope = coef.iloc[0,0]*(coef.iloc[0,3]) / 4
        fitted_y.columns = ['Attack angle','Early body rotation']
        all_y = pd.concat([all_y, fitted_y.assign(
            dpf=cond_dpf,
            condition=cond_abla,
            excluded_exp = excluded_exp,
            ztime=cond_ztime,
            )])
        all_coef = pd.concat([all_coef, coef.assign(
            slope=slope,
            dpf=cond_dpf,
            condition=cond_abla,
            excluded_exp = excluded_exp,
            ztime=cond_ztime,
            )])
    binned_df = distribution_binned_average(for_fit,by_col='rot_early_body_change',bin_col=which_atk_ang,bin=AVERAGE_BIN)
    binned_df.columns=['Early body rotation',which_atk_ang]
    all_binned_average = pd.concat([all_binned_average,binned_df.assign(
        dpf=cond_dpf,
        condition=cond_abla,
        ztime=cond_ztime,
        )],ignore_index=True)
    
all_y = all_y.reset_index(drop=True)
all_coef = all_coef.reset_index(drop=True)
all_coef.columns=['k','xval','min','height',
                  'slope','dpf','condition','excluded_exp','ztime']
all_ztime = list(set(all_coef['ztime']))
all_ztime.sort()
# %%
# plot bout frequency vs IBI pitch and fit with parabola
defaultPlotting(size=12)

plt.figure()

g = sns.relplot(x='Early body rotation',y='Attack angle', data=all_y, 
                kind='line',
                col='dpf', col_order=all_cond1,
                row = 'ztime', row_order=all_ztime,
                hue='condition', hue_order = all_cond2,ci='sd',
                )
for i , g_row in enumerate(g.axes):
    for j, ax in enumerate(g_row):
        sns.lineplot(data=all_binned_average.loc[
            (all_binned_average['dpf']==all_cond1[j]) & (all_binned_average['ztime']==all_ztime[i]),:
                ], 
                    x='Early body rotation', y=which_atk_ang, 
                    hue='condition',alpha=0.5,
                    ax=ax)
upper = np.percentile(df_toplt[which_atk_ang], 95)
lower = np.percentile(df_toplt[which_atk_ang], 5)
g.set(ylim=(lower, upper))

filename = os.path.join(fig_dir,"attack angle vs Early body rotation.pdf")
plt.savefig(filename,format='PDF')

# plt.show()

# %%
# plot 
# plt.close()
defaultPlotting(size=12)
plt.figure()
p = sns.catplot(
    data = all_coef, y='slope',x='dpf',kind='point',join=False,
    col_order=all_cond1,ci='sd',
    row = 'ztime', row_order=all_ztime,
    # units=excluded_exp,
    hue='condition', dodge=True,
    hue_order = all_cond2,
)
p.map(sns.lineplot,'dpf','slope',estimator=None,
      units='excluded_exp',
      hue='condition',
      alpha=0.2,
      data=all_coef)
filename = os.path.join(fig_dir,"slope_together.pdf")
plt.savefig(filename,format='PDF')

# plt.show()
# %%
defaultPlotting(size=12)
for coef_name in ['k','xval','min','height','slope']:
    plt.figure()
    p = sns.catplot(
        data = all_coef, y=coef_name,x='condition',kind='point',join=False,
        col='dpf',col_order=all_cond1,
        ci='sd',
        row = 'ztime', row_order=all_ztime,
        # units=excluded_exp,
        hue='condition', dodge=True,
        hue_order = all_cond2,
        sharey=False,
        aspect=.6,
    )
    p.map(sns.lineplot,'condition',coef_name,estimator=None,
        units='excluded_exp',
        color='grey',
        alpha=0.2,
        data=all_coef)
    sns.despine(offset=10)
    filename = os.path.join(fig_dir,f"{coef_name} by cond1.pdf")
    
    plt.savefig(filename,format='PDF')
# %%
