from django.test import TestCase

from budgie_bird.models import Breeder
from budgie_user.models import BudgieUser


class BreederModelTest(TestCase):
    def setUp(self):

        self.app_user = BudgieUser.objects.create(
            username="henk", breeding_reg_nr="OMG1337"
        )
        self.other_user = BudgieUser.objects.create(
            username="cees", breeding_reg_nr="OhNo666"
        )

        self.breeder1 = Breeder.objects.create(
            user=self.app_user,
            first_name="Henk",
            last_name="de Vries",
            breeding_reg_nr="NAVI-2000",
        )

    def test_breeder_information(self):
        """ Check if the breeder's information is saved"""
        self.assertIsInstance(self.breeder1.first_name, str)
        self.assertIsInstance(self.breeder1.last_name, str)
        self.assertIsInstance(self.breeder1.breeding_reg_nr, str)

        self.assertEqual(self.breeder1.__str__(), "de Vries, Henk (NAVI-2000)")
