# -*- coding: utf-8 -*-
'''
    Copyright (C) 2019 Rafael Picanço e Miguel Abdala Maciel.

    The present file is distributed under the terms of the GNU General Public License (GPL v3.0).
    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

from main import barplot_data
from methods import get_data_root_path

import os
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

tick_tags = np.tile(['PRE', 'POS', 'F1', 'F2'], 8)

for streetname, streetdata in barplot_data.items():
    fig, ax = plt.subplots(figsize=(7, 3))
    bar_width = 0.20
    bar_gap = 0.10
    bar_length = bar_width+bar_gap

    i = 0
    indexes = []
    for rate_chunk, min_chunk, max_chunk in streetdata:
        index = np.arange(0,bar_length*4, bar_length) + i
        i = index[-1]+1
        ax.bar(index, rate_chunk, bar_width,
                alpha=0.4, color='k', yerr=[min_chunk,max_chunk], #error_kw=error_config
        )
        indexes.append(index)
    xticks = np.hstack(indexes)

    # first axes
    ax.set_xlabel('Morning  Afternoon  Morning  Afternoon  Morning  Afternoon  Morning  Afternoon\nTuesday                Wednesday                  Thurday                   Sunday')
    ax.set_ylabel('Bikes/hour')
    ax.set_xticks(xticks)
    ax.set_xticklabels(tick_tags, rotation='vertical')

    fig.tight_layout()

    filename = os.path.join(get_data_root_path(),'figure_'+streetname+'.png')
    plt.savefig(filename)
