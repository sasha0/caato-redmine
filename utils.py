# -*- coding: utf-8 -*-

import csv
import datetime
import json
import sys

import requests
from models import session, SyncLog
import configuration

REDMINE_HOSTNAME = getattr(configuration, 'REDMINE_HOSTNAME', None)
REDMINE_API_KEY = getattr(configuration, 'REDMINE_API_KEY', None)
REDMINE_DEFAULT_ACTIVITY = getattr(configuration, 'REDMINE_DEFAULT_ACTIVITY', 'Development')
MERGE_TASKS = getattr(configuration, 'MERGE_TASKS', True)


def _get_data(endpoint):
    """Performing GET request to Redmine API."""
    
    headers = {'X-Redmine-API-Key': REDMINE_API_KEY}
    r = requests.get(REDMINE_HOSTNAME + endpoint, headers=headers)    
    return r


def _task_exists(task_id):
    """
    Checking if corresponding task exists in Redmine, 
    before performing synchronization.
    """
    
    r = _get_data('/issues/%s.json' % task_id)
    if r.status_code == 200:
        return True
    return False


def _task_synced(task_id, start_datetime, end_datetime, duration):
    """Checking if current fact was synchronized per logs."""

    if session.query(SyncLog).filter_by(task_id=task_id,
                                        start_datetime=start_datetime,
                                        end_datetime=end_datetime,
                                        duration=duration).count() == 0:
        return False
    return True


def _get_time_entry_activities():
    """Fetching Redmine activities."""
    
    return _get_data('/enumerations/time_entry_activities.json').json()


def _get_time_entry_activity():
    """Determining default activity ID."""
    
    activities = _get_time_entry_activities()['time_entry_activities']
    for a in activities:
        if a['name'] == REDMINE_DEFAULT_ACTIVITY:
            return a['id']
    return


def _log_sync(task_id, start_datetime, end_datetime, duration):
    """Adding entry to synchronization log model."""
    
    entry = SyncLog(task_id=task_id, start_datetime=start_datetime,
                    end_datetime=end_datetime, duration=duration)
    session.add(entry)
    session.commit()


def _sync_task(task_id, start_datetime, end_datetime, duration, activity_id):
    """Synchronizing fact by adding new time entry though Redmine API."""
    
    headers = {'X-Redmine-API-Key': REDMINE_API_KEY, 'content-type': 'application/json'}
    data = {'time_entry': {
                'issue_id': int(task_id),
                'spent_on': start_datetime.date().isoformat(),
                'hours': duration,
                'activity_id': activity_id,
                }
            }
    if not _task_synced(task_id, start_datetime, end_datetime, duration):
        sys.stdout.write('Logging task %s.\n' % task_id)
        r = requests.post(REDMINE_HOSTNAME + '/time_entries.json', headers=headers, data=json.dumps(data))
        if r.status_code == 201:
            _log_sync(task_id, start_datetime, end_datetime, duration)


def synchronize_tasks(time_entries):
    """Performing synchronization for given bunch of facts."""
    activity_id = _get_time_entry_activity()
    for time_entry in time_entries:
        task_id, start_datetime, end_datetime, duration = _extract_data(time_entry)
        if _task_exists(task_id):
            _sync_task(task_id, start_datetime, end_datetime, duration, activity_id)
        else:
            sys.stderr.write('Task %s does not exist in Redmine.\n' % task_id)


def _extract_data(time_entry):
    task_id = int(time_entry[1])
    start_datetime = datetime.datetime.strptime(time_entry[2], '%d.%m.%y, %H:%M')
    end_datetime = datetime.datetime.strptime(time_entry[3], '%d.%m.%y, %H:%M')
    duration = float(time_entry[4].replace(',', '.'))
    return task_id, start_datetime, end_datetime, duration


def check_tasks(time_entries):
    """Checking if given facts are already synchronized."""
    
    for time_entry in time_entries:
        task_id, start_datetime, end_datetime, duration = _extract_data(time_entry)
        if not _task_synced(task_id, start_datetime, end_datetime, duration):
            sys.stdout.write('Task %s (%s, %.2fh) was not synchronized.\n' % (task_id, start_datetime.date(), duration))
        else:
            sys.stdout.write('Task %s (%s, %.2fh) was synchronized.\n' % (task_id, start_datetime.date(), duration))


def get_time_entries(path_to_file):
    with open(path_to_file, 'rb') as imported_file:
        csv_file = csv.reader(imported_file, delimiter=';')
        for idx, row in enumerate(csv_file):
            if idx == 0:
                continue
            yield row
