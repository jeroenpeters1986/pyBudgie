import glob
import os
from unittest import skip

from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from budgie_bird.models import Breeder, Bird
from budgie_breeding.models import BreedingCouple, BreedingSeason, Egg, Location
from budgie_user.models import BudgieUser


class BreedingAppAdminTest(TestCase):
    fixtures = ["test_breeders.json"]
    couple_overview_url = reverse("admin:budgie_breeding_breedingcouple_changelist")
    add_couple_url = reverse("admin:budgie_breeding_breedingcouple_add")
    season_overview_url = reverse("admin:budgie_breeding_breedingseason_changelist")
    add_season_url = reverse("admin:budgie_breeding_breedingseason_add")
    add_bird_url = reverse("admin:budgie_bird_bird_add")
    location_overview_url = reverse("admin:budgie_breeding_location_changelist")
    add_location_url = reverse("admin:budgie_breeding_location_add")
    egg_overview_url = reverse("admin:budgie_breeding_egg_changelist")
    add_egg_url = reverse("admin:budgie_breeding_egg_add")
    bulkadd_egg_url = reverse("admin:budgie_breeding_egg_bulk_add")

    def setUp(self):
        self.admin_credentials = {
            "username": "m.scott",
            "password": "RyanIsMyFriend",
            "first_name": "Micheal",
            "last_name": "Scott",
            "breeding_reg_nr": "DM-01",
            "email": "m.g.scott@dundermifflin.com",
        }
        self.user_credentials = {
            "username": "d.shrute",
            "password": "Monkey",
            "breeding_reg_nr": "Assistant to the DM-01",
            "email": "d.k.shrute@dundermifflin.com",
        }

        self.pybudgie_admin = BudgieUser.objects.create_superuser(
            username=self.admin_credentials["username"],
            password=self.admin_credentials["password"],
            first_name=self.admin_credentials["first_name"],
            last_name=self.admin_credentials["last_name"],
            email=self.admin_credentials["email"],
            breeding_reg_nr=self.admin_credentials["breeding_reg_nr"],
        )
        self.pybudgie_user = BudgieUser.objects.create_user(
            username=self.user_credentials["username"],
            password=self.user_credentials["password"],
            email=self.user_credentials["email"],
            breeding_reg_nr=self.user_credentials["breeding_reg_nr"],
            is_staff=True,
        )

        ct_bird = ContentType.objects.get_for_model(Bird)
        ct_breeder = ContentType.objects.get_for_model(Breeder)
        ct_breedcouple = ContentType.objects.get_for_model(BreedingCouple)
        ct_breedseason = ContentType.objects.get_for_model(BreedingSeason)
        ct_egg = ContentType.objects.get_for_model(Egg)
        ct_location = ContentType.objects.get_for_model(Location)
        permissions = Permission.objects.filter(
            content_type__in=(
                ct_bird,
                ct_breeder,
                ct_breedcouple,
                ct_breedseason,
                ct_egg,
                ct_location,
            )
        )
        self.pybudgie_user.user_permissions.set(permissions)

        self.bird_data_male = {
            "user": 1,
            "ring_number": "5TJJ-12-2018",
            "gender": "male",
            "color": "18.004.003",
            "date_of_birth": "2017-10-02",
            "owner": 1,
            "breeder": 2,
            "is_owned": True,
            "is_for_sale": False,
            "notes": "",
            "photo": "assets/budgie-silhouette.png",
            "color_property": [],
            "split_property": [],
        }
        self.bird_data_female = {
            "user": 1,
            "ring_number": "5TJJ-12-1337",
            "gender": "female",
            "color": "18.004.003",
            "date_of_birth": "2018-10-02",
            "owner": 1,
            "breeder": 2,
            "is_owned": True,
            "is_for_sale": False,
            "notes": "",
            "photo": "assets/budgie-silhouette.png",
            "color_property": [],
            "split_property": [],
        }

    def tearDown(self):
        for filename in glob.glob(
            "{}/test_test_bird*".format(settings.BIRD_PICTURE_UPLOAD_LOCATION)
        ):
            os.remove(filename)

    def setup_assign_breeders(self, user):
        # Update templates breeders
        for breeder in Breeder.objects.all():
            breeder.user = user
            breeder.save()

    def test_admin_add_breeding_season(self):
        """Test if the user can add a new breeding season in the Django admin"""

        self.setup_assign_breeders(self.pybudgie_user)
        self.client.login(
            username=self.user_credentials["username"],
            password=self.user_credentials["password"],
        )

        view_page = self.client.get(self.season_overview_url)
        self.assertEqual(view_page.status_code, 200)
        self.assertEqual(0, BreedingSeason.objects.count())

        season_params = {
            "starting_year": 2021,
            "starting_month": "MAR",
            "label": "BIER",
            # Because of th inlines...
            "breedingcouple_set-TOTAL_FORMS": 1,
            "breedingcouple_set-INITIAL_FORMS": 0,
            "breedingcouple_set-MIN_NUM_FORMS": 0,
            "id_breedingcouple_set-MAX_NUM_FORMS": 5,
        }
        response = self.client.post(self.add_season_url, season_params)
        self.assertEqual(response.status_code, 302)
        view_page = self.client.get(self.season_overview_url)
        self.assertEqual(view_page.status_code, 200)
        self.assertEqual(1, BreedingSeason.objects.count())

    def test_admin_add_birds_as_breeding_couple(self):
        """Test if the user can add a new breeding couple"""

        self.setup_assign_breeders(self.pybudgie_user)
        self.client.login(
            username=self.user_credentials["username"],
            password=self.user_credentials["password"],
        )

        view_page = self.client.get(self.season_overview_url)
        self.assertEqual(view_page.status_code, 200)
        self.assertEqual(0, BreedingSeason.objects.count())

        season_params = {
            "starting_year": 2021,
            "starting_month": "MAR",
            "label": "BIER",
            # Because of th inlines...
            "breedingcouple_set-TOTAL_FORMS": 1,
            "breedingcouple_set-INITIAL_FORMS": 0,
            "breedingcouple_set-MIN_NUM_FORMS": 0,
            "breedingcouple_set-MAX_NUM_FORMS": 5,
        }
        response = self.client.post(self.add_season_url, season_params)
        self.assertEqual(response.status_code, 302)

        view_page = self.client.get(self.season_overview_url)
        self.assertEqual(view_page.status_code, 200)
        self.assertEqual(1, BreedingSeason.objects.count())

        new_bird = self.bird_data_male
        response = self.client.post(self.add_bird_url, new_bird)
        self.assertEqual(response.status_code, 302)

        new_bird2 = self.bird_data_female
        response = self.client.post(self.add_bird_url, new_bird2)
        self.assertEqual(response.status_code, 302)

        bird = Bird.objects.get(ring_number=self.bird_data_male["ring_number"])
        self.assertIsInstance(bird, Bird)
        self.assertEqual(bird.user, self.pybudgie_user)
        bird2 = Bird.objects.get(ring_number=self.bird_data_female["ring_number"])
        self.assertIsInstance(bird2, Bird)
        self.assertEqual(bird2.user, self.pybudgie_user)
        self.assertEqual(2, Bird.objects.count())

        couple = {
            "male": bird.pk,
            "female": bird2.pk,
            "season": 1,
            # Because of th inlines...
            "egg_set-TOTAL_FORMS": 1,
            "egg_set-INITIAL_FORMS": 0,
            "egg_set-MIN_NUM_FORMS": 0,
            "egg_set-MAX_NUM_FORMS": 5,
        }
        self.client.post(self.add_couple_url, couple)
        self.assertEqual(1, BreedingCouple.objects.count())
        view_page = self.client.get(self.couple_overview_url)
        self.assertEqual(view_page.status_code, 200)

        view_page = self.client.get(
            reverse("admin:budgie_breeding_breedingcouple_change", args=[1])
        )
        self.assertEqual(view_page.status_code, 200)

    def test_admin_add_birds_as_breeding_couple_add_eggs_after(self):
        """Test if the user can add a new breeding couple and add eggs after"""

        self.setup_assign_breeders(self.pybudgie_user)
        self.client.login(
            username=self.user_credentials["username"],
            password=self.user_credentials["password"],
        )

        view_page = self.client.get(self.season_overview_url)
        self.assertEqual(view_page.status_code, 200)
        self.assertEqual(0, BreedingSeason.objects.count())

        season_params = {
            "starting_year": 2021,
            "starting_month": "MAR",
            "label": "BIER",
            # Because of th inlines...
            "breedingcouple_set-TOTAL_FORMS": 1,
            "breedingcouple_set-INITIAL_FORMS": 0,
            "breedingcouple_set-MIN_NUM_FORMS": 0,
            "breedingcouple_set-MAX_NUM_FORMS": 5,
        }
        response = self.client.post(self.add_season_url, season_params)
        self.assertEqual(response.status_code, 302)

        view_page = self.client.get(self.season_overview_url)
        self.assertEqual(view_page.status_code, 200)
        self.assertEqual(1, BreedingSeason.objects.count())

        new_bird = self.bird_data_male
        response = self.client.post(self.add_bird_url, new_bird)
        self.assertEqual(response.status_code, 302)

        new_bird2 = self.bird_data_female
        response = self.client.post(self.add_bird_url, new_bird2)
        self.assertEqual(response.status_code, 302)

        bird = Bird.objects.get(ring_number=self.bird_data_male["ring_number"])
        self.assertIsInstance(bird, Bird)
        self.assertEqual(bird.user, self.pybudgie_user)
        bird2 = Bird.objects.get(ring_number=self.bird_data_female["ring_number"])
        self.assertIsInstance(bird2, Bird)
        self.assertEqual(bird2.user, self.pybudgie_user)
        self.assertEqual(2, Bird.objects.count())

        couple = {
            "male": bird.pk,
            "female": bird2.pk,
            "season": 1,
            # Because of th inlines...
            "egg_set-TOTAL_FORMS": 1,
            "egg_set-INITIAL_FORMS": 0,
            "egg_set-MIN_NUM_FORMS": 0,
            "egg_set-MAX_NUM_FORMS": 5,
        }
        self.client.post(self.add_couple_url, couple)
        self.assertEqual(1, BreedingCouple.objects.count())
        self.assertEqual(0, Egg.objects.count())
        view_page = self.client.get(self.couple_overview_url)
        self.assertEqual(view_page.status_code, 200)

        edit_page_url = reverse("admin:budgie_breeding_breedingcouple_change", args=[1])
        edit_page = self.client.get(edit_page_url)
        self.assertEqual(edit_page.status_code, 200)

        couple_with_eggs = {
            "male": bird.pk,
            "female": bird2.pk,
            "season": 1,
            # Because of th inlines...
            "eggs-TOTAL_FORMS": 3,
            "eggs-INITIAL_FORMS": 0,
            "eggs-MIN_NUM_FORMS": 0,
            "eggs-MAX_NUM_FORMS": 10,
            "eggs-0-date": "2022-08-01",
            "eggs-0-status": "fertilized",
            "eggs-1-date": "2022-08-03",
            "eggs-1-status": "fertilized",
            "eggs-2-date": "2022-08-04",
            "eggs-2-status": "fertilized",
        }
        self.client.post(edit_page_url, couple_with_eggs)
        self.assertEqual(1, BreedingCouple.objects.count())
        self.assertEqual(3, Egg.objects.count())

    def test_admin_add_egg_to_breeding_couple(self):
        """Test if the admin can add eggs to a new breeding couple"""

        self.setup_assign_breeders(self.pybudgie_user)
        self.client.login(
            username=self.user_credentials["username"],
            password=self.user_credentials["password"],
        )

        view_page = self.client.get(self.season_overview_url)
        self.assertEqual(view_page.status_code, 200)
        self.assertEqual(0, BreedingSeason.objects.count())

        season_params = {
            "starting_year": 2021,
            "starting_month": "MAR",
            "label": "BIER",
            # Because of th inlines...
            "breedingcouple_set-TOTAL_FORMS": 1,
            "breedingcouple_set-INITIAL_FORMS": 0,
            "breedingcouple_set-MIN_NUM_FORMS": 0,
            "breedingcouple_set-MAX_NUM_FORMS": 5,
        }
        response = self.client.post(self.add_season_url, season_params)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(1, BreedingSeason.objects.count())

        new_bird = self.bird_data_male
        response = self.client.post(self.add_bird_url, new_bird)
        self.assertEqual(response.status_code, 302)

        new_bird2 = self.bird_data_female
        response = self.client.post(self.add_bird_url, new_bird2)
        self.assertEqual(response.status_code, 302)

        bird = Bird.objects.get(ring_number=self.bird_data_male["ring_number"])
        bird2 = Bird.objects.get(ring_number=self.bird_data_female["ring_number"])

        couple = {
            "male": bird.pk,
            "female": bird2.pk,
            "season": 1,
            # Because of th inlines...
            "egg_set-TOTAL_FORMS": 1,
            "egg_set-INITIAL_FORMS": 0,
            "egg_set-MIN_NUM_FORMS": 0,
            "egg_set-MAX_NUM_FORMS": 5,
        }
        self.client.post(self.add_couple_url, couple)
        self.assertEqual(1, BreedingCouple.objects.count())

        view_page = self.client.get(self.egg_overview_url)
        self.assertEqual(view_page.status_code, 200)
        self.assertEqual(0, Egg.objects.count())

        egg_params = {
            "couple": 1,
            "date": "2022-08-01",
            "status": "fertilized",
        }
        response = self.client.post(self.add_egg_url, egg_params)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(1, Egg.objects.count())

    def test_admin_can_add_breeding_couple_on_season_overview(self):
        """Test if the admin can add breeding couples on season add view"""

        self.setup_assign_breeders(self.pybudgie_user)
        self.client.login(
            username=self.user_credentials["username"],
            password=self.user_credentials["password"],
        )

        new_bird = self.bird_data_male
        new_bird["user"] = self.pybudgie_admin.pk
        response = self.client.post(self.add_bird_url, new_bird)
        self.assertEqual(response.status_code, 302)

        new_bird = self.bird_data_male.copy()
        new_bird["user"] = self.pybudgie_admin.pk
        new_bird["ring_number"] = "5TJJ-Harry-Haak"
        response = self.client.post(self.add_bird_url, new_bird)
        self.assertEqual(response.status_code, 302)

        new_bird2 = self.bird_data_female
        new_bird2["user"] = self.pybudgie_admin.pk
        response = self.client.post(self.add_bird_url, new_bird2)
        self.assertEqual(response.status_code, 302)

        self.assertEqual(3, Bird.objects.all().count())

        bird = Bird.objects.get(ring_number=self.bird_data_male["ring_number"])
        bird2 = Bird.objects.get(ring_number=self.bird_data_female["ring_number"])

        season_params = {
            "user": self.pybudgie_admin.pk,
            "starting_year": 2021,
            "starting_month": "MAR",
            "label": "BIER",
            # Because of th inlines...
            "breedingcouple_set-TOTAL_FORMS": 1,
            "breedingcouple_set-INITIAL_FORMS": 0,
            "breedingcouple_set-MIN_NUM_FORMS": 0,
            "breedingcouple_set-MAX_NUM_FORMS": 5,
            "breedingcouple_set-0-id": "",
            "breedingcouple_set-0-male": bird.pk,
            "breedingcouple_set-0-female": bird2.pk,
            "breedingcouple_set-0-user": self.pybudgie_admin.pk,
        }
        response = self.client.post(self.add_season_url, season_params)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(1, BreedingSeason.objects.count())
        self.assertEqual(1, BreedingCouple.objects.count())

    def test_admin_can_bulk_add_eggs_to_breedcouples_and_test_expected_dates(self):
        """Test if the admin can bulk-add eggs to breeding couples, also test expecting-dates"""

        self.setup_assign_breeders(self.pybudgie_user)
        self.client.login(
            username=self.user_credentials["username"],
            password=self.user_credentials["password"],
        )

        view_page = self.client.get(self.add_season_url)
        self.assertEqual(view_page.status_code, 200)

        view_page = self.client.get(self.season_overview_url)
        self.assertEqual(view_page.status_code, 200)
        self.assertEqual(0, BreedingSeason.objects.count())

        season_params = {
            "user": self.pybudgie_admin.pk,
            "starting_year": 2021,
            "starting_month": "MAR",
            "label": "BIER",
            # Because of th inlines...
            "breedingcouple_set-TOTAL_FORMS": 1,
            "breedingcouple_set-INITIAL_FORMS": 0,
            "breedingcouple_set-MIN_NUM_FORMS": 0,
            "breedingcouple_set-MAX_NUM_FORMS": 5,
        }
        response = self.client.post(self.add_season_url, season_params)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(1, BreedingSeason.objects.count())

        new_bird = self.bird_data_male
        new_bird["user"] = self.pybudgie_admin.pk
        response = self.client.post(self.add_bird_url, new_bird)
        self.assertEqual(response.status_code, 302)

        new_bird = self.bird_data_male.copy()
        new_bird["user"] = self.pybudgie_admin.pk
        new_bird["ring_number"] = "5TJJ-Harry-Haak"
        response = self.client.post(self.add_bird_url, new_bird)
        self.assertEqual(response.status_code, 302)

        new_bird2 = self.bird_data_female
        new_bird2["user"] = self.pybudgie_admin.pk
        response = self.client.post(self.add_bird_url, new_bird2)
        self.assertEqual(response.status_code, 302)

        self.assertEqual(3, Bird.objects.all().count())

        bird = Bird.objects.get(ring_number=self.bird_data_male["ring_number"])
        bird2 = Bird.objects.get(ring_number=self.bird_data_female["ring_number"])
        bird3 = Bird.objects.get(ring_number="5TJJ-Harry-Haak")

        couple = {
            "male": bird.pk,
            "female": bird2.pk,
            "user": self.pybudgie_admin.pk,
            "season": 1,
            # Because of th inlines...
            "egg_set-TOTAL_FORMS": 1,
            "egg_set-INITIAL_FORMS": 0,
            "egg_set-MIN_NUM_FORMS": 0,
            "egg_set-MAX_NUM_FORMS": 5,
        }
        self.client.post(self.add_couple_url, couple)
        self.assertEqual(1, BreedingCouple.objects.count())

        andercouple = couple.copy()
        andercouple["male"] = bird3.pk
        self.client.post(self.add_couple_url, andercouple)
        self.assertEqual(2, BreedingCouple.objects.count())

        view_page = self.client.get(self.add_egg_url)
        self.assertEqual(view_page.status_code, 200)

        view_page = self.client.get(self.bulkadd_egg_url)
        self.assertEqual(view_page.status_code, 200)
        self.assertEqual(0, Egg.objects.count())

        egg_params = {
            "couples[]": [1, 2, 25],
            "date": "01-08-2022",
        }
        response = self.client.post(self.bulkadd_egg_url, egg_params)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.bulkadd_egg_url)

        response = self.client.post(self.bulkadd_egg_url, egg_params, follow=True)
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertContains(response, "Er zijn velden leeggelaten")

        egg_params.update({"status": "fertilized"})
        response = self.client.post(self.bulkadd_egg_url, egg_params)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(2, Egg.objects.count())
        self.assertEqual(2, Egg.objects.filter(user=self.pybudgie_user).count())

        last_egg = Egg.objects.last()
        self.assertEqual(
            "19-08-2022", last_egg.expected_hatch_date.strftime("%d-%m-%Y")
        )
        last_egg.status = Egg.Status.UNFERTILIZED
        last_egg.save()
        self.assertEqual(None, last_egg.expected_hatch_date)

    def test_admin_no_breeding_couple_on_formset_seasons(self):
        """Test the formset of Breeding Couples"""

        self.setup_assign_breeders(self.pybudgie_user)
        self.client.login(
            username=self.user_credentials["username"],
            password=self.user_credentials["password"],
        )

        view_page = self.client.get(self.add_couple_url)
        self.assertEqual([], view_page.context["inline_admin_formsets"])

        Bird.objects.create(user=self.pybudgie_user, ring_number="henk")
        Bird.objects.create(user=self.pybudgie_user, ring_number="nina")
        BreedingSeason.objects.create(
            user=self.pybudgie_user, starting_year=2022, starting_month=1
        )
        BreedingCouple.objects.create(
            user=self.pybudgie_user, male_id=1, female_id=2, season_id=1
        )
        view_page = self.client.get(
            reverse("admin:budgie_breeding_breedingcouple_change", args=[1])
        )
        self.assertNotEqual([], view_page.context["inline_admin_formsets"])
        self.assertEqual(list, type(view_page.context["inline_admin_formsets"]))

    @skip("TODO: Fix this test")
    def test_admin_add_egg_to_breeding_couple_inline(self):
        """Test if the admin can inline add a new breeding couple"""
        self.setup_assign_breeders(self.pybudgie_user)
        self.client.login(
            username=self.user_credentials["username"],
            password=self.user_credentials["password"],
        )

        view_page = self.client.get(self.season_overview_url)
        self.assertEqual(view_page.status_code, 200)
        self.assertEqual(0, BreedingSeason.objects.count())

        season_params = {
            "starting_year": 2021,
            "starting_month": 3,
            "label": "BIER",
            # Because of th inlines...
            "breedingcouple_set-TOTAL_FORMS": 1,
            "breedingcouple_set-INITIAL_FORMS": 0,
            "breedingcouple_set-MIN_NUM_FORMS": 0,
            "breedingcouple_set-MAX_NUM_FORMS": 5,
        }
        response = self.client.post(self.add_season_url, season_params)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(1, BreedingSeason.objects.count())

        new_bird = self.bird_data_male
        response = self.client.post(self.add_bird_url, new_bird)
        self.assertEqual(response.status_code, 302)

        new_bird2 = self.bird_data_female
        response = self.client.post(self.add_bird_url, new_bird2)
        self.assertEqual(response.status_code, 302)

        bird = Bird.objects.get(ring_number=self.bird_data_male["ring_number"])
        bird2 = Bird.objects.get(ring_number=self.bird_data_female["ring_number"])

        couple = {
            "male": bird.pk,
            "female": bird2.pk,
            "season": 1,
            # Because of th inlines...
            "egg_set-TOTAL_FORMS": 1,
            "egg_set-INITIAL_FORMS": 0,
            "egg_set-MIN_NUM_FORMS": 0,
            "egg_set-MAX_NUM_FORMS": 5,
        }
        self.client.post(self.add_couple_url, couple)
        self.assertEqual(1, BreedingCouple.objects.count())

        view_page = self.client.get(
            reverse("admin:budgie_breeding_breedingcouple_change", args=[1])
        )
        self.assertEqual(view_page.status_code, 200)
        couple = {
            "male": bird.pk,
            "female": bird2.pk,
            "season": 1,
            # Because of th inlines...
            "egg_set-TOTAL_FORMS": 1,
            "egg_set-INITIAL_FORMS": 0,
            "egg_set-MIN_NUM_FORMS": 0,
            "egg_set-MAX_NUM_FORMS": 5,
            "egg_set-0-id": "",
            "egg_set-0-couple": 1,
            "egg_set-0-date": "11-10-2022",
            "egg_set-0-status": "died_off",
        }
        response = self.client.post(
            reverse("admin:budgie_breeding_breedingcouple_change", args=[1]), couple
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(1, Egg.objects.count())

    def test_admin_location_overview(self):
        """Test the location overview"""

        self.setup_assign_breeders(self.pybudgie_user)
        self.client.login(
            username=self.user_credentials["username"],
            password=self.user_credentials["password"],
        )

        view_page = self.client.get(self.location_overview_url)
        self.assertEqual(view_page.status_code, 200)

        view_page = self.client.get(self.add_location_url)
        self.assertEqual(view_page.status_code, 200)

    def test_location_string_taken_status(self):
        """Test the location string, taken-status and the links to breeding couples"""

        location_name = "Kooi 1."

        self.setup_assign_breeders(self.pybudgie_user)
        self.client.login(
            username=self.user_credentials["username"],
            password=self.user_credentials["password"],
        )

        new_bird = self.bird_data_male
        new_bird["user"] = self.pybudgie_admin.pk
        response = self.client.post(self.add_bird_url, new_bird)
        self.assertEqual(response.status_code, 302)

        new_bird2 = self.bird_data_female
        new_bird2["user"] = self.pybudgie_admin.pk
        response = self.client.post(self.add_bird_url, new_bird2)
        self.assertEqual(response.status_code, 302)

        bird = Bird.objects.get(ring_number=self.bird_data_male["ring_number"])
        bird2 = Bird.objects.get(ring_number=self.bird_data_female["ring_number"])

        BreedingSeason.objects.create(
            user=self.pybudgie_user, starting_year=2022, starting_month=1
        )

        couple = {
            "male": bird.pk,
            "female": bird2.pk,
            "user": self.pybudgie_admin.pk,
            "season": 1,
            # Because of th inlines...
            "egg_set-TOTAL_FORMS": 1,
            "egg_set-INITIAL_FORMS": 0,
            "egg_set-MIN_NUM_FORMS": 0,
            "egg_set-MAX_NUM_FORMS": 5,
        }
        self.client.post(self.add_couple_url, couple)
        self.assertEqual(1, BreedingCouple.objects.count())

        view_page = self.client.get(self.add_location_url)
        self.assertEqual(view_page.status_code, 200)

        loc = {
            "code": location_name,
            "description": "In de hoek jung",
            "user": self.pybudgie_admin.pk,
            "current_breeding_couple": 1,
        }
        self.client.post(self.add_location_url, loc)
        self.assertEqual(1, Location.objects.count())

        locatie = Location.objects.first()
        self.assertEqual(location_name, locatie.code)
        self.assertEqual(
            "{} (Bezet)".format(location_name), locatie.__str__()
        )  # TODO: Check for English?
        locatie.current_breeding_couple = None
        locatie.save()
        self.assertEqual("{}".format(location_name), locatie.__str__())

        response = self.client.get(self.location_overview_url)
        self.assertContains(
            response, 'class="field-is_taken"><img src="/static/admin/img/icon-no.svg'
        )

        locatie.current_breeding_couple = BreedingCouple.objects.first()
        locatie.save()
        response = self.client.get(self.location_overview_url)
        breeding_couple_link = reverse(
            "admin:budgie_breeding_breedingcouple_change", args=[1]
        )
        self.assertNotContains(
            response, 'class="field-is_taken"><img src="/static/admin/img/icon-no.svg'
        )
        self.assertContains(
            response, 'class="field-is_taken"><img src="/static/admin/img/icon-yes.svg'
        )
        self.assertContains(response, breeding_couple_link)
