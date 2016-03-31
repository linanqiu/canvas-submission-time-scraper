# parse args

import argparse
import requests
import logging
import os
import sys
import re
import csv
import datetime

parser = argparse.ArgumentParser(
    description='Grabs submission times for an assignment in a course.')
parser.add_argument('canvas_api_key', metavar='K', type=str,
                    help='Canvas API Key obtained from "settings"')
parser.add_argument('course_id', metavar='C', type=int,
                    help='Course ID. e.g. xxxx in https://courseworks2.columbia.edu/courses/xxxx/assignments/yyyy')
parser.add_argument('assignment_id', metavar='A', type=int,
                    help='Course ID. e.g. yyyy in https://courseworks2.columbia.edu/courses/xxxx/assignments/yyyy')

args = parser.parse_args()

# logging

logger = logging.getLogger('root')

program = os.path.basename(sys.argv[0])
logger = logging.getLogger(program)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
logging.root.setLevel(level=logging.INFO)
logger.info("running %s" % ' '.join(sys.argv))

# construct headers

HEADERS = {'Authorization': 'Bearer ' + args.canvas_api_key}

URL_BASE = 'https://courseworks2.columbia.edu/api/v1/'

# map functions


def map_canvas_single(url, parse_func, params):
  response = requests.get(url, params=params, headers=HEADERS)
  json = response.json()
  return parse_func(json)


def map_canvas(url, parse_func, collector, page=1):
  response = requests.get(url, params={'page': page}, headers=HEADERS)

  submissions = response.json()
  if len(submissions) > 0:
    collector.extend([parse_func(submission) for submission in submissions])
    map_canvas(url, parse_func, collector, page + 1)

# grab submissions

url_submissions = URL_BASE + \
    'courses/%d/assignments/%d/submissions' % (
        args.course_id, args.assignment_id)


def parse_submissions(submission):
  submitted_at = datetime.datetime.strptime(submission['submitted_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%-m/%-d/%Y %-H:%-M:%-S') if submission['submitted_at'] is not None else None
  return {'submitted_at': submitted_at, 'user_id': submission['user_id']}

submission_times = []

logger.info('Grabbing submission times')
map_canvas(url_submissions, parse_submissions, submission_times)

# cross reference unis

pattern = re.compile('(.*)@')


def parse_uni(user):
  uni = pattern.match(user['email']).group(1)
  name = user['name']
  return {'uni': uni, 'name': name}

logger.info('Cross referencing user_ids to unis')

for submission_time in submission_times:
  logger.info('Grabbing user_id %s' % submission_time['user_id'])
  user_id = submission_time['user_id']
  url_user = URL_BASE + 'courses/%d/users/%d' % (args.course_id, user_id)
  user = map_canvas_single(url_user, parse_uni, params={'include': 'email'})
  submission_time['uni'] = user['uni']
  submission_time['name'] = user['name']

logger.info('Writing CSV')

with open('submissions_%s_%s.csv' % (args.course_id, args.assignment_id), 'w') as csv_file:
  writer = csv.DictWriter(csv_file, fieldnames=submission_times[0].keys())

  writer.writeheader()
  for submission_time in submission_times:
    writer.writerow(submission_time)
