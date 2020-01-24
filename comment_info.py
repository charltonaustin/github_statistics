class CommentInfo:
  def __init__(self, url, created_at):
    self.url = url
    self.created_at = created_at

  def __str__(self):
    return_string = f"url: {self.url}, "
    if self.created_at:
      return_string += f"created_at: {self.created_at.date()}, "
    return return_string

  def __repr__(self):
    return f"({self.__str__()})"


class ReviewInfo:
  def __init__(self, url, submitted_at, status):
    self.status = status
    self.url = url
    self.submitted_at = submitted_at

  def __str__(self):
    return_string = f"url: {self.url}, "
    if self.submitted_at:
      return_string += f"submitted_at: {self.submitted_at.date()}, "
    if self.status:
      return_string += f"status: {self.status}, "
    return return_string

  def __repr__(self):
    return f"({self.__str__()})"