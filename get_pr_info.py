class GetPRInfo:
  def __init__(self, repo, start, end, cache):
    self.repo = repo
    self.start = start
    self.end = end
    self.cache = cache

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

  def get_pr_info(self):
    print("gathering repo data")
    cached_date_start, cached_date_end = self.cache.get_cache_dates()
    if self.date_out_of_cache(cached_date_end, cached_date_start):
      print("not in cache pulling from api")
      prs, comments, reviews = self.get_values(self.start, self.end)
      self.cache.write_cache(comments, prs, reviews, self.start, self.end)
      return prs, comments, reviews
    if self.end > cached_date_end:
      print("partially in cache")
      prs, comments, reviews = self.get_values(cached_date_end, self.end)
      c_prs, c_comments, c_reviews = self.cache.pull_from_cache(self.start, self.end)
      self.cache.write_cache(comments, prs, reviews, cached_date_start, self.end)
      prs.extend(c_prs)
      prs = sorted(prs, key=lambda p: p.created_at)
      comments.extend(c_comments)
      comments = sorted(comments, key=lambda c: c.created_at)
      reviews.extend(c_reviews)
      reviews = sorted(reviews, key=lambda r: r.submitted_at)
      return prs, comments, reviews
    if self.date_in_cache(cached_date_end, cached_date_start):
      print("pulling from cache")
      return self.cache.pull_from_cache(self.start, self.end)

  def date_in_cache(self, cached_date_end, cached_date_start):
    return self.end <= cached_date_end and self.start >= cached_date_start

  def date_out_of_cache(self, cached_date_end, cached_date_start):
    return cached_date_end is None or cached_date_start is None or self.start < cached_date_start
