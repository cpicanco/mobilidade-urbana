# -*- coding: utf-8 -*-
'''
    Copyright (C) 2019 Rafael Picanço e Abdala Maciel.

    The present file is distributed under the terms of the GNU General Public License (GPL v3.0).
    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
'''
import os, csv, itertools
import unidecode
from glob import glob
import numpy as np

def load_observation(path, version='1.0'):
    if not os.path.isfile(path):
        raise 'Path was not found:'+path
    if version == '1.0':
        skip_header = 8
        skip_footer = 0

    data = np.genfromtxt(
        fname=path,
        dtype=[('keytime','i8'), ('videotime','i8')],
        delimiter=",",
        missing_values=['nan'],
        skip_header=skip_header,
        skip_footer=skip_footer        
    )
    return data

def normalize_string(string):
    return unidecode.unidecode(string).upper().strip()

def load_header_data(path):
    with open(path, encoding='utf-8') as f:
        reader = csv.reader(f)
        place = next(reader)
        turn = next(reader)
        day = next(reader)
        if 'oliveira-paiva' in path:
            video_day = next(reader)
        else:
            video_day = 'None'
        observer = next(reader)
        phase = next(reader)
        duration = next(reader)
        duration_ms = next(reader)
    return {
        'place':normalize_string(place[1]),
        'turn':normalize_string(turn[1]),
        'day':normalize_string(day[1]),
        'video_day':normalize_string(video_day[1]),
        'observer':normalize_string(observer[1]),
        'phase':normalize_string(phase[1]),
        'duration':normalize_string(duration[1]),
        'duration_ms':normalize_string(duration_ms[1])
    }

def get_data_root_path():
    data_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(data_path)

def get_data_filenames(src_directory, gaze_file_filter='*.csv'):
    target_filters = [gaze_file_filter]
    glob_lists = [glob(os.path.join(src_directory, tf)) for tf in target_filters]
    return [item for item in sorted(glob_lists)]

def calculate_concordance(target_files):
    minute_size = 60000
    def bikes_per_minute(observations, video_length):
        counts_per_minute = []
        # use video_length%minute_size?
        for minute in range(1, (video_length//minute_size)+1):
            X = observations <= minute_size*minute
            Y = observations > minute_size*(minute-1)
            counts_per_minute.append(np.sum(X & Y))
        return counts_per_minute, np.sum(counts_per_minute)

    def calculate(target_file1, target_file2):
        video_len = int(load_header_data(target_file1)['duration_ms'])
        data1 = np.array(load_observation(target_file1)['videotime'])
        data2 = np.array(load_observation(target_file2)['videotime'])
        concordances = []
        counts_per_minute1, count1 = bikes_per_minute(data1, video_len)
        counts_per_minute2, count2 = bikes_per_minute(data2, video_len)
        for (datum1, datum2) in zip(counts_per_minute1, counts_per_minute2):
            if (datum1 == 0) and (datum2 == 0):
                concordances.append(100.0)
                continue
            if datum1 < datum2:
                concordances.append(datum1/datum2*100)
            else:
                concordances.append(datum2/datum1*100)

        return {'concordance':np.average(concordances),
                'count': np.average([count1,count2]),
                'count_min':np.min([count1,count2]),
                'count_max':np.max([count1,count2]),
                'files':[target_file1, target_file2],
                'video_length':video_len}
    
    size = len(target_files)
    if size == 2:
        return {target_files[0][0]:[calculate(target_files[0][1], target_files[1][1])]}
    elif size > 2:
        files = []
        for file in target_files:
            files.append(file[1])
        
        concordances = []
        for (target_file1, target_file2) in itertools.combinations(files, 2):
            concordances.append(calculate(target_file1, target_file2))
        return {target_files[0][0]:concordances}

def rate_of_bikes(data, dayname):
    """
    find best pairwise concordance and group data by independent variables (phase, day of week)
    """
    target_data = []
    day_data = [{tag: value} for tag, value in data.items() if dayname in tag]
    day_data.sort(key=lambda x:sorted(x.keys()))
    for datum in day_data:
        for tag, value in datum.items():
            if len(value) == 1:
                value[0].update({'tag':tag})
                target_data.append(value[0])
            else:
                value.sort(key=lambda x: x['concordance'])
                value[-1].update({'tag':tag})
                target_data.append(value[-1])
    to_hour = 1000*60*60
    return [{
            'tag':datum['tag'],
            'concordance':datum['concordance'],
            'files':datum['files'],
            'count':[datum['count_min'],datum['count_max']],
            'length':datum['video_length'],
            'count_min':datum['count_min']/(datum['video_length']/to_hour),
            'count_max':datum['count_max']/(datum['video_length']/to_hour),
            'rate':datum['count']/(datum['video_length']/to_hour)} \
            for datum in target_data]

def chunks(l, n):
    """
    https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
    Yield successive n-sized chunks from l.
    """
    for i in range(0, len(l), n):
        yield l[i:i + n]