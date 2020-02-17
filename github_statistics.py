import argparse
import datetime
import os
import sys

from github import Github

from business_day_calculator import BusinessDayCalculator
from get_pr_info import GetPRInfo
from processors import PRInfoProcessor, ReviewsInfoProcessor, CommentsInfoProcessor


def main():
  token = os.getenv('GITHUB_TOKEN')
  if not token:
    print("missing GITHUB_TOKEN please set environment variable with personal token "
          "https://github.com/settings/tokens")
    return
  g = Github(token)

  parser = argparse.ArgumentParser(description='Github statistics calculator',
                                   usage='main.py -s 16-Jul-2020 -e 20-Jul-2020')
  parser.add_argument(
    '-s',
    '--start',
    dest='start_date',
    metavar='Start date for analysis',
    type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d').date(),
    nargs=1,
    help='The first day inclusive of analysis. ex: 16-Jul-2020',
    default=[(datetime.datetime.today() - datetime.timedelta(days=30)).date()]
  )
  parser.add_argument(
    '-e',
    '--end',
    dest='end_date',
    metavar='End date for analysis',
    type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d').date(),
    nargs=1,
    help='The last day inclusive of analysis. ex: 16-Jul-2020',
    default=[datetime.datetime.today().date()]
  )
  parser.add_argument('--verbose', '-v', action='count', default=0)

  parser.add_argument(
    '-r',
    '--repo_name',
    dest='repo_name',
    metavar='Name of repo to find',
    type=str,
    nargs=1,
    help='Name of repo you would like to analyze',
    default=["tuesday-strategies"]
  )
  args = parser.parse_args()
  start = args.start_date[0]
  end = args.end_date[0]
  name = args.repo_name[0]
  verbose = args.verbose
  print("start: {}".format(start))
  print("end: {}".format(end))
  print("repo name: {}".format(name))
  total_business_days = BusinessDayCalculator(start, end).business_days()
  repo = get_repo(g, name)
  prs, comments, reviews = GetPRInfo(repo, start, end).get_pr_info()
  statistics = {}
  statistics = PRInfoProcessor(statistics, prs, total_business_days, verbose).process()
  statistics = CommentsInfoProcessor(statistics, comments, total_business_days, verbose).process()
  statistics = ReviewsInfoProcessor(statistics, reviews, total_business_days, verbose).process()
  for k in sorted(statistics.keys()):
    print(f"{k}: {statistics[k]}")
  print(f"Total business days {total_business_days}")


def get_repo(g, repo_name):
  print("finding repo")
  names = []
  for repo in g.get_user().get_repos():
    names.append(repo.name)
    if repo.name == repo_name:
      return repo
  print(f"Invalid repo name: {repo_name}")
  print(f"Please select repo name from: {names}")
  sys.exit(1)


if __name__ == "__main__":
  main()
