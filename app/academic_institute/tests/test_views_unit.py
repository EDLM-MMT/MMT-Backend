from django.test import tag
from django.urls import reverse
from guardian.shortcuts import assign_perm

from academic_institute.models import AcademicInstitute
from users.models import MMTUser

from .test_setup import TestSetUp


@tag('unit')
class ViewsTests(TestSetUp):
    def test_partial_update_manage_ai(self):
        add_email = 'added_user@example.com'
        add = MMTUser.objects.create_user(
            password=self.password, email=add_email)
        self.ur.save()
        self.institute.save()
        permission = 'academic_institute.change_academicinstitute'
        assign_perm(permission, self.user)
        self.institute.group.user_set.add(self.user)
        self.institute.admins.user_set.add(self.user)

        data = {
            'members': [
                {
                    'email': add_email,
                    'position': 'tester'
                }
            ]
        }
        url = reverse('academic_institute:manage-academic-institute-detail',
                      args=[self.institute.id])

        self.client.login(username=self.email,
                          password=self.password)
        response = self.client.patch(
            url, data, format='json')

        self.assertEqual(
            response.status_code//100, 2)
        self.assertEqual(
            AcademicInstitute.objects.count(), 1)
        self.assertEqual(
            AcademicInstitute.objects.first().group.user_set.count(), 2)
        self.assertIn(
            add, AcademicInstitute.objects.first().group.user_set.all())
        self.assertIn(
            self.user, AcademicInstitute.objects.first().group.user_set.all())
        self.assertEqual(len(response.json()['members']), 2)
