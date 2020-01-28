import datetime
import os
import pickle
from os.path import isfile, join

PATH = os.environ['HOME'] + '/Library/Caches/github_statistics'


class GetPRInfo:
  def __init__(self, repo, start, end):
    self.repo = repo
    self.start = start
    self.end = end
    self.cached_date_start = None
    self.cached_date_end = None

  @staticmethod
  def write_cache_date(start, end):
    with open(f"{PATH}/cache_dates", 'w+') as f:
      f.write(f"{start} {end}")

  def get_cache_dates(self):
    try:
      with open(f"{PATH}/cache_dates", 'r') as f:
        cache_date_start, cache_date_end = f.readline().strip().split()
        cache_date_start = datetime.datetime.strptime(cache_date_start, '%Y-%m-%d').date()
        cache_date_end = datetime.datetime.strptime(cache_date_end, '%Y-%m-%d').date()
        self.cached_date_start = cache_date_start
        self.cached_date_end = cache_date_end
    except FileNotFoundError:
      pass

  def get_values(self, start, end):
    prs = []
    comments = []
    reviews = []
    for pr in self.repo.get_pulls(state='all', sort='created_at', direction='desc'):
      created_at = pr.created_at.date()
      if created_at < start:
        break
      if not (start <= created_at <= end):
        continue
      prs.append(pr)
      for rc in pr.get_review_comments():
        if not (start <= rc.created_at.date() <= end):
          continue
        comments.append(rc)
      for c in pr.get_comments():
        if not (start <= c.created_at.date() <= end):
          continue
        comments.append(c)
      for r in pr.get_reviews():
        if not (start <= r.submitted_at.date() <= end):
          continue
        reviews.append(r)
    return prs, comments, reviews

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

  def get_pr_info(self):
    print("gathering repo data")
    self.get_cache_dates()
    if self.date_out_of_cache():
      print("not in cache pulling from api")
      prs, comments, reviews = self.get_values(self.start, self.end)
      self.write_cache(comments, prs, reviews, self.start, self.end)
      return prs, comments, reviews
    if self.end > self.cached_date_end:
      print("partially in cache")
      prs, comments, reviews = self.get_values(self.cached_date_end, self.end)
      c_prs, c_comments, c_reviews = self.pull_from_cache(self.start, self.end)
      self.write_cache(comments, prs, reviews, self.cached_date_start, self.end)
      prs.extend(c_prs)
      prs = sorted(prs, key=lambda p: p.created_at)
      comments.extend(c_comments)
      comments = sorted(comments, key=lambda c: c.created_at)
      reviews.extend(c_reviews)
      reviews = sorted(reviews, key=lambda r: r.created_at)
      return prs, comments, reviews
    if self.date_in_cache():
      print("pulling from cache")
      return self.pull_from_cache(self.start, self.end)

  def date_in_cache(self):
    return self.end <= self.cached_date_end and self.start >= self.cached_date_start

  def date_out_of_cache(self):
    cached_end_is_none = self.cached_date_end is None
    cache_start_is_none = self.cached_date_start is None
    return cached_end_is_none or cache_start_is_none or self.start < self.cached_date_start

  def write_cache(self, comments, prs, reviews, start, end):
    print(f"writing cache from {start} to {end}")
    for pr in prs:
      name = pr.user.name  # this is to force lazy evaluation
      with open(f"{PATH}/pull_request_{pr.number}", "w+b") as pr_file:
        pickle.dump(pr, pr_file)
    for c in comments:
      name = c.user.name  # this is to force lazy evaluation
      with open(f"{PATH}/comment_{c.id}", "w+b") as c_file:
        pickle.dump(c, c_file)
    for r in reviews:
      name = r.user.name  # this is to force lazy evaluation
      with open(f"{PATH}/reviews_{r.id}", "w+b") as c_file:
        pickle.dump(r, c_file)
    self.cached_date_start = start
    self.cached_date_end = end
    self.write_cache_date(start, end)
