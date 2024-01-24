from django.db import models
from django.urls import reverse

# Create your models here.


class AcademicCourseArea(models.Model):
    """Model to store academic course areas"""
    id = models.BigAutoField(primary_key=True)
    course_area = models.CharField(max_length=250)

    def get_absolute_url(self):
        """ URL for displaying individual model records."""
        return reverse('academic-course-area', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.course_area}'


class AcademicCourse(models.Model):
    """Model to store academic course detail"""
    id = models.BigAutoField(primary_key=True)
    courses = models.CharField(max_length=250)
    academic_course_areas = models.ForeignKey(AcademicCourseArea,
                                              on_delete=models.CASCADE)

    def get_absolute_url(self):
        """ URL for displaying individual model records."""
        return reverse('academic-courses', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id}'


class AreasAndHour(models.Model):
    """Models to store areas and Hours related to courses"""
    id = models.BigAutoField(primary_key=True)
    academic_areas = models.ForeignKey(AcademicCourseArea,
                                       on_delete=models.CASCADE)
    hours = models.IntegerField()

    def get_absolute_url(self):
        """ URL for displaying individual model records."""
        return reverse('areas-and-hour', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.academic_areas}  -  {self.hours} hour/s'


class Degree(models.Model):
    """Model to store degrees"""
    id = models.BigAutoField(primary_key=True)
    degree = models.CharField(max_length=250)
    areas_and_hours = models.ForeignKey(AreasAndHour,
                                        on_delete=models.CASCADE)

    def get_absolute_url(self):
        """ URL for displaying individual model records."""
        return reverse('degree', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.degree}'


class AcademicInstitute(models.Model):
    """Model to store degree offerings"""
    id = models.BigAutoField(primary_key=True)
    institute = models.CharField(max_length=250)
    degree_offered = models.ForeignKey(Degree,
                                       on_delete=models.CASCADE)

    def get_absolute_url(self):
        """ URL for displaying individual model records."""
        return reverse('academic-institute', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.institute}'


class MilitaryCourse(models.Model):
    """Model to store Military course details"""
    id = models.BigAutoField(primary_key=True)
    course = models.CharField(max_length=250)

    def get_absolute_url(self):
        """ URL for displaying individual model records."""
        return reverse('military-course', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.course}'


class ACEMapping(models.Model):
    """Model to store mappings btw course areas and military courses"""
    id = models.BigAutoField(primary_key=True)
    academic_course_areas = models.ForeignKey(AcademicCourseArea,
                                              on_delete=models.CASCADE)
    military_courses = models.ManyToManyField(MilitaryCourse)

    def get_absolute_url(self):
        """ URL for displaying individual model records."""
        return reverse('ACE-mapping', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id}'
