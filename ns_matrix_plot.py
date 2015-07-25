import os

import numpy as np
import scipy as sp
import scipy.stats as stat
import matplotlib.pyplot as plt

from statsmodels.formula.api import ols
from statsmodels.graphics.api import interaction_plot, abline_plot
from statsmodels.stats.anova import anova_lm
import statsmodels.api as sm
import pandas as pd

import nibabel as nib
import epitome as epi

#file_name = 'young_december.csv'
file_name = 'old_december.csv'


labels = ['FEF', 
          'IPS', 
          'SPL7a', 
          'MT+', 
          'SPL7p', 
          'PrCv', 
          'PFCdp',
          'IPL',
          'STS',
          'MPFC',
          'PHC',
          'PCC']

data = np.genfromtxt(file_name, delimiter=',')

# zero the diagonal
for x in np.arange(len(data)):
     for y in np.arange(len(data)):
          if x == y:
               data[x,y] = 0


# figure out the colormapping
cm_max = np.max(data)
cm_min = np.min(data)
cm_lim = np.max((np.abs(cm_min), np.abs(cm_max)))

fig, ((ax1a, ax1b)) = plt.subplots(nrows=1, ncols=2, figsize=(5,3.1875))

x = np.arange(len(labels)+1)
y = np.arange(len(labels)+1)
x, y = np.meshgrid(x, y)

a = ax1a.pcolor(x, y, np.rot90(data), cmap='RdBu_r', 
                                     vmin=-cm_lim, 
                                     vmax=cm_lim,
                                     )
ax1a.set_yticks(np.flipud(np.linspace(0.5,11.5,num=12)))
ax1a.set_yticklabels(labels,fontsize=8)
ax1a.set_xticks(np.linspace(0.5,11.5,num=12))
ax1a.set_xticklabels(labels, fontsize=8, rotation=270)
ax1a.set_title(file_name)
fig.colorbar(a,cax=ax1b)
ax1b.set_aspect(7)

plt.tight_layout()
plt.savefig(file_name + '.svg')
