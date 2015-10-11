# -*- coding: utf-8 -*-
from optparse import OptionParser
import os
import sys
from utils import check_tasks, synchronize_tasks, get_time_entries


parser = OptionParser(add_help_option=False)
parser.add_option('-s', '--synchronize', dest='synchronize', action='store_true')
parser.add_option('-p', '--path-to-file', dest='path_to_file', action='store', type='string')
(options, args) = parser.parse_args()

facts = []

path_to_file = getattr(options, 'path_to_file', None)

if not getattr(options, 'path_to_file', None):
    sys.stderr.write('Please provide path to imported file.\n')
    sys.stderr.write('python caato_redmine.py -p PATH_TO_FILE\n')

if path_to_file and not os.path.exists(path_to_file):
    sys.stderr.write('Imported file %s does not exist.\n' % path_to_file)
    path_to_file = None

if path_to_file:
    time_entries = get_time_entries(path_to_file)
    if time_entries:
        # depends on option, synchronizing aggregated tasks data or just displaying results
        if getattr(options, 'synchronize', None):
            synchronize_tasks(time_entries)
        else:
            check_tasks(time_entries)
    else:
        sys.stdout.write('No activity found.\n')
