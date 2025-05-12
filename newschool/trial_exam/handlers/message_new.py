import logging
from datetime import UTC
from datetime import date
from datetime import datetime
from datetime import timedelta

from django.core.cache import cache
from django.db.models import Q
from vk_api.bot_longpoll import VkBotMessageEvent
from vk_api.utils import get_random_id
from vk_api.vk_api import VkApiMethod

from newschool.myclass.models import Student

# Импорт моделей
from newschool.myclass.models import Subject as Record
from newschool.trial_exam.keyboard import keyboard_choice_subjects
from newschool.trial_exam.keyboard import keyboard_main
from newschool.trial_exam.keyboard import keyboard_type_exam
from newschool.trial_exam.models import ExamConfig
from newschool.trial_exam.models import ExamRegistration
from newschool.trial_exam.models import ExamType
from newschool.trial_exam.models import MessageBot
from newschool.trial_exam.models import Subject
from newschool.trial_exam.statuses import Statuses


class HandlersMessagesNew:
    def __init__(self, vk: VkApiMethod, event: VkBotMessageEvent):
        self.user_id = event.obj.message["peer_id"]
        self.message = event.obj.message["text"]
        self.vk = vk
        self.event = event

    def _get_cache_user(self) -> dict | None:
        if not cache.has_key(self.user_id):
            cache.set(self.user_id, {}, timeout=300)
        return cache.get(self.user_id)

    def _get_user_url(self) -> str:
        user_info = self.vk.users.get(user_ids=self.user_id, fields="domain")
        if user_info and "domain" in user_info[0]:
            user_domain = user_info[0]["domain"]
            user_url = f"https://vk.com/{user_domain}"
        else:
            user_url = f"https://vk.com/id{self.user_id}"
        return user_url

    def _check_student(self):
        """
        Проверяет, зарегистрирован ли пользователь как студент.
        Если да, возвращает объект студента, иначе отправляет сообщение об ошибке
        и возвращает None.
        """
        user_url = self._get_user_url()
        try:
            student = Student.objects.get(vk_link=user_url)
            return student
        except Student.DoesNotExist:
            self._send_message(
                "Вы не зарегистрированы как студент. Если это не так, то напишите Нам",
                keyboard_main(),
            )
            return None

    def _get_aviable_subjects(self, type_exam: str) -> Subject:
        type_exam_instance = ExamType.objects.get(type=type_exam)
        user_link = self._get_user_url()
        all_active_subjects = Subject.objects.filter(
            is_active=True, types=type_exam_instance
        )
        records = Record.objects.filter(student__vk_link=user_link)

        if not records:
            return all_active_subjects

        query = Q()
        for record in records:
            query |= Q(name__icontains=record.subject)

        return (
            Subject.objects.filter(is_active=True)
            .filter(query)
            .filter(types=type_exam_instance)
            .distinct()
        )

    def _send_message(self, message, keyboard=None):
        return self.vk.messages.send(
            user_id=self.user_id,
            message=message,
            random_id=get_random_id(),
            keyboard=keyboard,
        )

    def _is_active(self):
        now = datetime.now(tz=UTC) + timedelta(hours=3)
        weekday_now = now.isoweekday()
        is_worked = ExamConfig.objects.filter(is_active=True)
        is_open = (
            ExamConfig.objects.filter(
                is_active=True,
                registration_open_day__lte=weekday_now,
                registration_close_day__gte=weekday_now,
            )
            .exclude(
                registration_open_day=weekday_now,
                registration_open_time__gt=now.time(),
            )
            .exclude(
                registration_close_day=weekday_now,
                registration_close_time__lt=now.time(),
            )
        )
        if not is_worked.exists():
            return (
                False,
                MessageBot.objects.get(title="Бот отключен").message
                if MessageBot.objects.exists(title="Бот отключен")
                else "Бот временно не работает. Обратитесь к администрации для установления причины остановки",
            )
        if not is_open.exists():
            return (
                False,
                MessageBot.objects.get(title="Регистрация закрыта").message
                if MessageBot.objects.exists(title="Регистрация закрыта")
                else "Регистрация закрыта",
            )
        return (True, True)

    def run_handler(self):
        student = self._check_student()
        if not student:
            cache_user = {}
            cache.set(self.user_id, cache_user, timeout=300)
            return

        cache_user: dict = self._get_cache_user()
        status = cache_user.get("status")

        match status, self.message:
            # Выбор типа экзамена для записи
            case None, "Записаться на пробные экзамены":
                cache_user["status"] = Statuses.CHOICE_TYPEP_EXAM.value
                self._send_message("Выберите тип экзамена", keyboard_type_exam())

            # Обработка выбора типа экзамена
            case Statuses.CHOICE_TYPEP_EXAM.value, "ОГЭ" | "ЕГЭ":
                cache_user["type_exam"] = self.message
                subjects = self._get_aviable_subjects(cache_user["type_exam"])
                keyboard = keyboard_choice_subjects(aviable_subjects=subjects)
                message_id = self._send_message(
                    "Выберите предметы, которые хотите сдать",
                    keyboard,
                )
                cache_user["message_id_for_choice_subjects"] = message_id
                cache_user["aviable_subjects"] = [subject.name for subject in subjects]
                cache_user["status"] = Statuses.CHOICE_SUBJECTS.value

            # Просмотр своей записи на пробный экзамен (только будущие записи)
            case None, "Посмотреть куда записан":
                student = self._check_student()
                if not student:
                    cache_user = {}
                    cache.set(self.user_id, cache_user, timeout=300)
                    return

                now = datetime.now(tz=UTC) + timedelta(hours=3)
                today = now.date()
                # Фильтруем будущие записи:
                registrations = ExamRegistration.objects.filter(user=student).filter(
                    Q(date__gt=today)
                    | Q(date=today, time_exam__start_exam__gt=now.time())
                )

                if registrations.exists():
                    message = "Ваша будущая запись на пробный экзамен:\n"
                    for reg in registrations:
                        weekday = (
                            reg.time_exam.weekday.name
                            if reg.time_exam.weekday
                            else "Неизвестный день"
                        )
                        time_exam_str = (
                            f"{reg.time_exam.start_exam.strftime('%H:%M')}-"
                            f"{reg.time_exam.end_exam.strftime('%H:%M')}"
                        )
                        message += (
                            f"Предмет: {reg.subject.name}, Дата: {reg.date.strftime('%d.%m.%Y')}, "
                            f"Время: {weekday} {time_exam_str}\n"
                        )
                    self._send_message(message, keyboard_main())
                else:
                    self._send_message(
                        "У вас нет будущих записей на пробный экзамен", keyboard_main()
                    )
                cache_user = {}

            # Удаление записи на пробный экзамен (только будущей)
            case None, "Удалить запись на пробный экзамен":
                student = self._check_student()
                if not student:
                    cache_user = {}
                    cache.set(self.user_id, cache_user, timeout=300)
                    return

                now = datetime.now(tz=UTC) + timedelta(hours=3)
                today = now.date()
                # Фильтруем будущие записи:
                registrations = ExamRegistration.objects.filter(user=student).filter(
                    Q(date__gt=today)
                    | Q(date=today, time_exam__start_exam__gt=now.time())
                )
                if not registrations.exists():
                    self._send_message(
                        "У вас нет будущих записей для удаления", keyboard_main()
                    )
                else:
                    registration = registrations.first()
                    registration.delete()
                    self._send_message(
                        "Ваша запись на пробный экзамен успешно удалена",
                        keyboard_main(),
                    )
                cache_user = {}

            # Кнопка "Отмена" – возвращаем основное меню.
            case _, "Отмена":
                self._send_message("Основное меню", keyboard_main())
                cache_user = {}

            # Остальные случаи – возвращаемся в главное меню.
            case _, _:
                self._send_message(
                    "Я тебя не понимаю, Возврат в главное меню", keyboard_main()
                )
                cache_user = {}

        cache.set(self.user_id, cache_user, timeout=300)
