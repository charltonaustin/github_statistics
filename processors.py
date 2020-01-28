from user_statistics import UserStatistics


class PRInfoProcessor:
  def __init__(self, statistics, prs, total_business_days, verbose):
    self.verbose = verbose
    self.total_business_days = total_business_days
    self.prs = prs
    self.statistics = statistics

  def process(self):
    statistics = self.statistics
    print("processing prs")
    for pr in self.prs:
      default = UserStatistics(self.total_business_days, self.verbose)
      user_statistics = statistics.get(pr.user.name, default)
      user_statistics.add_pr(pr)
      statistics[pr.user.name] = user_statistics

    return statistics


class ReviewsInfoProcessor:
  def __init__(self, statistics, reviews, total_business_days, verbose):
    self.verbose = verbose
    self.total_business_days = total_business_days
    self.reviews = reviews
    self.statistics = statistics

  def process(self):
    statistics = self.statistics
    print("processing reviews")
    for review in self.reviews:
      default = UserStatistics(self.total_business_days, self.verbose)
      user_statistics = statistics.get(review.user.name, default)
      user_statistics.add_review(review)
      statistics[review.user.name] = user_statistics

    return statistics


class CommentsInfoProcessor:
  def __init__(self, statistics, comments, total_business_days, verbose):
    self.verbose = verbose
    self.total_business_days = total_business_days
    self.comments = comments
    self.statistics = statistics

  def process(self):
    statistics = self.statistics
    print("processing comments")
    for comment in self.comments:
      default = UserStatistics(self.total_business_days, self.verbose)
      user_statistics = statistics.get(comment.user.name, default)
      user_statistics.add_comment(comment)
      statistics[comment.user.name] = user_statistics

    return statistics
