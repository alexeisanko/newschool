from django.db import models


class ExamType(models.Model):
    EXAM_CHOICES = [
        ("ЕГЭ", "ЕГЭ"),
        ("ОГЭ", "ОГЭ"),
    ]
    type = models.CharField(
        max_length=3,
        choices=EXAM_CHOICES,
        verbose_name="Тип экзамена",
    )

    def __str__(self):
        return self.get_type_display()


class Subject(models.Model):
    name = models.CharField(max_length=100, verbose_name="Наименование предмета")
    genitive_name = models.CharField(
        max_length=100,
        verbose_name="Имя в родительном падеже",
    )
    is_active = models.BooleanField(default=True, verbose_name="Статус")
    types = models.ManyToManyField(
        ExamType,
        related_name="subjects",
        verbose_name="Тип экзамена",
    )

    def __str__(self):
        return self.name


class WeekDay(models.Model):
    name = models.CharField(max_length=10, verbose_name="День недели")

    def __str__(self):
        return self.name


class ExamSchedule(models.Model):
    weekday = models.ForeignKey(
        WeekDay,
        on_delete=models.CASCADE,
        verbose_name="День недели",
    )
    start_exam = models.TimeField(verbose_name="Начало проведения")
    end_exam = models.TimeField(verbose_name="Окончание экзамена")
    available_slots = models.PositiveIntegerField(
        verbose_name="Количество свободных мест",
    )

    def __str__(self):
        return f"{self.weekday}: {self.start_exam}-{self.end_exam}"


class ExamRegistration(models.Model):
    user = models.ForeignKey("myclass.Student", on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField(verbose_name="Дата провдения")
    time_exam = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} ({self.date})"


class ExamConfig(models.Model):
    is_active = models.BooleanField(verbose_name="Регистрация активна?")
    registration_open_day = models.IntegerField(
        verbose_name="День недели открытия регистрации (1..7)",
    )
    registration_open_time = models.TimeField(verbose_name="Вермя открытия регистрации")
    registration_close_day = models.IntegerField(
        verbose_name="День недели окончания регистрации (1..7)",
    )
    registration_close_time = models.TimeField(
        verbose_name="Вермя окончания регистрации",
    )


class MessageBot(models.Model):
    title = models.CharField(verbose_name="Название сообщение", max_length=50)
    message = models.TextField(verbose_name="Сообщение")
