# -*- coding: utf-8 -*-
'''
    Copyright (C) 2019 Rafael Picanço e Abdala Maciel.

    The present file is distributed under the terms of the GNU General Public License (GPL v3.0).
    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

from main import all_data
from methods import get_data_root_path

import os
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

# pre, pos, fu1, fu2 = all_data['rogaciano-leite']
# fu1 = np.hstack([datum for datum in fu1 if datum != 0])
# all_data['rogaciano-leite'] = [pre, pos, fu1, fu2]

# pre, pos, fu1, fu2 = all_data['oliveira-paiva']
# all_data['oliveira-paiva'] = [pre, pos,[0],[0]]

tags = all_data['oliveira-paiva'][0]
rates = all_data['oliveira-paiva'][1]
min_delta = all_data['oliveira-paiva'][2]
max_delta = all_data['oliveira-paiva'][3]

pre_manha_rate = [rate for rate, tag in zip(rates, tags) if ('PRE' in tag) and ('MANHA' in tag)]
pre_manha_min_delta = [delta for delta, tag in zip(max_delta, tags) if ('PRE' in tag) and ('MANHA' in tag)]
pre_manha_max_delta = [delta for delta, tag in zip(min_delta, tags) if ('PRE' in tag) and ('MANHA' in tag)]

pre_tarde_rate = [rate for rate, tag in zip(rates, tags) if ('PRE' in tag) and ('TARDE' in tag)]
pre_tarde_min_delta = [delta for delta, tag in zip(max_delta, tags) if ('PRE' in tag) and ('TARDE' in tag)]
pre_tarde_max_delta = [delta for delta, tag in zip(min_delta, tags) if ('PRE' in tag) and ('TARDE' in tag)]

labels = ['terça', 'quarta', 'quinta', 'domingo']
men_means = [20, 34, 30, 35, 27]
women_means = [25, 32, 34, 20, 25]
yminmax1 = np.array([pre_manha_min_delta, pre_manha_max_delta]) 
yminmax2 = np.array([pre_tarde_min_delta, pre_tarde_max_delta])

x = np.arange(len(labels))  # the label locations
width = 0.35  # the width of the bars

fig, ax = plt.subplots()
pre_manha_boxs = ax.bar(x - width/2, pre_manha_rate, width, label='Manhã', yerr=yminmax1)
pre_tarde_boxs = ax.bar(x + width/2, pre_tarde_rate, width, label='Tarde', yerr=yminmax2)

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Bicicletas por Hora')
ax.set_title('Bicicletas por Hora na Oliveira Paiva')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

fig.tight_layout()

filename = os.path.join(get_data_root_path(),'figure_1_bars.png')
plt.savefig(filename)