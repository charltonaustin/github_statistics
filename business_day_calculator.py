import datetime


class BusinessDayCalculator:
  def __init__(self, start: datetime.date, end: datetime.date):
    self.end = end
    self.start = start
    self._business_days = None

  def _calculate(self):
    total_business_days = 0
    number_of_days = self.end - self.start
    for i in range(1, number_of_days.days + 1):
      weekday = (self.start - datetime.timedelta(days=i)).weekday()
      if not (weekday == 6 or weekday == 5):
        total_business_days += 1
    self._business_days = total_business_days

  def business_days(self):
    if self._business_days is None:
      self._calculate()
    return self._business_days
