# -*- coding: utf-8 -*-
'''
    Copyright (C) 2019 Rafael Picanço e Abdala Maciel.

    The present file is distributed under the terms of the GNU General Public License (GPL v3.0).
    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
'''
import os

import calendar
import numpy as np
import dateutil.parser as dateparser

from methods import chunks, load_header_data
from methods import calculate_concordance, rate_of_bikes
from methods import get_data_root_path, get_data_filenames


all_paths = ['rogaciano-leite', 'virgilio-tavora', 'oliveira-paiva']

all_data = {'rogaciano-leite':None, 'virgilio-tavora':None, 'oliveira-paiva':None}

for path in all_paths:
    # load filenames
    root_path = os.path.join(get_data_root_path(),path)
    data_filenames = get_data_filenames(root_path)
    data_filenames = data_filenames[0] # remove encapsulation 

    # create a tag for each filename
    tags = []
    for data_filename in data_filenames:
        phase = os.path.basename(data_filename).split('_')[0]
        date, phase = phase.split('-')
        phase = phase.upper()
        weekday = dateparser.parse(date).weekday()
        weekday = calendar.day_name[weekday].upper()
        header_data = load_header_data(data_filename)
        turn = header_data['turn']
        # observer = header_data['observer']
        tag = '_'.join([turn, date, phase, weekday])
        tags.append([tag, data_filename])

    # use duplicated tags to group observations and calculate their concordance pairwise
    data = {}
    tags_no_repetition = list(set([tag[0] for tag in tags]))
    target_files = []
    for tag_nr in tags_no_repetition:
        for tag in tags:
            if tag[0] == tag_nr:
                target_files.append(tag)

        if len(target_files) > 1:
            data.update(calculate_concordance(target_files))
            target_files = []
        else:
            print('Can''t calculate concordance with just one data file.')
            print(target_files)

    # we must find all tags in our data dictionary,
    # elsewhere there is relevant missing data and we can't continue
    # use the following code to check
    # for tag in tags_no_repetition:
    #     print(data[tag])

    weeknames = ['TUESDAY','WEDNESDAY','THURSDAY','SUNDAY']
    bike_rate_by_day = [rate_of_bikes(data, weekname) for weekname in weeknames]

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

    # treating exceptions
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


    table_names = np.array(('tag', 'rate_average', 'rate_min','rate_max','concordance','files'))
    export_table = [
            tags,
            rates,
            count_min,
            count_max,
            concordance,
            file_list
        ]

    
    export_table = np.asarray(export_table).T
    export_table = np.insert(export_table, 0, table_names, 0)
    np.savetxt(
        os.path.join(root_path, 'data'),
        export_table,
        delimiter=",",
        fmt="%s")