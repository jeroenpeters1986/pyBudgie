from datetime import datetime
from django.test import TestCase

from .models import Breeder
from budgie_user.models import BudgieUser


class BreederModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.app_user = BudgieUser.objects.create(breeding_reg_nr="OMG1337")

        cls.breeder = Breeder.objects.create(
            user=cls.app_user,
            first_name="Henk",
            last_name="de Vries",
            breeding_reg_nr="NAVI-2000",
        )

    def test_is_information_correct(self):
        self.assertIsInstance(self.breeder.first_name, str)
        self.assertIsInstance(self.breeder.last_name, str)
        self.assertIsInstance(self.breeder.breeding_reg_nr, str)

        self.assertEqual(self.breeder.__str__(), "Henk de Vries (NAVI-2000)")
