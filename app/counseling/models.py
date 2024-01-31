from django.db import models
from model_utils.models import TimeStampedModel

from generate_transcript.models import (AcademicCourse, AcademicInstitute,
                                        Degree)
from users.models import MMTUser, UserRecord


# Create your models here.
class CareerPlan(models.Model):
    owner = models.ForeignKey(UserRecord, related_name='career_plan',
                              on_delete=models.CASCADE,
                              help_text="Set owner/subject of plan")
    eso = models.ForeignKey(MMTUser, related_name='counseling_plans',
                            on_delete=models.SET_NULL, blank=True, null=True,
                            help_text="Set ESO for plan")
    degree = models.ForeignKey(Degree, related_name='plans',
                               on_delete=models.SET_NULL, blank=True,
                               null=True, help_text="Select associated degree")
    academic_institute = models.ForeignKey(AcademicInstitute,
                                           related_name='plans',
                                           on_delete=models.SET_NULL,
                                           blank=True, null=True,
                                           help_text="Select associated "
                                           "academic institute")
    degree_start_date = models.DateField(
        help_text="Set degree start date month and year, January 2050")
    expected_graduation_date = models.DateField(
        help_text="Set expected degree end date month and year, January 2050")


class Comment(TimeStampedModel):
    comment = models.TextField(editable=False, help_text="Set comment text")
    plan = models.ForeignKey(CareerPlan, related_name='comments',
                             on_delete=models.CASCADE,
                             help_text="Select associated plan")
    poster = models.ForeignKey(MMTUser, related_name='counseling_comments',
                               on_delete=models.SET_NULL, blank=True,
                               null=True, help_text="Select comment poster")

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.comment}'


class CoursePlan(models.Model):
    course = models.ForeignKey(AcademicCourse,
                               related_name='attendance_plans',
                               on_delete=models.CASCADE,
                               help_text="Select associated course")
    plan = models.ForeignKey(CareerPlan, related_name='courses',
                             on_delete=models.CASCADE,
                             help_text="Select associated plan")
    required = models.BooleanField(default=False,
                                   help_text="Set required status")
    approved = models.BooleanField(default=False,
                                   help_text="Set approved status")
    expected_semester = models.DateField(
        help_text="Set expected semester date month and year, January 2050")
