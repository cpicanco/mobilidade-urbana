# -*- coding: utf-8 -*-
'''
    Copyright (C) 2025 Rafael Picanço e Abdala Maciel.

    The present file is distributed under the terms of the GNU General Public License (GPL v3.0).
    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
'''
import os
import numpy as np

from methods import (
    Tag,
    sessions_dict,
    get_data_root_path,
    get_data_filenames,
)

all_paths = ['rogaciano-leite', 'virgilio-tavora', 'oliveira-paiva']
all_data = {'rogaciano-leite':None, 'virgilio-tavora':None, 'oliveira-paiva':None}

table = []
table.append([
    'street',
    'shift',
    'date',
    'phase',
    'weekday',
    'video_id',
    'video_minute',
    'count1',
    'count2',
    'concordance',
    'video_length'])

video_id = 0
for street in all_paths:
    root_path = os.path.join(get_data_root_path(), street)
    data_filenames = get_data_filenames(root_path)
    normalized_tags = [Tag(data_filename) for data_filename in data_filenames]
    data = sessions_dict(normalized_tags, True)
    for key, candidate_pairwise_observations in data.items():
        tag = key.split('_')
        shift = tag[0]
        date = tag[1]
        phase = tag[2]
        weekday = tag[3]

        if len(candidate_pairwise_observations) > 1:
            candidate_pairwise_observations.sort(key=lambda x: np.average(x['concordance']))
            best_observations = candidate_pairwise_observations[-1]
        elif len(candidate_pairwise_observations) == 1:
            best_observations = candidate_pairwise_observations[0]
        else:
            raise Exception(f'No observation for {key}')

        count_minute_by_minute1, count_minute_by_minute2 = best_observations['count_minutes']
        concordance_minute_by_minute = best_observations['concordance']
        for minute, (count1, count2, concordance) in enumerate(zip(
            count_minute_by_minute1,
            count_minute_by_minute2,
            concordance_minute_by_minute)):
            table.append([
                street,
                shift,
                date,
                phase,
                weekday,
                video_id,
                minute,
                count1,
                count2,
                concordance,
                best_observations['video_length']])
        video_id += 1

for row in table:
    if len(row) != 10:
        print(row)

np.savetxt(
    os.path.join('data_minute_by_minute.tsv'),
    table,
    delimiter="\t",
    fmt="%s"
)