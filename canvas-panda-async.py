# parse args
from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import requests
import grequests
import logging
import os
import sys
import re
import csv
import datetime
import iso8601
from pytz import timezone

TIMEZONE = timezone('Australia/Melbourne')


def map_canvas(url, parse_func, collector, page=1):
  response = requests.get(url, params={'page': page}, headers=HEADERS)

  submissions = response.json()
  if len(submissions) > 0:
    collector.extend([parse_func(submission) for submission in submissions])
    map_canvas(url, parse_func, collector, page + 1)

def parse_submissions(submission):
    # Original code to covert '%Y-%m-%dT%H:%M:%SZ' to ''%-m/%-d/%Y %-H:%-M:%-S' (no timezone reasoning)
    submitted_at = datetime.datetime.strptime(submission['submitted_at'], '%Y-%m-%dT%H:%M:%SZ').strftime(
        '%-m/%-d/%Y %-H:%-M:%-S') if submission['submitted_at'] is not None else None

    submitted_at = iso8601.parse_date(submission['submitted_at']).astimezone(TIMEZONE) if submission[
                                                                                              'submitted_at'] is not None else None
    return {'submitted_at': submitted_at, 'user_id': submission['user_id']}

def parse_uni(resp, **kwargs):
  user = resp.json()
  uni = pattern.match(user['email']).group(1)
  name = user['name']
  user_id = user['id']
  id_uni_name_map[user_id] = {'uni': uni, 'name': name}
  logger.info('Cross referenced uni %s' % uni)




if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Grabs submission times for an assignment in a course.')
    parser.add_argument('canvas_api_key', metavar='K', type=str,
                        help='Canvas API Key obtained from "settings"')
    parser.add_argument('course_id', metavar='C', type=int,
                        help='Course ID. e.g. xxxx in https://<canvas_url>/courses/xxxx/assignments/yyyy')
    parser.add_argument('assignment_id', metavar='A', type=int,
                        help='Course ID. e.g. yyyy in https://<canvas_url>/courses/xxxx/assignments/yyyy')
    parser.add_argument('-u', '--canvas_url', type=str,
                        help='Canvas base URL (default: courseworks2.columbia.edu)')

    args = parser.parse_args()

    if not args.canvas_url:
        args.canvas_url = 'rmit.instructure.com'

    # Logging configuration
    logger = logging.getLogger('root')
    program = os.path.basename(sys.argv[0])
    logger = logging.getLogger(program)
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
    logging.root.setLevel(level=logging.INFO)
    logger.info("running %s" % ' '.join(sys.argv))

    # Construct headers
    HEADERS = {'Authorization': 'Bearer ' + args.canvas_api_key}
    URL_BASE = 'https://' + args.canvas_url + '/api/v1/'

    # Grab submissions
    logger.info('Grabbing submission times')
    url_submissions = URL_BASE + \
                      'courses/%d/assignments/%d/submissions' % (
                          args.course_id, args.assignment_id)
    submission_times = []
    map_canvas(url_submissions, parse_submissions, submission_times)

    # Cross-reference unis
    pattern = re.compile('(.*)@')
    id_uni_name_map = {}

    logger.info('Cross referencing user_ids to unis')
    url_users = [URL_BASE + 'courses/%d/users/%d' % (args.course_id, submission_time['user_id']) for submission_time in submission_times]
    reqs = (grequests.get(url_user, params={'include': 'email'}, headers=HEADERS, hooks={'response': parse_uni}) for url_user in url_users)
    resps = grequests.map(reqs)

    logger.info('Writing CSV')
    with open('submissions_%s_%s.csv' % (args.course_id, args.assignment_id), 'w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=submission_times[0].keys())

        writer.writeheader()
        for submission_time in submission_times:
            writer.writerow(submission_time)
