import pathlib

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
            data_frame = pandas.read_csv(file)
        else:
            data_frame = pandas.read_excel(file)
        data_frame = data_frame.drop(columns=['FirstName', 'LastName',])
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
        for file in pathlib.Path("/mnt/imports").iterdir():
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
