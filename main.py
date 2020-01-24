import argparse
import datetime
import os
import sys

from github import Github

from business_day_calculator import BusinessDayCalculator
from user_statistics import UserStatistics


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
    help='The first day inclusive of analysis. ex: 16-Jul-2020',
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

  statistics = get_pr_info(repo, total_business_days, start, end, verbose)
  for k in sorted(statistics.keys()):
    print(f"{k}: {statistics[k]}")
  print(f"Total business days {total_business_days}")


def get_pr_info(repo, total_business_days, start, end, verbose):
  statistics = {}
  comments = []
  reviews = []
  prs = []
  print("gathering repo data")
  for pr in repo.get_pulls(state='all', sort='created_at', direction='desc'):
    created_at = pr.created_at.date()
    if created_at < start:
      break
    if not (start <= created_at <= end):
      continue
    prs.append(pr)
    for rc in pr.get_review_comments():
      comments.append(rc)
    for c in pr.get_comments():
      comments.append(c)
    for r in pr.get_reviews():
      reviews.append(r)
  print("processing prs")
  for pr in prs:
    default = UserStatistics(total_business_days, verbose)
    user_statistics = statistics.get(pr.user.name, default)
    user_statistics.add_pr(pr)
    statistics[pr.user.name] = user_statistics

  print("processing comments")
  for comment in comments:
    default = UserStatistics(total_business_days, verbose)
    user_statistics = statistics.get(comment.user.name, default)
    user_statistics.add_comment(comment)
    statistics[comment.user.name] = user_statistics

  print("processing reviews")
  for review in reviews:
    default = UserStatistics(total_business_days, verbose)
    user_statistics = statistics.get(review.user.name, default)
    user_statistics.add_review(review)
    statistics[review.user.name] = user_statistics

  return statistics


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
