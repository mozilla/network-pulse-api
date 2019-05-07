from datetime import date

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class YearValidator:
    message = _('The year must be between %(min_year)s and %(max_year)s.')
    code = 'year_value'

    def __init__(self, min_offset=10, max_offset=10):
        self.min_offset = min_offset
        self.max_offset = max_offset

    def __call__(self, value):
        current_year = date.today().year
        min_year = current_year - self.min_offset
        max_year = current_year + self.max_offset

        if value < min_year or value > max_year:
            raise ValidationError(
                self.message,
                code=self.code,
                params={'min_year': min_year, 'max_year': max_year}
            )

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.min_offset == other.min_offset and
            self.max_offset == other.max_offset and
            self.message == other.message and
            self.code == other.code
        )
