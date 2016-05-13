# Copyright (C) 2015, 2016  Sheila Miguez, Will Kahn-Greene
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from collections import OrderedDict
import datetime
import json
import os

from clive.pyvideo_schema import SCHEMAS
from clive.schemalib import get_version


def load_json_data(path):
    """Parses and returns all video files for a path

    :arg path: a file or directory
    :returns: list of (filename, data) tuples for all .json files

    """
    if not path or not os.path.exists(path):
        return []

    if os.path.isfile(path):
        if not path.endswith('.json'):
            all_files = []
        else:
            all_files = [path]

    else:
        all_files = []

        for root, dirs, files in os.walk(path):
            all_files.extend(
                [os.path.join(root, fn) for fn in files if fn.endswith('.json')]
            )

    data = []

    for fn in sorted(all_files):
        with open(fn, 'r') as fp:
            data.append((fn, json.load(fp)))

    return data


def json_convert(obj):
    if isinstance(obj, datetime.date):
        return obj.strftime('%Y-%m-%d')
    if isinstance(obj, datetime.datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    return obj


def reorder_dict(object_type, json_data):
    """Converts dict to OrderedDict using schema order

    This reorders the data in a dict using the order the item is defined in the
    schema.

    """
    version = get_version(json_data)
    schema = SCHEMAS[version][object_type]

    new_dict = OrderedDict()

    for key, val in schema.keyvals:
        if key in json_data:
            new_dict[key] = json_data[key]

    return new_dict


def save_json_data(data_items):
    """Takes list of (fn, data) tuples and saves them all to disk

    :arg data_items: list of (fn, data) tuples to save

    """
    for fn, data in data_items:
        with open(fn, 'w') as fp:
            type_ = 'category' if fn.endswith('category.json') else 'video'
            data = reorder_dict(type_, data)
            json.dump(
                data,
                fp,
                indent=2,
                sort_keys=False,
                default=json_convert,
                separators=(',', ': ')
            )
