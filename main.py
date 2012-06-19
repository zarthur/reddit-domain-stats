#!/usr/bin/env python3

"""Calculate, load, and store domain information for reddit posts.
Requires Python 3.
"""

import json
import os
import pylab

HOME_PATH = home = os.getenv('USERPROFILE') or os.getenv('HOME')
DATA_PATH = os.path.join(HOME_PATH, '.reddit')
DATA_FILE = 'data'
ALL_DATA_FILE = 'data_all'
DATE_FILE = 'dates'

try:
    os.makedirs(DATA_PATH)
except OSError:
    #if directory already exists, do nothing
    pass

def _gen_data_dict(dictionary, key, value):
"""Update dictionary by appending value if key in dictionary and
the associated value is a list.  If the key is not in the dictionary or
the associated value is not a list (malformed), create a new key, value
pair.
"""
    if key in dictionary and isinstance(dictionary[key], list):
        dictionary[key].append(value)
    else:
        dictionary[key] = [value]
    return dictionary

def _get_response(req_url, json_resp=True):
"""Get response from a sepecified URL; process JSON if response
is JSON, else return data from URL request.
"""
    request = urllib.request.Request(req_url)
    req_data = urllib.request.urlopen(request)
    data = json.loads(req_data.read().decode()) \
            if json_resp else req_data
    return data

class reddit_averages(object):
"""Container for data and associated methods."""

    def __init__(self):
    """Initialize data containers and set path."""
        self._all_data = None
        self._data = None
        self._date_data = None
        self._data_file = os.path.join(DATA_PATH, DATA_FILE)
        self._all_data_file = os.path.join(DATA_PATH, ALL_DATA_FILE)
        self._date_data_file = os.path.join(DATA_PATH, DATE_FILE)

    @staticmethod
    def _get_reddit_data():
        date_date = datetime.now().strftime('%Y-%d-%m %H:%M:%S')
        data = _get_response('http://www.reddit.com/.json')
        all_data = _get_response('http://www.reddit.com/r/all/.json')

        return data, all_data, date_data

    @staticmethod
    def _load_data_file(filename):
    """Load saved data from file."""
        with open(filename) as infile:
            try:
                data = json.loads(infile)
            except:
                data = {}
        return data

    @staticmethod
    def _save_data_file(filename, data):
    """Save data to file."""
        with open(filename, 'w') as out_file:
            json.dump(data, out_file)

    def get_user_totals(self):
    """Return total number of posts by user."""
        pass

    def get_domain_totals(self):
    """Return todal number of posts per unique domain name."""
        pass

    def is_data_loaded(self):
    """Return true if data is loaded, false otherwise."""
        return bool(self._data) and bool(self._all_data) and \
               bool(self._date_data)

    def load_data(self, override=False):
    """Load data from various files"""
        if not self.is_data_loaded() or override:
            self._data = self._load_data_file(self._data_file)
            self._all_data = self._load_all_data(self._all_data_file)
            self._date_data = self._load_all_data(self._date_data_file)

    def save_data(self):
    """Save data to various files"""
        self._save_data(self._data_file, self._data)
        self._save_data(self._all_data_file, self._all_data)
        self._save_data(self._date_data_file. self._date_data)

    def update(self):
    """Update data with values from website."""
        self.load_data()
        data, all_data, date_data = self._get_reddit_data()

    def update_data_dict(dict, key, newval)

    def generate_graph(self, xvec, yvec, filename):
    """Generate bar graph of the data, save to file."""
        pass

if __name__ == "__main__":
    reddit = reddit_averages()
    reddit.update()
