#!/usr/bin/env python
import argparse
import datetime
import os
import sys

from github import Github

from business_day_calculator import BusinessDayCalculator
from cache import Cache
from get_pr_info import GetPRInfo
from processors import PRInfoProcessor, ReviewsInfoProcessor, CommentsInfoProcessor


def main():
  token = os.getenv("GITHUB_TOKEN")
  if not token:
    print("missing GITHUB_TOKEN please set environment variable with personal token "
          "https://github.com/settings/tokens")
    return
  g = Github(token)

  parser = argparse.ArgumentParser(description="Github statistics calculator",
                                   usage="main.py -s 16-Jul-2020 -e 20-Jul-2020")
  start_help = "The first day inclusive of analysis. " + \
               "Default is 30 days ago. Must be in Y-m-d. ex: 16-Jul-2020"
  parser.add_argument(
    "-s",
    "--start",
    dest="start_date",
    type=lambda s: datetime.datetime.strptime(s, "%Y-%m-%d").date(),
    nargs=1,
    help=start_help,
    default=[(datetime.datetime.today() - datetime.timedelta(days=30)).date()]
  )
  end_help = "The last day inclusive of analysis. " + \
             "Default is today. Must be in Y-m-d. ex: 16-Jul-2020"
  parser.add_argument(
    "-e",
    "--end",
    dest="end_date",
    type=lambda s: datetime.datetime.strptime(s, "%Y-%m-%d").date(),
    nargs=1,
    help=end_help,
    default=[datetime.datetime.today().date()]
  )

  parser.add_argument(
    "-r",
    "--repo_name",
    dest="repo_name",
    type=str,
    nargs=1,
    help="Name of repo you would like to analyze. Default is tuesday-strategies",
    default=["tuesday-strategies"]
  )

  parser.add_argument(
    "-d",
    "--delete_cache",
    action="count",
    default=0,
  )

  parser.add_argument(
    "--verbose",
    "-v",
    action="count",
    help="Shows urls to reviews, comments, and pr reviews",
    default=0
  )

  args = parser.parse_args()
  name = args.repo_name[0]
  cache = Cache(name)
  start = args.start_date[0]
  end = args.end_date[0]
  verbose = args.verbose
  print("start: {}".format(start))
  print("end: {}".format(end))
  print("repo name: {}".format(name))
  repo = get_repo(g, name)
  cache.initialize_folder()
  if args.delete_cache:
    print("deleting cache")
    cache.delete_cache()
    return

  total_business_days = BusinessDayCalculator(start, end).business_days()
  prs, comments, reviews = GetPRInfo(repo, start, end, cache).get_pr_info()
  statistics = {}
  statistics = PRInfoProcessor(statistics, prs, total_business_days, verbose).process()
  statistics = CommentsInfoProcessor(statistics, comments, total_business_days, verbose).process()
  statistics = ReviewsInfoProcessor(statistics, reviews, total_business_days, verbose).process()
  for k in sorted(statistics.keys()):
    print(f"{k}: {statistics[k]}")
  print(f"Total business days {total_business_days}")


def get_repo(g, repo_name):
  print("finding repos")
  names = []
  for repo in g.get_user().get_repos():
    names.append(repo.name)
    if repo.name == repo_name:
      return repo
  print(f"******\nInvalid repo name: {repo_name}\n******\n")
  print(f"Please select repo name from:")
  for name in names:
    print(name)
  sys.exit(1)


if __name__ == "__main__":
  main()
