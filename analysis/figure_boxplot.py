# -*- coding: utf-8 -*-
'''
    Copyright (C) 2019 Rafael Picanço e Miguel Abdala Maciel.

    The present file is distributed under the terms of the GNU General Public License (GPL v3.0).
    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

from main import boxplot_data
from methods import get_data_root_path

import os
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt


pre, pos, fu1, fu2 = boxplot_data['rogaciano-leite']
fu1 = np.hstack([datum for datum in fu1 if datum != 0])
boxplot_data['rogaciano-leite'] = [pre, pos, fu1, fu2]

flierprops = dict(markersize=2)
xticks = np.hstack([.2, .4, .6, .8])
fig, ax = plt.subplots(1, 2, figsize=(7, 3),sharey=True)
i = 0
for street_name, street_data in boxplot_data.items():
    ax[i].set_title(street_name)
    print(street_data)
    ax[i].boxplot(street_data,
        widths=[0.1, 0.1, 0.1, 0.1],
        positions=xticks,
        flierprops=flierprops)
    # first axes
    ax[i].set_xlabel('Phase')
    ax[i].set_ylabel('Bikes/hour')
    ax[i].set_xticks(xticks)
    ax[i].set_xticklabels(['PRE', 'POS', 'F1', 'F2'])
    i += 1

fig.tight_layout()

filename = os.path.join(get_data_root_path(),'figure_1.png')
plt.savefig(filename)