import pprint

from comment_info import CommentInfo, ReviewInfo
from pr_info import PRInfo


class UserStatistics:
  def __init__(self, number_of_business_days, verbose):
    self.verbose = verbose
    self.number_of_business_days = number_of_business_days
    self.number_of_review_comments = 0
    self.comments = []
    self.number_of_prs = 0
    self.prs = []
    self.number_of_reviews = 0
    self.reviews = []

  def add_pr(self, pr):
    self.prs.append(PRInfo(pr.created_at, pr.html_url, pr.closed_at))
    self.number_of_prs += 1

  def add_comment(self, comment):
    self.number_of_review_comments += 1
    self.comments.append(CommentInfo(comment.html_url, comment.created_at))

  def add_review(self, review):
    self.number_of_reviews += 1
    self.reviews.append(ReviewInfo(review.html_url, review.submitted_at, review.state))

  def __str__(self):
    return_string = f"number of comments: {self.number_of_review_comments}, "
    return_string += f"number of reviews: {self.number_of_reviews}, "
    return_string += f"number of prs: {self.number_of_prs}, "
    days = self.number_of_business_days
    if days == 0:
      days += 1
    return_string += f"pr/days: {round(self.number_of_prs / days, 2)}, "
    if self.verbose >= 1:
      if self.comments:
        return_string += "\n" + pprint.pformat(self.comments)
      if self.prs:
        return_string += "\n" + pprint.pformat(self.prs)
      if self.reviews:
        return_string += "\n" + pprint.pformat(self.reviews)
    return return_string

  def __repr__(self):
    return f"{self.__str__()}"
