from django.test import TestCase
from django.urls import reverse

from budgie_bird.models import Breeder, Bird
from budgie_user.models import BudgieUser


class DocumentAdminFormTest(TestCase):
    fixtures = ["test_breeders.json"]

    def setUp(self):

        self.admin_credentials = {
            "username": "m.scott",
            "password": "RyanIsMyFriend",
            "first_name": "Micheal",
            "last_name": "Scott",
            "breeding_reg_nr": "DM-01",
            "email": "m.g.scott@dundermifflin.com",
        }

        self.pybudgie_admin = BudgieUser.objects.create_superuser(
            username=self.admin_credentials["username"],
            password=self.admin_credentials["password"],
            first_name=self.admin_credentials["first_name"],
            last_name=self.admin_credentials["last_name"],
            email=self.admin_credentials["email"],
        )
        self.pybudgie_user = BudgieUser.objects.create_user(
            username="d_schrute", breeding_reg_nr="DunderMifflin02", is_staff=True
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

    def test_admin_bird_add(self):

        # Update template breeders
        for breeder in Breeder.objects.all():
            breeder.user = self.pybudgie_admin
            breeder.save()

        self.client.login(
            username=self.admin_credentials["username"],
            password=self.admin_credentials["password"],
        )

        add_bird_url = reverse("admin:budgie_bird_bird_add")
        view_page = self.client.get(add_bird_url)
        self.assertEqual(view_page.status_code, 200)

        self.assertEqual(0, Bird.objects.count())

        new_bird = self.bird_data
        new_bird["user"] = self.pybudgie_admin.pk

        response = self.client.post(add_bird_url, self.bird_data)
        bird_overview_url = reverse("admin:budgie_bird_bird_changelist")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers["location"][1], bird_overview_url)

        bird = Bird.objects.get(ring_number=self.bird_data["ring_number"])
        self.assertIsInstance(bird, Bird)
        self.assertEqual(bird.user, self.pybudgie_admin)
        self.assertEqual(1, Bird.objects.count())
