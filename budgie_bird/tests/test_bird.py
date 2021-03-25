from django.test import TestCase

from budgie_bird.models import Breeder, Bird
from budgie_bird.forms import BirdForm
from budgie_user.models import BudgieUser


class BreederModelTest(TestCase):
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
        self.existing_bird = Bird.objects.create(
            user=self.app_user, breeder=self.breeder1, ring_number="5TJJ-1337-2018"
        )

    def test_bird_default_gender(self):
        """ Check if gender is 'unknown' if user does not make choice """

        new_bird = Bird.objects.create(
            user=self.app_user, breeder=self.breeder1, ring_number="5TJJ-81-2018"
        )
        self.assertEqual(new_bird.gender, Bird.Gender.UNKNOWN)

    def test_bird_descendant_validation(self):
        """ Check if a bird can be it's own parent (kerelll!!) """

        bird_henk = Bird.objects.create(
            user=self.app_user, breeder=self.breeder1, ring_number="Henk"
        )
        form = BirdForm(
            instance=bird_henk, data={"father": bird_henk, "mother": bird_henk}
        )
        self.assertIn("Bird cannot be", form.errors["father"][0])
        self.assertIn("Bird cannot be", form.errors["mother"][0])
