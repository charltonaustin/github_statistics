class PRInfo:
  def __init__(self, created_at, url, closed_at):
    self.url = url
    self.closed_at = closed_at
    self.created_at = created_at

  def __str__(self):
    return_string = f"url: {self.url} "
    if self.created_at:
      return_string += f"created_at: {self.created_at.date()}, "
    if self.closed_at:
      return_string += f"close_at: {self.closed_at.date()}, "
    return return_string

  def __repr__(self):
    return f"({self.__str__()})"
