import datetime
import glob
import os
from unittest import mock

from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from budgie_bird.forms import BirdForm
from budgie_bird.models import Breeder, Bird, ColorProperty
from budgie_user.models import BudgieUser


class BirdAppAdminTest(TestCase):
    fixtures = ["test_breeders.json"]
    bird_overview_url = reverse("admin:budgie_bird_bird_changelist")
    add_bird_url = reverse("admin:budgie_bird_bird_add")
    breeder_overview_url = reverse("admin:budgie_bird_breeder_changelist")
    add_breeder_url = reverse("admin:budgie_bird_breeder_add")

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
        content_type_bird = ContentType.objects.get_for_model(Bird)
        content_type_breeder = ContentType.objects.get_for_model(Breeder)
        permissions = Permission.objects.filter(
            content_type__in=(content_type_bird, content_type_breeder)
        )
        self.pybudgie_user.user_permissions.set(permissions)

        self.bird_data = {
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

    def test_admin_bird_add_by_admin(self):
        """Test if the admin can add a new bird"""
        self.setup_assign_breeders(self.pybudgie_admin)
        self.client.login(
            username=self.admin_credentials["username"],
            password=self.admin_credentials["password"],
        )

        view_page = self.client.get(self.add_bird_url)
        self.assertEqual(view_page.status_code, 200)
        self.assertEqual(0, Bird.objects.count())

        new_bird = self.bird_data
        new_bird["user"] = self.pybudgie_admin.pk
        response = self.client.post(self.add_bird_url, new_bird)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.bird_overview_url)

        bird = Bird.objects.get(ring_number=self.bird_data["ring_number"])
        self.assertIsInstance(bird, Bird)
        self.assertEqual(bird.user, self.pybudgie_admin)
        self.assertEqual(1, Bird.objects.count())

    def test_admin_bird_add_cannot_die_before_born_date(self):
        """Test if the cannot-die-before-birthdate check works"""
        self.setup_assign_breeders(self.pybudgie_user)
        self.client.login(
            username=self.user_credentials["username"],
            password=self.user_credentials["password"],
        )

        view_page = self.client.get(self.add_bird_url)
        self.assertEqual(view_page.status_code, 200)
        self.assertEqual(0, Bird.objects.count())

        spullen_bird = {
            "ring_number": "5TJJ-12-2010",
            "gender": "male",
            "color": "18.004.003",
            "date_of_birth": "2017-10-02",
            "date_of_death": "2015-10-02",
            "owner": 1,
            "breeder": 2,
            "is_owned": True,
            "is_for_sale": False,
            "notes": "",
            "photo": "assets/budgie-silhouette.png",
            "color_property": [],
            "split_property": [],
        }
        response = self.client.post(self.add_bird_url, spullen_bird)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "Een vogel kan niet doodgaan voordat het geboren is"
        )  # FIXME: Test for English, @override_settings(LANGUAGE_CODE="en") doesnt seem to work

    def test_bird_form_date_of_death(self):
        spullen_bird = {
            "user": 1,
            "ring_number": "5TJJ-12-2010",
            "gender": "male",
            "color": "18.004.003",
            "date_of_birth": "2017-10-02",
            "date_of_death": "2015-10-02",
            "owner": 1,
            "breeder": 2,
            "is_owned": True,
            "is_for_sale": False,
            "notes": "",
            "photo": "assets/budgie-silhouette.png",
            "color_property": [],
            "split_property": [],
        }
        form = BirdForm(spullen_bird)
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "date_of_death", [])

        goeie_bird = {
            "user": 1,
            "ring_number": "5TJJ-12-2010",
            "gender": "male",
            "color": "18.004.003",
            "date_of_birth": "2017-10-02",
            "date_of_death": "2019-10-02",
            "owner": 1,
            "breeder": 2,
            "is_owned": True,
            "is_for_sale": False,
            "notes": "",
            "photo": "assets/budgie-silhouette.png",
            "color_property": [],
            "split_property": [],
        }
        form = BirdForm(goeie_bird)
        self.assertTrue(form.is_valid())

    def test_admin_user_without_group_or_permission(self):
        """Test if a staff user without the proper permissions gets a 403"""

        content_type = ContentType.objects.get_for_model(Bird)
        for permission in Permission.objects.filter(content_type=content_type):
            self.pybudgie_user.user_permissions.remove(permission)

        self.client.login(
            username=self.user_credentials["username"],
            password=self.user_credentials["password"],
        )
        view_page = self.client.get(self.add_bird_url)
        self.assertEqual(view_page.status_code, 403)

    def test_admin_bird_add_by_user(self):
        """Test if a normal user can add a new bird"""
        self.setup_assign_breeders(self.pybudgie_user)
        self.client.login(
            username=self.user_credentials["username"],
            password=self.user_credentials["password"],
        )

        # Try to insert a bird with Michaels data (Oh you sneaky bastard!!)
        new_bird = self.bird_data
        new_bird["user"] = self.pybudgie_admin.pk  # Oehlala!
        response = self.client.post(self.add_bird_url, self.bird_data)
        self.assertEqual(response.status_code, 302)  # Redirected, probably to the index

        bird = Bird.objects.get(ring_number=self.bird_data["ring_number"])
        self.assertIsInstance(bird, Bird)
        self.assertNotEqual(bird.user, self.pybudgie_admin)
        self.assertEqual(bird.user, self.pybudgie_user)
        self.assertEqual(1, Bird.objects.count())

    def test_admin_bird_photo_preview(self):
        """Test if the birdpreview is displayed"""
        self.setup_assign_breeders(self.pybudgie_user)
        self.client.login(
            username=self.user_credentials["username"],
            password=self.user_credentials["password"],
        )

        new_bird = self.bird_data
        new_bird["user"] = self.pybudgie_user.pk  # Oehlala!
        response = self.client.post(self.add_bird_url, self.bird_data)
        self.assertEqual(response.status_code, 302)  # Redirected, probably to the index
        response = self.client.get(self.bird_overview_url)
        self.assertContains(response, 'class="birdpreview"')
        self.assertContains(response, settings.BIRD_PICTURE_DEFAULT)

    def test_admin_bird_photo_upload_test(self):
        """Test if user can attach a photo"""
        self.setup_assign_breeders(self.pybudgie_user)
        self.client.login(
            username=self.user_credentials["username"],
            password=self.user_credentials["password"],
        )

        photo_filename = "test_test_bird{}.png".format(
            datetime.datetime.now().timestamp()
        )
        photo_data = open(
            "{}/../budgie_bird/fixtures/testpic.png".format(settings.BASE_DIR), "rb"
        ).read()
        photo = SimpleUploadedFile(photo_filename, photo_data)

        new_bird = self.bird_data
        new_bird["photo"] = photo
        response = self.client.post(self.add_bird_url, new_bird)
        self.assertEqual(response.status_code, 302)

        response = self.client.get(self.bird_overview_url)
        self.assertContains(response, 'class="birdpreview"')
        self.assertContains(response, photo_filename)  # Test for the filename
        self.assertNotContains(
            response, settings.BIRD_PICTURE_DEFAULT
        )  # We dont want the default

    def test_bird_get_queryset_mixin_called(self):
        """Test if the BudgieUser mixin is used in the admin"""

        self.client.login(
            username=self.user_credentials["username"],
            password=self.user_credentials["password"],
        )

        with mock.patch("budgie_user.mixins.BudgieUserMixin.get_queryset") as mocked:
            response = self.client.get(self.bird_overview_url)
            mocked.assert_called_once()

            self.assertEqual(str(response.context["user"]), "d.shrute")
            self.assertEqual(response.status_code, 200)

    def test_admin_userfilter_mixin_working_for_user(self):
        """Test if the BudgieUser mixin is used in the admin"""

        Bird.objects.create(user=self.pybudgie_user, ring_number="5TJJ-2802-2021")
        Bird.objects.create(user=self.pybudgie_user, ring_number="5TJJ-0801-2021")
        Bird.objects.create(user=self.pybudgie_user, ring_number="5TJJ-2710-2021")
        Bird.objects.create(user=self.pybudgie_admin, ring_number="5TJJ-2011-2021")

        self.client.login(
            username=self.user_credentials["username"],
            password=self.user_credentials["password"],
        )
        response = self.client.get(self.bird_overview_url)
        self.assertContains(response, "5TJJ-2802-2021")
        self.assertContains(response, "5TJJ-0801-2021")
        self.assertContains(response, "5TJJ-2710-2021")
        self.assertNotContains(response, "5TJJ-2011-2021")

    def test_admin_userfilter_mixin_admin_user(self):
        """Test if the BudgieUser does not limit the administrator user"""

        Bird.objects.create(user=self.pybudgie_admin, ring_number="6TJJ-1-2021")
        Bird.objects.create(user=self.pybudgie_user, ring_number="6TJJ-2-2021")
        Bird.objects.create(user=self.pybudgie_user, ring_number="6TJJ-3-2021")
        Bird.objects.create(user=self.pybudgie_admin, ring_number="6TJJ-4-2021")

        self.client.login(
            username=self.admin_credentials["username"],
            password=self.admin_credentials["password"],
        )
        response = self.client.get(self.bird_overview_url)
        self.assertContains(response, "6TJJ-1-2021")
        self.assertContains(response, "6TJJ-2-2021")
        self.assertContains(response, "6TJJ-3-2021")
        self.assertContains(response, "6TJJ-4-2021")

    def test_admin_userfilter_color(self):
        """Test if the BudgieUsers colorlist is limited to the current user"""

        ColorProperty.objects.create(
            user=self.pybudgie_user, color_name="DarkBlue", rank=1
        )
        ColorProperty.objects.create(
            user=self.pybudgie_user, color_name="DarkYellow", rank=3
        )
        ColorProperty.objects.create(
            user=self.pybudgie_admin, color_name="DarkPink", rank=4
        )

        self.client.login(
            username=self.user_credentials["username"],
            password=self.user_credentials["password"],
        )
        response = self.client.get(self.add_bird_url)
        self.assertNotContains(response, "DarkPink")
        self.assertContains(response, "DarkBlue")
        self.assertContains(response, "DarkYellow")

    def test_admin_display_age_calculation(self):
        """Test if the age calculation works (also test the minus-zero clause)"""

        for num in range(1, 13):
            stringnum = "{:02d}".format(num)
            Bird.objects.create(
                user=self.pybudgie_user,
                ring_number="5TJJ-2802-20{}".format(stringnum),
                date_of_birth="2018-{}-14".format(stringnum),
            ),

        self.client.login(
            username=self.user_credentials["username"],
            password=self.user_credentials["password"],
        )
        response = self.client.get(self.bird_overview_url)
        self.assertContains(response, "jaren")  # FIXME, test in English

    def test_bird_csv_export(self):
        """Test if the CSV-export works"""

        testbirds = [
            Bird.objects.create(user=self.pybudgie_user, ring_number="5TJJ-2802-2021"),
            Bird.objects.create(user=self.pybudgie_user, ring_number="5TJJ-0801-2021"),
            Bird.objects.create(user=self.pybudgie_user, ring_number="5TJJ-2710-2021"),
        ]

        self.client.login(
            username=self.user_credentials["username"],
            password=self.user_credentials["password"],
        )

        post_data = {
            "action": "export_as_csv",
            "_selected_action": [b.pk for b in testbirds],
        }
        response = self.client.post(self.bird_overview_url, post_data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "id,user,ring_number,gender,color,date_of_birth,date_of_death,father,"
            "mother,breeder,owner,is_owned,is_for_sale,notes,photo",
        )
        self.assertContains(response, "5TJJ-2802-2021")
        self.assertContains(response, "5TJJ-0801-2021")
        self.assertContains(response, "5TJJ-2710-2021")
        self.assertEqual(response.headers["Content-Type"], "text/csv")

    def test_admin_bird_familytree(self):
        """Test if user can view a birds familytree"""

        self.client.login(
            username=self.user_credentials["username"],
            password=self.user_credentials["password"],
        )

        bird_henk = Bird.objects.create(user=self.pybudgie_user, ring_number="D")
        bird_mother = Bird.objects.create(user=self.pybudgie_user, ring_number="M")
        bird_father = Bird.objects.create(user=self.pybudgie_user, ring_number="F")
        bird_henk.father = bird_father
        bird_henk.mother = bird_mother
        bird_henk.save()

        response = self.client.get(
            reverse(
                "admin:budgie_bird_bird_familytree", kwargs={"object_id": bird_henk.pk}
            )
        )
        self.assertContains(response, "digraph G {")  # Graphviz notation
        self.assertEqual(response.status_code, 200)

    def test_admin_bird_familytree_non_existing_bird(self):
        """Test if user can view a birds familytree"""

        self.client.login(
            username=self.user_credentials["username"],
            password=self.user_credentials["password"],
        )
        response = self.client.get(
            reverse("admin:budgie_bird_bird_familytree", kwargs={"object_id": 28021986})
        )
        self.assertEqual(response.status_code, 302)

        response = self.client.get(
            reverse(
                "admin:budgie_bird_bird_familytree", kwargs={"object_id": 28021986}
            ),
            follow=True,
        )
        self.assertContains(
            response, "bestaat niet"
        )  # FIXME: Test for English, @override_settings(LANGUAGE_CODE="en") doesnt seem to work

    def test_bird_mark_as_owned(self):
        """Test if the Mark as owned admin action works"""

        Bird.objects.create(user=self.pybudgie_user, ring_number="5TJJ-2802-2022"),
        selected_birds = [
            Bird.objects.create(user=self.pybudgie_user, ring_number="5TJJ-0801-2022"),
            Bird.objects.create(user=self.pybudgie_user, ring_number="5TJJ-2710-2022"),
        ]

        self.client.login(
            username=self.user_credentials["username"],
            password=self.user_credentials["password"],
        )

        post_data = {
            "action": "mark_as_owned",
            "_selected_action": [b.pk for b in selected_birds],
        }
        response = self.client.post(self.bird_overview_url, post_data, follow=True)

        self.assertContains(
            response, "gemarkeerd als In bezit"
        )  # FIXME: Test for English, @override_settings(LANGUAGE_CODE="en") doesnt seem to work
        self.assertEqual(3, Bird.objects.filter(user=self.pybudgie_user).count())
        self.assertEqual(
            2, Bird.objects.filter(user=self.pybudgie_user, is_owned=True).count()
        )
        self.assertTrue(Bird.objects.get(ring_number="5TJJ-0801-2022").is_owned)
        self.assertTrue(Bird.objects.get(ring_number="5TJJ-2710-2022").is_owned)
        self.assertFalse(Bird.objects.get(ring_number="5TJJ-2802-2022").is_owned)

    def test_bird_mark_as_for_sale(self):
        """Test if the For Sale action works in the admin"""

        Bird.objects.create(user=self.pybudgie_user, ring_number="Dunder Mifflin"),
        sale_bird = Bird.objects.create(user=self.pybudgie_user, ring_number="Staples")

        self.client.login(
            username=self.user_credentials["username"],
            password=self.user_credentials["password"],
        )

        post_data = {
            "action": "mark_as_for_sale",
            "_selected_action": [sale_bird.pk],
        }
        response = self.client.post(self.bird_overview_url, post_data, follow=True)

        self.assertContains(
            response, "gemarkeerd als Te koop"
        )  # FIXME: Test for English, @override_settings(LANGUAGE_CODE="en") doesnt seem to work
        self.assertEqual(2, Bird.objects.filter(user=self.pybudgie_user).count())
        self.assertTrue(Bird.objects.get(ring_number="Staples").is_for_sale)
        self.assertFalse(Bird.objects.get(ring_number="Dunder Mifflin").is_for_sale)

    def test_admin_breeders(self):
        """Test if the admin can view the breeders"""
        self.setup_assign_breeders(self.pybudgie_admin)
        self.client.login(
            username=self.admin_credentials["username"],
            password=self.admin_credentials["password"],
        )

        view_page = self.client.get(self.breeder_overview_url)
        self.assertEqual(view_page.status_code, 200)
