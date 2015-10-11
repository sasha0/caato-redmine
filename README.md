# Caato-redmine

Caato-redmine is a simple command-line script, which helps to synchronize tracked time from [Caato Time Tracker](http://www.caato.de/en/products/time-tracker-for-mac.html) to [Redmine](http://www.redmine.org/) project management application.

# Configuration

`REDMINE_HOSTNAME` — URL of your Redmine instance

`REDMINE_API_KEY` — your personal API key, available in **My account** section

`REDMINE_DEFAULT_ACTIVITY` - title of activity, you'd like to use for synchronization.

# Usage

Provide path to your exported CSV, so you can view time entries:

```bash
python caato_redmine.py -p /path/to/your/file.csv
```

Or to synchronize them all:

```bash
python caato_redmine.py -p /path/to/your/file.csv -s
```

# Requirements
* [SQLAlchemy](https://github.com/zzzeek/sqlalchemy)
* [requests](https://github.com/kennethreitz/requests)
