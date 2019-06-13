from datetime import date
from django.test import TestCase
from django.core.exceptions import ValidationError

from pulseapi.profiles.models import CohortRecord
from pulseapi.utility.validators import YearValidator
from pulseapi.profiles.factory import (
    BasicUserProfileFactory,
    ProgramTypeFactory,
)


class TestProfileCategories(TestCase):
    def setUp(self):
        self.profile = BasicUserProfileFactory()
        self.programs = [ProgramTypeFactory() for i in range(3)]

    def test_cohortrecord_year_under_valid_range(self):
        current_year = date.today().year
        expected_message = ValidationError(
            YearValidator.message,
            YearValidator.code,
            params={'min_year': 2000, 'max_year': current_year + 2}
        ).messages[0]

        with self.assertRaisesMessage(ValidationError, expected_message):
            CohortRecord.objects.create(
                profile=self.profile,
                program=self.programs[0],
                year=1999
            )

    def test_cohortrecord_year_over_valid_range(self):
        current_year = date.today().year
        expected_message = ValidationError(
            YearValidator.message,
            YearValidator.code,
            params={'min_year': 2000, 'max_year': current_year + 2}
        ).messages[0]

        with self.assertRaisesMessage(ValidationError, expected_message):
            CohortRecord.objects.create(
                profile=self.profile,
                program=self.programs[0],
                year=current_year + 10
            )

    def test_cohortrecord_missing_year_and_cohort_name(self):
        expected_message = 'Either the year or cohort must have a value'

        with self.assertRaisesMessage(ValidationError, expected_message):
            CohortRecord.objects.create(
                profile=self.profile,
                program=self.programs[0],
            )
