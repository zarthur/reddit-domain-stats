#!/usr/bin/env python3

"""Calculate, load, and store domain and user information for reddit posts.
Requires Python 3.
"""

import itertools
import json
import os
import pylab
import sys
import urllib
import urllib.request

from datetime import datetime

HOME_PATH = home = os.getenv('USERPROFILE') or os.getenv('HOME')
DATA_PATH = os.path.join(HOME_PATH, '.reddit-stats')
DATA_FILE = 'data'
ALL_DATA_FILE = 'data_all'
DATE_FILE = 'dates'
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36'

if not os.path.exists(DATA_PATH):
    os.makedirs(DATA_PATH)

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
    headers = {'User-Agent': USER_AGENT}
    request = urllib.request.Request(req_url, headers=headers)
    req_data = urllib.request.urlopen(request)
    data = json.loads(req_data.read().decode()) \
            if json_resp else req_data
    return data

class reddit_stats(object):
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
    def _extract_data(response):
        """Extract user/domain info from decoded JSON response."""
        try:
            children = response['data']['children']
            temp_dict = {}
            for child in children:
                temp_dict = _gen_data_dict(temp_dict, child['data']['author'],
                                           child['data']['domain'])
            return temp_dict
        except KeyError:
            return {}

    def _get_reddit_data(self):
        """Get reddit JSON data."""
        date_data = datetime.now().strftime('%Y-%d-%m %H:%M:%S')
        data = self._extract_data(_get_response('http://www.reddit.com/.json'))
        all_data = self._extract_data(_get_response(
                                        'http://www.reddit.com/r/all/.json'))

        return data, all_data, date_data

    @staticmethod
    def _load_data_file(filename, is_list=False):
        """Load saved data from file."""
        try:
            with open(filename) as infile:
                data = json.load(infile)
        except IOError:
            data = {} if not is_list else []
        return data

    @staticmethod
    def _save_data_file(filename, data):
        """Save data to file."""
        with open(filename, 'w') as out_file:
            json.dump(data, out_file)

    def get_user_totals(self):
        """Return total number of posts by user."""
        date_total = len(self._date_data)

        user_data = dict((key, len(value)) \
                        for key, value in self._data.items())

        user_all_data = dict((key, len(value)) \
                        for key, value in self._all_data.items())

        return user_data, user_all_data, date_total

    def get_domain_totals(self):
        """Return todal number of posts per unique domain name."""
        date_total = len(self._date_data)

        domain_list = [x[0] for x in itertools.chain(*self._data.values())]
        domain_all_list = [x[0] for x in
                           itertools.chain(*self._all_data.values())]

        domain_set = set(list(domain_list))
        domain_all_set = set(list(domain_all_list))

        domain_data = dict((entry, domain_list.count(entry)) \
                        for entry in domain_set)

        domain_all_data = dict((entry, domain_all_list.count(entry)) \
                        for entry in domain_all_set)

        return domain_data, domain_all_data, date_total

    def is_data_loaded(self):
        """Return true if data is loaded, false otherwise."""
        return bool(self._data) and bool(self._all_data) and \
               bool(self._date_data)

    def load_data(self, override=False):
        """Load data from various files"""
        if not self.is_data_loaded() or override:
            self._data = self._load_data_file(self._data_file)
            self._all_data = self._load_data_file(self._all_data_file)
            self._date_data = self._load_data_file(self._date_data_file)

    def save_data(self):
        """Save data to various files"""
        self._save_data_file(self._data_file, self._data)
        self._save_data_file(self._all_data_file, self._all_data)
        self._save_data_file(self._date_data_file, self._date_data)

    def update(self):
        """Update data with values from website."""
        self.load_data()
        data, all_data, date_data = self._get_reddit_data()

        if isinstance(self._date_data, list):
            self._date_data.append(date_data)
        else:
            self._date_data = [date_data]

        for key, value in data.items():
            self._data = _gen_data_dict(self._data, key, value)

        for key, value in all_data.items():
            self._all_data = _gen_data_dict(self._all_data, key, value)

        self.save_data()

    def generate_graph(self, data_dict, filename, samples):
        """Generate and save a plot from a data dictionary."""
        tuples = [(k, v) for k, v in data_dict.items()]
        tuples.sort(key=lambda x: x[1], reverse=True)

        if len(tuples) > 25:
            tuples = tuples[:25]
            title = 'Top 25, Samples =' + str(samples)
        else:
            title = 'Samples =' + str(samples)

        tuples.sort(key=lambda x: x[0])

        x, y = zip(*tuples)
        f = pylab.figure()
        ax = f.add_subplot(211)
        ax.bar(range(len(y)), y)
        tick_loc = [entry + 0.5 for entry in range(len(x))]
        ax.xaxis.set_ticks(tick_loc)
        ax.xaxis.set_ticklabels(x, rotation=90)
        ax.set_title(title)
        f.savefig(os.path.join(DATA_PATH, filename))


def main():
    reddit = reddit_stats()
    success = False
    attempts = 0
    while not success and attempts < 10:
        try:
            reddit.update()
        except urllib.error.HTTPError:
            attempts += 1
            continue
        success = True

    if attempts == 10 and not success:
        print('Unable to establish connection', file=sys.stderr)
        sys.exit()

    user_data, user_all_data, samples = reddit.get_user_totals()
    domain_data, domain_all_data, _ = reddit.get_domain_totals()

    file_dict =  {
        'user_data.png':user_data,
        'user_all_data.png': user_all_data,
        'domain_data.png': domain_data,
        'domain_all_data.png': domain_all_data,
    }

    for filename, data_dict in file_dict.items():
        reddit.generate_graph(data_dict, filename, samples)

if __name__ == "__main__":
    main()
