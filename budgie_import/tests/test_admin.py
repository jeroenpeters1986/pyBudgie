import datetime
import glob
import os

from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from budgie_bird.models import Breeder, Bird
from budgie_import.models import ImportFile
from budgie_user.models import BudgieUser


class ImportFileAdminTest(TestCase):
    importfile_overview_url = reverse("admin:budgie_import_importfile_changelist")
    add_file_url = reverse("admin:budgie_import_importfile_add")

    def setUp(self):
        self.user_credentials = {
            "username": "d.shrute",
            "password": "Monkey",
            "breeding_reg_nr": "Assistant to the DM-01",
            "email": "d.k.shrute@dundermifflin.com",
        }

        self.pybudgie_user = BudgieUser.objects.create_user(
            username=self.user_credentials["username"],
            password=self.user_credentials["password"],
            email=self.user_credentials["email"],
            breeding_reg_nr=self.user_credentials["breeding_reg_nr"],
            is_staff=True,
        )
        content_type_bird = ContentType.objects.get_for_model(Bird)
        content_type_breeder = ContentType.objects.get_for_model(Breeder)
        content_type_import = ContentType.objects.get_for_model(ImportFile)
        permissions = Permission.objects.filter(
            content_type__in=(
                content_type_bird,
                content_type_breeder,
                content_type_import,
            )
        )
        self.pybudgie_user.user_permissions.set(permissions)

    def tearDown(self):
        for filename in glob.glob(
            "{}/test_test_import*".format(settings.BIRD_PICTURE_UPLOAD_LOCATION)
        ):
            os.remove(filename)

    def test_admin_upload_excel_file(self):
        """Test if a user can upload an excel file in the admin"""
        self.client.login(
            username=self.user_credentials["username"],
            password=self.user_credentials["password"],
        )

        upload_filename = "test_test_import_excel_{}.xlsx".format(
            datetime.datetime.now().timestamp()
        )
        excel_file = open(
            "{}/../budgie_import/fixtures/test_bird_data.xlsx".format(
                settings.BASE_DIR
            ),
            "rb",
        ).read()
        uploadfile = SimpleUploadedFile(upload_filename, excel_file)

        import_form = {"import_file": uploadfile, "user": "1", "photo": uploadfile}

        response = self.client.post(self.add_file_url, import_form)
        self.assertEqual(response.status_code, 302)

        response = self.client.get(self.importfile_overview_url)
        self.assertContains(response, upload_filename)

        # Check for created birds
        # Normal bird
        self.assertTrue(
            Bird.objects.filter(
                user=self.pybudgie_user, ring_number="5TJJ-12-2018"
            ).exists()
        )
        # Created father, which was not in the regular import row
        self.assertTrue(
            Bird.objects.filter(
                user=self.pybudgie_user, ring_number="HD07-2014-80"
            ).exists()
        )
        # Created mother (same as above)
        self.assertTrue(
            Bird.objects.filter(
                user=self.pybudgie_user, ring_number="5TJJ-2014-ISA"
            ).exists()
        )
        self.assertEqual(Bird.objects.filter(user=self.pybudgie_user).count(), 7)
