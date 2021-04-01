from django.test import TestCase, override_settings
from django.db.utils import IntegrityError

from budgie_bird.models import Breeder, Bird, ColorProperty
from budgie_bird.forms import BirdForm
from budgie_user.models import BudgieUser


class BreederModelTest(TestCase):

    fixtures = ["test_colors.json"]

    def setUp(self):

        self.app_user = BudgieUser.objects.create_user(
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

    def test_bird_unique_ringnumber_per_user(self):
        """ Check if the ring number is truly unique """

        # Register a bird with a new ring number (which is unique at this point)
        new_bird = Bird.objects.create(
            user=self.app_user, breeder=self.breeder1, ring_number="5TJJ-1337-2021"
        )
        self.assertIsInstance(new_bird, Bird)
        self.assertTrue(hasattr(new_bird, "pk"))
        self.assertEqual("5TJJ-1337-2021", new_bird.ring_number)

        # Register the same ring number for a different user
        second_user = BudgieUser.objects.create(
            username="harry", breeding_reg_nr="JEVER-2021"
        )
        same_bird = Bird.objects.create(
            user=second_user, breeder=self.breeder1, ring_number="5TJJ-1337-2021"
        )
        self.assertIsInstance(same_bird, Bird)
        self.assertTrue(hasattr(same_bird, "pk"))
        self.assertEqual("5TJJ-1337-2021", same_bird.ring_number)

        # Register the bird again
        with self.assertRaises(IntegrityError):
            Bird.objects.create(
                user=self.app_user, breeder=self.breeder1, ring_number="5TJJ-1337-2021"
            )

    def test_bird_default_gender(self):
        """ Check if gender is 'unknown' if user does not make choice """

        new_bird = Bird.objects.create(
            user=self.app_user, breeder=self.breeder1, ring_number="5TJJ-81-2018"
        )
        self.assertEqual(new_bird.gender, Bird.Gender.UNKNOWN)

    @override_settings(LANGUAGE_CODE="en-us")
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

    def test_bird_descendant_validation_ok(self):
        """ Check if a bird can have descendants """

        bird_henk = Bird.objects.create(user=self.app_user, ring_number="D")
        bird_mother = Bird.objects.create(user=self.app_user, ring_number="M")
        bird_father = Bird.objects.create(user=self.app_user, ring_number="F")
        form = BirdForm(
            instance=bird_henk, data={"father": bird_father, "mother": bird_mother}
        )
        self.assertTrue(True, form.is_valid())

    def test_bird_color_notation(self):
        """ Test if the color notation and color ranks will be outputted correctly """

        new_bird = Bird.objects.create(
            user=self.app_user, breeder=self.breeder1, ring_number="5TJJ-81-2018"
        )
        for color in ColorProperty.objects.all():
            color.user = self.app_user
        [new_bird.color_property.add(x) for x in range(1, 4)]
        self.assertEqual(new_bird.color_props(), "Dominant bont Cinnamon Geelmasker")
        ColorProperty.objects.filter(rank=2).update(rank=100)
        self.assertEqual(new_bird.color_props(), "Dominant bont Geelmasker Cinnamon")
