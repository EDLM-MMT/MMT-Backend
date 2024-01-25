from django.db import models

# Create your models here.


class AcademicCourseArea(models.Model):
    """Model to store academic course areas"""
    id = models.BigAutoField(primary_key=True)
    course_area = models.CharField(max_length=250)

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.course_area}'


class AcademicCourse(models.Model):
    """Model to store academic course detail"""
    id = models.BigAutoField(primary_key=True)
    course = models.CharField(max_length=250)
    academic_course_area = models.ForeignKey(AcademicCourseArea,
                                             on_delete=models.CASCADE,
                                             related_name="academic_"
                                             "course_set",
                                             help_text="Choose an academic "
                                             "area from academic course area",)

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.course}'


class AreasAndHour(models.Model):
    """Models to store areas and Hours related to courses"""
    id = models.BigAutoField(primary_key=True)
    academic_course_area = models.ForeignKey(AcademicCourseArea,
                                             on_delete=models.CASCADE,
                                             related_name="areas_and_"
                                             "hours_set",
                                             help_text="Choose an academic "
                                             "area from academic course area",
                                             )
    hours = models.DecimalField(max_digits=10, decimal_places=2,
                                help_text="Enter value in hours")

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.academic_course_area}  -  {self.hours} hour/s'


class Degree(models.Model):
    """Model to store degrees"""
    id = models.BigAutoField(primary_key=True)
    degree = models.CharField(max_length=250)
    area_and_hours = models.ForeignKey(AreasAndHour,
                                       on_delete=models.CASCADE,
                                       related_name="degree_set",
                                       help_text="Choose an academic "
                                       "area with duration")
 
    def __str__(self):
        """String for representing the Model object."""
        return f'{self.degree} - {self.area_and_hours}'


class AcademicInstitute(models.Model):
    """Model to store degree offerings"""
    id = models.BigAutoField(primary_key=True)
    institute = models.CharField(max_length=250)
    degrees = models.ManyToManyField(Degree,
                                     related_name="institute_set",
                                     help_text="Choose a degree offered")

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.institute}'


class MilitaryCourse(models.Model):
    """Model to store Military course details"""
    id = models.BigAutoField(primary_key=True)
    course = models.CharField(max_length=250)

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.course}'


class ACEMapping(models.Model):
    """Model to store mappings btw course areas and military courses"""
    id = models.BigAutoField(primary_key=True)
    academic_course_area = models.ForeignKey(AcademicCourseArea,
                                             on_delete=models.CASCADE,
                                             related_name="ace_area_set",
                                             help_text="Choose an academic "
                                             "area from academic course area",)
    military_courses = models.ManyToManyField(MilitaryCourse,
                                              related_name="ace_military_set",
                                              help_text="Choose military "
                                              "courses realted to "
                                              "the academic area")

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id}'
