from django.test import TestCase, override_settings

from budgie_bird.models import Breeder, Bird
from budgie_bird.forms import BirdForm
from budgie_user.models import BudgieUser


class PyBudgieGeneralTest(TestCase):
    def setUp(self):
        self.app_user = BudgieUser.objects.create(
            username="henk", breeding_reg_nr="OMG1337"
        )
        self.breeder1 = Breeder.objects.create(
            user=self.app_user,
            first_name="Henk",
            last_name="de Vries",
            breeding_reg_nr="NAVI-2000",
        )

    @override_settings(LANGUAGE_CODE="nl")
    def test_dutch_translation(self):
        """Check if an error message will be returned in Dutch"""

        bird_henk = Bird.objects.create(
            user=self.app_user, breeder=self.breeder1, ring_number="Henk"
        )
        form = BirdForm(
            instance=bird_henk, data={"father": bird_henk, "mother": bird_henk}
        )
        self.assertIn("Een vogel kan niet zijn", form.errors["father"][0])
        self.assertIn("Een vogel kan niet zijn", form.errors["mother"][0])
