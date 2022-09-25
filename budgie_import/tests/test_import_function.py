import datetime
import glob
import os

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

import budgie_import.services.import_from_file
from budgie_bird.models import ColorProperty, Bird
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
        self.upload_filename = "test_test_import_excel_{}.csv".format(
            datetime.datetime.now().timestamp()
        )
        self.upload_file_path = (
            "{}/../budgie_import/fixtures/test_bird_data.xlsx".format(settings.BASE_DIR)
        )
        self.uploading = open(
            self.upload_file_path,
            "rb",
        ).read()
        self.uploaded_file = SimpleUploadedFile(self.upload_filename, self.uploading)

    def tearDown(self):
        for filename in glob.glob(
            "{}/test_test_import*".format(settings.BIRD_EXCELFILE_UPLOAD_LOCATION)
        ):
            os.remove(filename)

    def test_import_exception(self):
        """Test if the extension-exception is raised"""

        # Did the import throw an error?
        with self.assertRaises(Exception):
            budgie_import.services.import_from_file.import_from_file(
                "henk.txt", self.pybudgie_user
            )

    def test_color_import(self):
        """Test if self named colors are recognized during import"""

        ColorProperty.objects.create(
            user=self.pybudgie_user, color_name="Grijs", rank=1
        )
        budgie_import.services.import_from_file.import_from_file(
            self.upload_file_path, self.pybudgie_user
        )
        bird = Bird.objects.get(ring_number="5TJJ-81-2018")
        self.assertIn(
            "Grijs", bird.color_property.all().values_list("color_name", flat=True)
        )
