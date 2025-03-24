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
    rate_of_bikes,
    get_data_root_path,
    get_data_filenames,
    unique_days_from_dict
)

all_paths = ['rogaciano-leite', 'virgilio-tavora', 'oliveira-paiva']
all_data = {'rogaciano-leite':None, 'virgilio-tavora':None, 'oliveira-paiva':None}

tables = []
for path in all_paths:
    root_path = os.path.join(get_data_root_path(), path)
    data_filenames = get_data_filenames(root_path)
    normalized_tags = [Tag(data_filename) for data_filename in data_filenames]
    data = sessions_dict(normalized_tags)
    week_day_names = unique_days_from_dict(data)
    bike_rate_by_day = [rate_of_bikes(data, weekname) for weekname in week_day_names]

    # # check if concordance is above or equal to 80%
    # for day in bike_rate_by_day:
    #     for datum in day:
    #         if datum['concordance'] >= 80:
    #             print(datum['files'], datum['concordance'])
    #         else:
    #             print(datum['files'], datum['concordance'], '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

    rates = []
    tags = []
    count_min = []
    count_max = []
    concordance = []
    file_list = []
    count = []
    length = []
    for day in bike_rate_by_day:
        for datum in day:
            length.append(datum['length'])
            count.append(datum['count'])
            file_list.append(datum['files'])
            concordance.append(datum['concordance'])
            rates.append(datum['rate'])
            count_min.append(datum['count_min'])
            count_max.append(datum['count_max'])
            tags.append(datum['tag'])

    count_min_delta = list(np.array(rates) - np.array(count_min))
    count_max_delta = list(np.array(count_max) - np.array(rates))

    # exceptions
    if 'rogaciano-leite' in root_path:
        length.insert(18, 0)
        count.insert(18,[0, 0])
        file_list.insert(18, [])
        concordance.insert(18, 0)
        rates.insert(18, np.nan)
        count_min.insert(18, 0)
        count_max.insert(18, 0)
        count_min_delta.insert(18, 0)
        count_max_delta.insert(18, 0)
        tags.insert(18, 'MANHA_20180802_F1_THURSDAY')

    all_data[path] = [tags, rates, count_min_delta, count_max_delta]

    ############################
    #          export          #
    ############################

    # split tags by underscore
    tags_column = [tag.split('_') for tag in tags]
    # each tag have a list of 4 elements, Turn, Date, Phase, Weekday
    shifts_column = [tag[0] for tag in tags_column]
    dates_column = [tag[1] for tag in tags_column]
    phases_column = [tag[2] for tag in tags_column]
    weekdays_column = [tag[3] for tag in tags_column]

    street_column = [path for _ in tags]

    # IOA = inter observer agreement
    table_names = np.array((
        'Street',
        'Shift',
        'Date',
        'Phase',
        'DOW',
        'RateAverage',
        'RateMin',
        'RateMax',
        'IOA',
        'Files'))

    export_table = [
            street_column,
            shifts_column,
            dates_column,
            phases_column,
            weekdays_column,
            rates,
            count_min,
            count_max,
            concordance,
            [str(f) for f in file_list]
        ]

    export_table = np.asarray(export_table).T
    export_table = np.insert(export_table, 0, table_names, 0)
    np.savetxt(
        os.path.join(root_path, path+'-data.tsv'),
        export_table,
        delimiter="\t",
        fmt="%s")
    tables.append(export_table)

np.savetxt(
    os.path.join('all-data.tsv'),
    np.vstack(tables),
    delimiter="\t",
    fmt="%s"
)