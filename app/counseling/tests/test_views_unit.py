import json

from django.test import tag
from django.urls import reverse
from guardian.shortcuts import assign_perm
from rest_framework import status

from .test_setup import TestSetUp


@tag('unit')
class ViewTests(TestSetUp):

    def test_careerplan_requests_pass(self):
        """Test that making a get request to the career plan api with a
        correct id returns the career plan"""
        self.ur.save()
        self.cp.save()
        permission = 'counseling.view_careerplan'
        assign_perm(permission, self.user, self.cp)
        assign_perm(permission, self.user)

        url = self.cp.get_absolute_url()

        self.client.login(username=self.email,
                          password=self.password)
        response = self.client.get(url)
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.cp.degree_start_date.isoformat(),
                         responseDict['degree_start_date'])
        self.assertEqual(self.cp.expected_graduation_date.isoformat(),
                         responseDict['expected_graduation_date'])
        self.assertEqual(self.cp.owner.email,
                         responseDict['owner'])

    def test_careerplan_requests_create(self):
        """Test that making a post request to the career plan api with a
        correct data creates a career plan"""
        self.ur.save()
        self.user.eso_default = self.user
        self.user.save()
        self.institute.save()
        self.degree.save()
        data = {
            'degree': {
                'degree': self.degree.degree,
                'institute': self.institute.institute
            },
            'academic_institute': self.institute.institute,
            'degree_start_date': self.cp.degree_start_date.isoformat(),
            'expected_graduation_date': self.cp.degree_start_date.isoformat()
        }
        # self.cp.save()
        permission = 'counseling.add_careerplan'
        assign_perm(permission, self.user)

        url = reverse('counseling:career-plan-list')

        self.client.login(username=self.email,
                          password=self.password)
        response = self.client.post(url, data, format='json')
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.cp.degree_start_date.isoformat(),
                         responseDict['degree_start_date'])
        self.assertEqual(self.cp.expected_graduation_date.isoformat(),
                         responseDict['expected_graduation_date'])
        self.assertEqual(self.cp.owner.email,
                         responseDict['owner'])
