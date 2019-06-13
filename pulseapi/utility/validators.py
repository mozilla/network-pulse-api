from datetime import date

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class YearValidator:
    """Validates that a year is within a specified range of years

    Keyword arguments:
    min_year -- the lower limit of the year range (default 2000)
    max_offset -- the number of years to offset from the current year to
    determine the upper limit of the year range (default 10)
    """
    message = _('The year must be between %(min_year)s and %(max_year)s.')
    code = 'year_value'

    def __init__(self, min_year=2000, max_offset=10):
        current_year = date.today().year

        if min_year > current_year:
            raise ValueError(f'The min_year passed ({min_year}) cannot be after the current year ({current_year})')

        self.min_year = min_year
        self.max_offset = max_offset

    def __call__(self, value):
        current_year = date.today().year
        max_year = current_year + self.max_offset

        if value < self.min_year or value > max_year:
            raise ValidationError(
                self.message,
                code=self.code,
                params={'min_year': self.min_year, 'max_year': max_year}
            )

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.min_year == other.min_year and
            self.max_offset == other.max_offset and
            self.message == other.message and
            self.code == other.code
        )
