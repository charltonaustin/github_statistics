import datetime
import os
import pickle
import shutil
from os.path import join, isfile

PATH = os.environ['HOME'] + '/Library/Caches/github_statistics'


class Cache:
  def __init__(self, repo):
    self.repo = repo

  def get_cache_dates(self):
    try:
      with open(f"{PATH}/{self.repo}/cache_dates", 'r') as f:
        cache_date_start, cache_date_end = f.readline().strip().split()
        cache_date_start = datetime.datetime.strptime(cache_date_start, '%Y-%m-%d').date()
        cache_date_end = datetime.datetime.strptime(cache_date_end, '%Y-%m-%d').date()
        return cache_date_start, cache_date_end
    except FileNotFoundError:
      return None, None

  @staticmethod
  def pull_from_cache(start, end):
    prs = []
    comments = []
    reviews = []
    onlyfiles = [join(PATH, f) for f in os.listdir(PATH) if isfile(join(PATH, f))]
    for file_name in onlyfiles:
      with open(file_name, "rb") as file_:
        if file_name.find("pull_request_") >= 0:
          pr = pickle.load(file_, encoding="UTF-8")
          if start <= pr.created_at.date() <= end:
            prs.append(pr)
        if file_name.find("comment_") >= 0:
          comment = pickle.load(file_, encoding="UTF-8")
          if start <= comment.created_at.date() <= end:
            comments.append(comment)
        if file_name.find("review_") >= 0:
          review = pickle.load(file_, encoding="UTF-8")
          if start <= review.submitted_at.date() <= end:
            reviews.append(review)
    return prs, comments, reviews

  def write_cache(self, comments, prs, reviews, start, end):
    if start == end:
      print("not writing cache since start and end date are the same")
      return

    if end == datetime.datetime.today().date():
      end = (end - datetime.timedelta(days=1))
    print(f"writing cache from {start} to {end}")
    for pr in prs:
      name = pr.user.name  # this is to force lazy evaluation
      with open(f"{PATH}/{self.repo}/pull_request_{pr.number}", "w+b") as pr_file:
        pickle.dump(pr, pr_file)

    for c in comments:
      name = c.user.name  # this is to force lazy evaluation
      with open(f"{PATH}/{self.repo}/comment_{c.id}", "w+b") as c_file:
        pickle.dump(c, c_file)

    for r in reviews:
      name = r.user.name  # this is to force lazy evaluation
      with open(f"{PATH}/{self.repo}/reviews_{r.id}", "w+b") as c_file:
        pickle.dump(r, c_file)

    with open(f"{PATH}/{self.repo}/cache_dates", 'w+') as f:
      f.write(f"{start} {end}")

    return start, end

  def delete_cache(self):
    shutil.rmtree(f"{PATH}/{self.repo}")

  def initialize_folder(self):
    if not os.path.isdir(f"{PATH}"):
      os.mkdir(f"{PATH}")
    if not os.path.isdir(f"{PATH}/{self.repo}"):
      os.mkdir(f"{PATH}/{self.repo}")
