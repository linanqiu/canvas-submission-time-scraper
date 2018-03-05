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

# default values
TIMEZONE = 'Australia/Melbourne'
CANVAS_URL = 'rmit.instructure.com'

# Process URL, parse doc with function parse_func and collect data in collector
def map_canvas(url, parse_func, collector, page=1):
  web_response = requests.get(url, params={'page': page}, headers=HEADERS)

  web_response_json = web_response.json() # transform response into json-encoded content
  logging.info("Processing page no. %d" % page)
  if len(web_response_json) > 0 and page < 4:
    collector.extend([parse_func(submission) for submission in web_response_json])
    map_canvas(url, parse_func, collector, page + 1)


def parse_submissions(response_json):
    # Original code to covert '%Y-%m-%dT%H:%M:%SZ' to ''%-m/%-d/%Y %-H:%-M:%-S' (no timezone reasoning)
    submitted_at = datetime.datetime.strptime(response_json['submitted_at'], '%Y-%m-%dT%H:%M:%SZ').strftime(
        '%-m/%-d/%Y %-H:%-M:%-S') if response_json['submitted_at'] is not None else None

    # New version using iso8601 (https://en.wikipedia.org/wiki/ISO_8601) time standard and timezones
    submitted_at = iso8601.parse_date(response_json['submitted_at']).astimezone(timezone(TIMEZONE)) if response_json[
                                                                                              'submitted_at'] is not None else None
    return {'user_id': response_json['user_id'], 'submitted_at': submitted_at}



def parse_uni(resp, **kwargs):
  user = resp.json()
  # print(user)
  uni = pattern.match(user['email']).group(1)
  name = user['name']
  user_id = user['id']
  id_uni_name_map[user_id] = {'uni': uni, 'name': name}
  logger.info('Cross referenced uni %s' % uni)









if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Grabs submission times for an assignment in a course.')
    parser.add_argument(
        'canvas_api_key',
        # metavar='K',
        type=str,
        help='Canvas API Key obtained from "settings"'
    )
    parser.add_argument(
        'course_id',
        # metavar='C',
        type=int,
        help='Course ID. e.g. xxxx in https://<canvas_url>/courses/xxxx/assignments/yyyy'
    )
    parser.add_argument(
        'assignment_id',
        # metavar='A',
        type=int,
        help='Course ID. e.g. yyyy in https://<canvas_url>/courses/xxxx/assignments/yyyy'
    )
    parser.add_argument(
        '-u',
        '--canvas_url',
        type=str,
        default = CANVAS_URL,
        help='Canvas base URL (default: %(default)s)'
    )
    parser.add_argument(
        '--timezone',
        type=str,
        default = TIMEZONE,
        help='Timezone to used (default: %(default)s) (see http://en.wikipedia.org/wiki/List_of_tz_database_time_zones)'
    )
    args = parser.parse_args()

    TIMEZONE = args.timezone

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

    # TOOD: this does seem to go over all student and print a message but is unrelated to the submission time extraction
    # Cross-reference unis
    # pattern = re.compile('(.*)@')
    # id_uni_name_map = {}

    # logger.info('Cross referencing user_ids to unis')
    #
    #  url_users = [URL_BASE + 'courses/%d/users/%d' % (args.course_id, submission_time['user_id']) for submission_time in submission_times]
    # reqs = (grequests.get(url_user, params={'include': 'email'}, headers=HEADERS, hooks={'response': parse_uni}) for url_user in url_users)
    # resps = grequests.map(reqs)

    logger.info('Writing CSV')
    with open('submissions_%s_%s.csv' % (args.course_id, args.assignment_id), 'w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=submission_times[0].keys())

        writer.writeheader()
        for submission_time in submission_times:
            writer.writerow(submission_time)
