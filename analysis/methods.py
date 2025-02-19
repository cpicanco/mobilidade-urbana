# -*- coding: utf-8 -*-
'''
    Copyright (C) 2025 Rafael Picanço e Abdala Maciel.

    The present file is distributed under the terms of the GNU General Public License (GPL v3.0).
    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
'''
import os, csv, itertools
import unidecode
import calendar
from glob import glob

import numpy as np
import dateutil.parser as dateparser

def load_observation(path, version='1.0'):
    """
        Returns a numpy array with observations (time is in ms) where:

        keytime,
            is the monotonically increasing time of key presses.

        videotime,
            is the frame time of the video captured by a key press.

        Participants could pause, rewind and resume the video at any time.
        Hence, "videotime" here may not be monotonic and may repeat.

        We must use videotime to calculate concordance.
    """
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
    glob_lists = sorted(glob_lists)
    glob_lists = glob_lists[0] # remove encapsulation
    return [item for item in glob_lists]

def bikes_per_minute(observations:np.array, video_length:int, minute_size:int = 60000):
    """
        Count the number of bikes per minute.
        We use numpy vectorization, don't need to sort "observations".
    """
    counts_per_minute = []
    for minute in range(1, (video_length//minute_size)+1):
        X = observations <= minute_size*minute
        Y = observations > minute_size*(minute-1)
        counts_per_minute.append(np.sum(X & Y))
    return counts_per_minute, np.sum(counts_per_minute)

def calculate_concordance(filename1:str, filename2:str, per_minute_array=False):
    """
    Here we assume that filename1 and filename2 have the same underlying video.
    """
    video_len = int(load_header_data(filename1)['duration_ms']) # hence, the same video length
    data1 = np.array(load_observation(filename1)['videotime'])
    data2 = np.array(load_observation(filename2)['videotime'])
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

    if per_minute_array:
        return {'concordance': concordances,
                'count': [count1, count2],
                'count_min':np.min([count1, count2]),
                'count_max':np.max([count1, count2]),
                'files':[filename1, filename2],
                'video_length':video_len}
    else:
        return {'concordance':np.average(concordances),
                'count': np.average([count1, count2]),
                'count_min':np.min([count1, count2]),
                'count_max':np.max([count1, count2]),
                'files':[filename1, filename2],
                'video_length':video_len}

class Tag:
    """
    We use standard tags to identify observation sessions.
    """
    def __init__(self, filename: str):
        self.filename = filename

        phase = os.path.basename(filename).split('_')[0]
        date, phase = phase.split('-')
        phase = phase.upper()
        try:
            weekday = dateparser.parse(date).weekday()
        except:
            weekday = 0

        weekday = calendar.day_name[weekday].upper()
        header_data = load_header_data(filename)
        turn = header_data['turn']
        # observer = header_data['observer']
        self.id = '_'.join([turn, date, phase, weekday])

    def as_array(self):
        return [self.id, self.filename]

def calculate_concordance_pairwise(target_tags:list[Tag], per_minute_array=False):
    """
    Returns a list of concordances calculated pairwise with all possible combinations.
    """
    size = len(target_tags)
    if size < 2:
        print('Warning: Can''t calculate concordance with just one observer file.')
        return {}
    else: # calculate concordance pairwise for all combinations
        files = [tag.filename for tag in target_tags]
        concordances = []
        for (target_file1, filename2) in itertools.combinations(files, 2):
            concordances.append(calculate_concordance(target_file1, filename2, per_minute_array))
        return {target_tags[0].id: concordances}

def rate_of_bikes(data: dict, dayname: str):
    """
    Find best averaged concordance pairwise.

    Now, only for averaged concordances calculated with "per_minute_array=False"
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

def sessions_dict(standard_tags: list[Tag], return_concordance_per_minute=False):
    unique_tag_ids = list(set([tag.id for tag in standard_tags]))
    data = {}
    for unique_id in unique_tag_ids:
        observations = [tag for tag in standard_tags if tag.id == unique_id]
        data.update(calculate_concordance_pairwise(observations, return_concordance_per_minute))
    return data

def unique_days_from_dict(data: dict):
    days = []
    for key in data.keys():
        days.append(key.split('_')[3])
    return list(set(days))

if __name__ == '__main__':
    # see main.py to an export_to_csv example

    # simple example
    street = 'oliveira-paiva'
    observation_session_filenames = [
        # three observers of the street in the same day
        os.path.join(street, '20190728-POS_OLIVEIRA-PAIVA_MANHA_ABDALA.csv'),
        os.path.join(street, '20190728-POS_OLIVEIRA-PAIVA_MANHA_JOSE.csv'),
        os.path.join(street, '20190728-POS_OLIVEIRA-PAIVA_MANHA_RAQUEL.csv')
    ]

    data = sessions_dict([Tag(filename) for filename in observation_session_filenames])
    print(data)
    print('')

    for day in unique_days_from_dict(data):
        for day_data in rate_of_bikes(data, day):
            for key, value in day_data.items():
                print(key, value)