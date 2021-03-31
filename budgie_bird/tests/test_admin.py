import datetime

from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from budgie_bird.models import Breeder, Bird
from budgie_user.models import BudgieUser


class DocumentAdminFormTest(TestCase):
    fixtures = ["test_breeders.json"]
    bird_overview_url = reverse("admin:budgie_bird_bird_changelist")
    add_bird_url = reverse("admin:budgie_bird_bird_add")

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

    def setup_assign_breeders(self, user):
        # Update template breeders
        for breeder in Breeder.objects.all():
            breeder.user = user
            breeder.save()

    def setup_assign_users_bird_permissions(self, user):
        content_type = ContentType.objects.get_for_model(Bird)
        permissions = Permission.objects.filter(content_type=content_type)
        user.user_permissions.set(permissions)

    def test_admin_bird_add_by_admin(self):
        """ Test if the admin can add a new bird """
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
        response = self.client.post(self.add_bird_url, self.bird_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers["location"][1], self.bird_overview_url)

        bird = Bird.objects.get(ring_number=self.bird_data["ring_number"])
        self.assertIsInstance(bird, Bird)
        self.assertEqual(bird.user, self.pybudgie_admin)
        self.assertEqual(1, Bird.objects.count())

    def test_admin_user_without_group_or_permission(self):
        """ Test if a staff user without the proper permissions gets a 403 """
        self.client.login(
            username=self.user_credentials["username"],
            password=self.user_credentials["password"],
        )
        view_page = self.client.get(self.add_bird_url)
        self.assertEqual(view_page.status_code, 403)

    def test_admin_bird_add_by_user(self):
        """ Test if a normal user can add a new bird """
        self.setup_assign_breeders(self.pybudgie_user)
        self.setup_assign_users_bird_permissions(self.pybudgie_user)
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

    def test_admin_bird_preview(self):
        """ Test if the birdpreview is displayed """
        self.setup_assign_breeders(self.pybudgie_user)
        self.setup_assign_users_bird_permissions(self.pybudgie_user)
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
        """ Test if user can attach a photo """
        self.setup_assign_breeders(self.pybudgie_user)
        self.setup_assign_users_bird_permissions(self.pybudgie_user)
        self.client.login(
            username=self.user_credentials["username"],
            password=self.user_credentials["password"],
        )

        photo_filename = "mooievogel_{}.png".format(datetime.datetime.now().timestamp())
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
