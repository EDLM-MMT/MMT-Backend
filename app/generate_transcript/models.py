from django.contrib.auth.models import Group
from django.db import models
from django.db.models import Q
from django.urls import reverse
from users.models import MOS, MMTUser, UserRecord

# Create your models here.


class AcademicCourseArea(models.Model):
    """Model to store academic course areas"""
    id = models.BigAutoField(primary_key=True)
    course_area = models.CharField(max_length=500)

    def __str__(self):
        """String for representing the Model object."""
        if self.academiccourse:
            return f'{self.academiccourse.code} - {self.academiccourse.name}'\
                f' - {self.course_area}'
        return f'{self.course_area}'


class AcademicCourse(AcademicCourseArea):
    """Model to store academic course detail"""
    name = models.CharField(max_length=500, help_text="Set course name")
    code = models.CharField(max_length=200, help_text="Set course code")

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
    military_course = models.ForeignKey("MilitaryCourse",
                                        related_name="areas_and_hours",
                                        on_delete=models.CASCADE,
                                        help_text="Choose the relevant"
                                        " military course",
                                        blank=True, null=True)
    hours = models.PositiveIntegerField()

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


class AcademicInstitute(models.Model):
    """Model to store degree offerings"""
    id = models.BigAutoField(primary_key=True)
    institute = models.CharField(max_length=500, unique=True)
    group = models.ForeignKey(Group, related_name='academic_institutes',
                              on_delete=models.SET_NULL,
                              null=True, blank=True,
                              help_text="Select the group that will manage "
                              "requests for this Institute")
    # Groups - for tracking who has access

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.institute}'


class Degree(models.Model):
    """Model to store degrees"""
    id = models.BigAutoField(primary_key=True)
    degree = models.CharField(max_length=500)
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


class MilitaryCourse(models.Model):
    """Model to store Military course details"""
    id = models.BigAutoField(primary_key=True)
    user_id = \
        models.ManyToManyField(
            UserRecord, "military_course",
            max_length=250, blank=True)
    course_id = models.CharField(max_length=250, unique=True)
    areas = models.ManyToManyField(
        AcademicCourseArea, related_name="mappings", through=AreasAndHour)

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.course_id}'


class Transcript(models.Model):
    """Model to track Transcript access permissions"""
    id = models.BigAutoField(primary_key=True)
    subject = models.OneToOneField(UserRecord, on_delete=models.CASCADE)
    recipient = models.ManyToManyField(MMTUser, blank=True,
                                       through='TranscriptStatus')

    def get_absolute_url(self):
        """ URL for displaying individual model records."""
        return reverse('transcript', args=[str(self.subject.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.subject}'


class TranscriptStatus(models.Model):
    """Model to track Transcript status"""
    STATUS_CHOICES = [
        ('Pending','Pending'),
        ('Delivered', 'Delivered'),
        ('Opened', 'Opened'),
        ('Downloaded', 'Downloaded'),
    ]

    transcript = models.ForeignKey(Transcript, on_delete=models.CASCADE)
    recipient = models.ForeignKey(MMTUser, on_delete=models.CASCADE)
    status = models.CharField(max_length=250, choices=STATUS_CHOICES,
                              default="Pending")
    status_update = models.DateTimeField(auto_now_add=True)

    class Meta:  
        verbose_name_plural = 'Transcript Status'