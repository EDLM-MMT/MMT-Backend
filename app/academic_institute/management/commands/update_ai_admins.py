import os
import pathlib

import boto3
import pandas
from django.core.management.base import BaseCommand

from academic_institute.models import AcademicInstitute
from users.models import MMTUser


class Command(BaseCommand):
    """
    Django Command to update Academic Institute Admins
    """

    def retrieve_admin_list(self, file: pathlib.Path):
        """
        Get list of emails and associated AIs
        """
        if file.suffix == '.csv':
            data_frame = pandas.read_csv(file, usecols=['Name', 'Email'])
        else:
            data_frame = pandas.read_excel(file, usecols=['Name', 'Email'])
        return data_frame

    def format_admin_list(self, admin_list: pandas.DataFrame):
        """
        Change admin list to match the expected format

        FORMAT RETURNED
        dict_format = {
            "institute_name": ["email_addresses",]
        }
        """

        dict_ret = {}

        for row in admin_list.itertuples(index=False):
            if row.Name not in dict_ret:
                dict_ret[row.Name] = []
            dict_ret[row.Name].append(row.Email)

        return dict_ret

    def update_admin_access(self, admin_dict):
        """
        Update admin lists for AIs
        """
        admins = []
        # iterate over admin dict
        for institute_name in admin_dict:
            # create AI if it doesn't exist
            inst = AcademicInstitute.objects.get_or_create(
                institute=institute_name)[0]
            # if AI is managed by import (this process)
            if inst.managed_by_import:
                # remove all current admins
                inst.admins.user_set.clear()
                # iterate over email list
                for email in admin_dict[institute_name]:
                    # add user to admin group if user exists
                    if MMTUser.objects.filter(email=email).exists():
                        user = MMTUser.objects.get(email=email)
                        user.groups.add(inst.admins)
                        admins.append(user)
        return admins

    def handle(self, *args, **options):
        # check import dir exists
        import_dir = pathlib.Path().joinpath("/tmp", "imports")
        if not import_dir.exists():
            return f"Unable to access {import_dir.absolute()}"

        # connect to S3 if able
        bucket_name = os.getenv("S3_BUCKET_NAME")
        if bucket_name:
            s3 = boto3.resource('s3')
            try:
                objects = list(s3.Bucket(bucket_name).objects.all())
                print("Downloading objects in bucket:")
                # iterate items in bucket
                for obj in objects:
                    print(f"- {obj.key}")
                    # download file to import dir
                    with open(import_dir.joinpath(obj.key), 'wb') as f:
                        boto3.client('s3').download_fileobj(
                            bucket_name, obj.key, f)
            except Exception as e:
                print(f"Error accessing bucket: {e}")

        # iterate files and attempt import
        for file in import_dir.iterdir():
            try:
                admin_list = self.retrieve_admin_list(file)
                admin_dict = self.format_admin_list(admin_list)
                admin_users = self.update_admin_access(admin_dict)

                ais_imported = len(admin_dict)
                admins_updated = len(admin_users)

                print(f"{ais_imported} AI retrieved\n{admins_updated}" +
                      f" AI admins updated\nFrom {file}")
            except Exception:
                print(f"Issue with {file}")
            finally:
                # delete files so downloaded files aren't kept
                file.unlink(missing_ok=True)
