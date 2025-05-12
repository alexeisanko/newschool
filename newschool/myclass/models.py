from django.db import models


class Student(models.Model):
    id_my_class = models.IntegerField(unique=True)
    vk_link = models.CharField(max_length=100, null=True)
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Subject(models.Model):
    id_my_class = models.IntegerField()
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.subject} ({self.student.name})"
