from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse
from model_utils import Choices
from model_utils.models import StatusModel, TimeStampedModel

from academic_institute.models import AcademicInstitute
from users.models import MOS, MMTUser, UserRecord

from .regex import REGEX_CHECK, REGEX_ERROR_MESSAGE

# Create your models here.


class AcademicCourseArea(models.Model):
    """Model to store academic course areas"""
    id = models.BigAutoField(primary_key=True)
    course_area = models.CharField(max_length=500, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])

    def __str__(self):
        """String for representing the Model object."""
        if hasattr(self, 'academiccourse'):
            return str(self.academiccourse)
        return f'{self.course_area}'


class AcademicCourse(AcademicCourseArea):
    """Model to store academic course detail"""
    name = models.CharField(max_length=500, help_text="Set course name",
                            validators=[
                                RegexValidator(
                                    regex=REGEX_CHECK,
                                    message=REGEX_ERROR_MESSAGE),
                            ])
    code = models.CharField(max_length=200, help_text="Set course code",
                            validators=[
                                RegexValidator(
                                    regex=REGEX_CHECK,
                                    message=REGEX_ERROR_MESSAGE),
                            ])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.code} - {self.name} - {self.course_area}'


class AreasAndHour(models.Model):
    """Models to store areas and Hours related to courses"""
    id = models.BigAutoField(primary_key=True)
    academic_course_area = models.ForeignKey(AcademicCourseArea,
                                             on_delete=models.CASCADE,
                                             related_name="areas_and_"
                                             "hours",
                                             help_text="Choose an academic "
                                             "area from academic course area",
                                             )
    degree = models.ForeignKey("Degree", related_name="areas_and_hours",
                               on_delete=models.CASCADE,
                               help_text="Choose the relevant degree",
                               blank=True, null=True)
    military_course = models.ForeignKey("MilitaryExperience",
                                        related_name="areas_and_hours",
                                        on_delete=models.CASCADE,
                                        help_text="Choose the relevant"
                                        " military course",
                                        blank=True, null=True)
    hours = models.PositiveIntegerField()
    level = models.CharField(max_length=3, blank=True, null=True, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.academic_course_area}  -  {self.hours} hour/s'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['academic_course_area',
                        'degree',
                        'military_course'],
                name='unique_connection'),
            models.CheckConstraint(
                check=Q(degree=None) | Q(military_course=None),
                name='only_degree_or_mc'),
        ]


class Degree(models.Model):
    """Model to store degrees"""
    id = models.BigAutoField(primary_key=True)
    degree = models.CharField(max_length=500, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    institute = models.ForeignKey(
        AcademicInstitute, related_name="degrees", on_delete=models.CASCADE,
        help_text="Choose the affiliated Academic Institute")
    mos = models.ManyToManyField(
        MOS, related_name='degrees', help_text="Select valid MOS", blank=True)
    areas = models.ManyToManyField(
        AcademicCourseArea, related_name="degrees", through=AreasAndHour)

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.degree} - {self.institute}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['institute',
                        'degree',],
                name='unique_degrees'),
        ]


class MilitaryExperience(models.Model):
    """Model to store academic course areas"""
    id = models.BigAutoField(primary_key=True)
    user_id = \
        models.ManyToManyField(
            UserRecord,
            max_length=250, blank=True, through="MilitaryCourse_User")
    experience_id = models.CharField(max_length=500, unique=True, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    experience_name = models.CharField(max_length=500, blank=True, null=True,
                                       validators=[
                                           RegexValidator(
                                               regex=REGEX_CHECK,
                                               message=REGEX_ERROR_MESSAGE
                                           ),
                                       ])
    ACE_identifier = models.CharField(max_length=250, default="None Assigned",
                                      validators=[
                                          RegexValidator(
                                              regex=REGEX_CHECK,
                                              message=REGEX_ERROR_MESSAGE
                                          ),
                                      ])
    description = models.TextField(null=True, blank=True, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    rank = models.CharField(max_length=500, null=True, blank=True, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    rank_level = models.CharField(max_length=500, null=True, blank=True,
                                  validators=[
                                      RegexValidator(
                                          regex=REGEX_CHECK,
                                          message=REGEX_ERROR_MESSAGE),
                                  ])
    areas = models.ManyToManyField(
        AcademicCourseArea, related_name="mappings", through=AreasAndHour)

    def determine_experience_type(self):
        if hasattr(self, 'militarycourse') and \
                hasattr(self.militarycourse, 'militarytestresult'):
            return self.militarycourse.militarytestresult.test_type
        if hasattr(self, 'militarycourse'):
            return 'Course'
        return 'Occupation'

    def __str__(self):
        """String for representing the Model object."""
        if hasattr(self, 'militarycourse'):
            return str(self.militarycourse)
        return f'{self.experience_name}'


class MilitaryCourse(MilitaryExperience):
    """Model to store Military course details"""
    course_name = models.CharField(max_length=500, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])

    def __str__(self):
        """String for representing the Model object."""
        if hasattr(self, 'militarytestresult'):
            return str(self.militarytestresult)
        return f'{self.course_name}'


class MilitaryTestResult(MilitaryCourse):
    """Model to store Military Test Results details"""
    TEST_TYPES = Choices("DSST", "CLEP")
    test_type = models.CharField(max_length=10, choices=TEST_TYPES)
    hours = models.CharField(max_length=10, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    passing = models.IntegerField()

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.test_type} - {self.course_name}'


class MilitaryCourse_User(TimeStampedModel):
    """Model to store User and Military course through details"""
    course_id = models.ForeignKey(MilitaryExperience,
                                  related_name="militarycourse_user",
                                  on_delete=models.CASCADE,
                                  help_text="Choose the relevant"
                                  " military course")
    user_id = models.ForeignKey(UserRecord, related_name="militarycourse_user",
                                on_delete=models.CASCADE, max_length=250,
                                blank=True)
    start_date = models.DateField(
        null=True, blank=True,
        help_text="Set degree start date month and year, January 2050")
    end_date = models.DateField(
        null=True, blank=True,
        help_text="Set degree start date month and year, January 2050")
    score = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Military Course User"

    def get_absolute_url(self):
        """ URL for displaying individual model records."""
        if hasattr(self.course_id, 'militarycourse') and \
                hasattr(self.course_id.militarycourse, 'militarytestresult'):
            return reverse('generate_transcript:additional-updates-detail',
                           args=[str(self.pk)])
        if hasattr(self.course_id, 'militarycourse'):
            return reverse('generate_transcript:course-updates-detail',
                           args=[str(self.pk)])
        return reverse('generate_transcript:occupation-updates-detail',
                       args=[str(self.pk)])


class Transcript(models.Model):
    """Model to track Transcript access permissions"""
    id = models.BigAutoField(primary_key=True)
    subject = models.OneToOneField(UserRecord, on_delete=models.CASCADE)

    def get_absolute_url(self):
        """ URL for displaying individual model records."""
        return reverse('generate_transcript:transcript-detail',
                       args=[str(self.pk)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.subject}'


class TranscriptStatus(StatusModel, TimeStampedModel):
    """Model to track Transcript status"""

    STATUS = Choices('Pending', 'Delivered', 'Opened', 'Downloaded')

    transcript = models.ForeignKey(Transcript, on_delete=models.CASCADE)
    recipient = models.ForeignKey(MMTUser, related_name='transcript_status',
                                  on_delete=models.CASCADE, blank=True,
                                  null=True, help_text="Select associated "
                                  "email address")
    academic_institute = models.ForeignKey(AcademicInstitute,
                                           related_name='transcript_status',
                                           on_delete=models.CASCADE,
                                           blank=True, null=True,
                                           help_text="Select associated "
                                           "academic institute")

    def get_absolute_url(self):
        """ URL for displaying individual model records."""
        return reverse('generate_transcript:transcript-status-detail',
                       args=[str(self.pk)])

    class Meta:
        verbose_name_plural = 'Transcript Status'
