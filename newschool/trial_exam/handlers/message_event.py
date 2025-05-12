import logging
from datetime import UTC
from datetime import datetime
from datetime import timedelta
from typing import Any

from django.core.cache import cache
from django.db.models import Count
from django.db.models import F
from django.db.models import Q
from vk_api.bot_longpoll import VkBotMessageEvent
from vk_api.utils import get_random_id
from vk_api.vk_api import VkApiMethod

from newschool.myclass.models import Subject as Record
from newschool.trial_exam.keyboard import keyboard_choice_datetime
from newschool.trial_exam.keyboard import keyboard_choice_final
from newschool.trial_exam.keyboard import keyboard_choice_subjects
from newschool.trial_exam.keyboard import keyboard_main
from newschool.trial_exam.models import ExamConfig
from newschool.trial_exam.models import ExamSchedule
from newschool.trial_exam.models import ExamType
from newschool.trial_exam.models import MessageBot
from newschool.trial_exam.models import Subject
from newschool.trial_exam.statuses import Statuses


class HandlersCallbackEvent:
    def __init__(self, vk: VkApiMethod, event: VkBotMessageEvent):
        self.user_id = event.obj["peer_id"]
        self.callback_type = event.obj["payload"]["type"]
        self.vk = vk
        self.event = event

    def _get_cache_user(self) -> dict:
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

    def _get_aviable_subjects(self, type_exam: str) -> Any:
        type_exam = ExamType.objects.get(type=type_exam)
        user_link = self._get_user_url()
        all_active_subjects = Subject.objects.filter(is_active=True, types=type_exam)
        records = Record.objects.filter(student__vk_link=user_link)

        if not records:
            return all_active_subjects

        query = Q()
        for record in records:
            query |= Q(name__icontains=record.subject)

        return (
            Subject.objects.filter(is_active=True)
            .filter(query)
            .filter(types=type_exam)
            .distinct()
        )

    def _get_aviable_time(self) -> Any:
        today = datetime.now(tz=UTC)

        days_ahead_saturday = (5 - today.weekday()) % 7
        next_saturday_date = today + timedelta(days=days_ahead_saturday)

        days_ahead_sunday = (6 - today.weekday()) % 7
        next_sunday_date = today + timedelta(days=days_ahead_sunday)

        saturday_weekday = 6
        sunday_weekday = 7

        return ExamSchedule.objects.annotate(
            registration_count=Count(
                "examregistration",
                filter=Q(examregistration__date=next_saturday_date)
                & Q(weekday__name=saturday_weekday)
                | Q(examregistration__date=next_sunday_date)
                & Q(weekday__name=sunday_weekday),
            ),
        ).filter(registration_count__lt=F("available_slots"))

    def _send_message(self, message, keyboard=None):
        return self.vk.messages.send(
            user_id=self.user_id,
            message=message,
            random_id=get_random_id(),
            keyboard=keyboard,
        )

    def _edit_message(self, message_id, message="sfdds", keyboard=None):
        self.vk.messages.edit(
            peer_id=self.user_id,
            message_id=message_id,
            message=message,
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
                if MessageBot.objects.filter(title="Бот отключен").exists()
                else "Бот временно не работает. Обратитесь к администрации для установления причины остановки",
            )
        if not is_open.exists():
            return (
                False,
                MessageBot.objects.get(title="Регистрация закрыта").message
                if MessageBot.objects.filter(title="Регистрация закрыта").exists()
                else "Регистрация закрыта",
            )
        return (True, True)

    def run_handler(self):
        cache_user: dict = self._get_cache_user()
        status = cache_user.get("status")
        match status, self.callback_type:
            case Statuses.CHOICE_SUBJECTS.value, "subject_selection":
                # Обработка выбора предмета (уже реализовано)
                aviable_subjects = self._get_aviable_subjects(cache_user["type_exam"])
                event_subjects = Subject.objects.get(
                    id=self.event.obj["payload"]["subject_id"],
                ).name
                cache_user["selected_subjects"] = cache_user.get(
                    "selected_subjects", []
                )
                if event_subjects in cache_user["selected_subjects"]:
                    cache_user["selected_subjects"].remove(event_subjects)
                else:
                    cache_user["selected_subjects"].append(event_subjects)

                keyboard = keyboard_choice_subjects(
                    aviable_subjects=aviable_subjects,
                    selected_subjects=cache_user["selected_subjects"],
                )
                message_id = cache_user["message_id_for_choice_subjects"]
                self._edit_message(
                    message_id=message_id,
                    message="Когда выберите предметы которые хотите, нажимай «Выбраны»",
                    keyboard=keyboard,
                )
                cache.set(self.user_id, cache_user, timeout=300)

            case Statuses.CHOICE_SUBJECTS.value, "confirm_selection":
                # После подтверждения выбора предметов
                selected_subjects = cache_user.get("selected_subjects", [])
                if not selected_subjects:
                    self._send_message("Пожалуйста, выберите хотя бы один предмет.")
                    return

                # Инициализируем структуру для сохранения даты и времени для каждого предмета
                cache_user["selected_schedule"] = {}
                cache_user["current_subject_index"] = 0
                cache_user["status"] = Statuses.CHOICE_DATETIME.value

                # Отправляем сообщение с первым предметом и сохраняем его message_id
                available_schedules = self._get_aviable_time()
                current_subject = selected_subjects[0]
                first_message_id = self._send_message(
                    message=f"Выберите дату проведения экзамена для предмета {current_subject}",
                    keyboard=keyboard_choice_datetime(available_schedules),
                )
                cache_user["message_id_for_choice_datetime"] = first_message_id
                cache.set(self.user_id, cache_user, timeout=300)

            case Statuses.CHOICE_DATETIME.value, "date_selection":
                # Обработка выбора даты (нажатие на кнопку из inline-клавиатуры)
                schedule_id = self.event.obj["payload"]["schedule_id"]
                try:
                    chosen_schedule = ExamSchedule.objects.get(id=schedule_id)
                except ExamSchedule.DoesNotExist:
                    self._send_message(
                        "Выбранное расписание недоступно. Попробуйте ещё раз."
                    )
                    return

                current_index = cache_user["current_subject_index"]
                selected_subjects = cache_user["selected_subjects"]
                current_subject = selected_subjects[current_index]

                # Сохраняем выбор для текущего предмета
                cache_user.setdefault("selected_schedule", {})[current_subject] = {
                    "schedule_id": chosen_schedule.id
                }

                # Формируем словарь выбранных расписаний для отображения в клавиатуре:
                selected_mapping = {
                    data["schedule_id"]: subj
                    for subj, data in cache_user["selected_schedule"].items()
                }

                if current_index + 1 < len(selected_subjects):
                    # Если есть следующий предмет, обновляем сообщение (редактируем то же сообщение)
                    next_subject = selected_subjects[current_index + 1]
                    cache_user["current_subject_index"] = current_index + 1
                    available_schedules = self._get_aviable_time()
                    new_keyboard = keyboard_choice_datetime(
                        available_schedules, selected_schedules=selected_mapping
                    )
                    self._edit_message(
                        message_id=cache_user["message_id_for_choice_datetime"],
                        message=f"Выберите дату проведения экзамена для предмета {next_subject}",
                        keyboard=new_keyboard,
                    )
                else:
                    available_schedules = self._get_aviable_time()
                    new_keyboard = keyboard_choice_datetime(
                        available_schedules, selected_schedules=selected_mapping
                    )
                    self._edit_message(
                        message_id=cache_user["message_id_for_choice_datetime"],
                        message="Все предметы выбраны",
                        keyboard=new_keyboard,
                    )
                    # Если выбран последний предмет – выводим итоговое сообщение и новую клавиатуру с тремя кнопками:
                    summary = "Вы выбрали следующее время проведения экзаменов:\n"
                    for subj, sched_info in cache_user["selected_schedule"].items():
                        try:
                            schedule_obj = ExamSchedule.objects.get(
                                id=sched_info["schedule_id"]
                            )
                            time_info = sched_info.get("time_slot", "—")
                            summary += f"{subj}: {schedule_obj}\n"
                        except ExamSchedule.DoesNotExist:
                            continue

                    # Обновляем статус для финального выбора
                    cache_user["status"] = "final_selection"
                    cache.set(self.user_id, cache_user, timeout=300)

                    final_keyboard = (
                        keyboard_choice_final()
                    )  # новая клавиатура для финального выбора
                    self._send_message(message=summary, keyboard=final_keyboard)

                cache.set(self.user_id, cache_user, timeout=300)
            case "final_selection", "final_confirm":
                # Подтверждение выбора: выводим сообщение с итоговым расписанием и завершаем регистрацию
                summary = "Регистрация завершена. Вы выбрали следующие предметы и время проведения экзаменов:\n"
                for subj, sched_info in cache_user.get("selected_schedule", {}).items():
                    try:
                        schedule_obj = ExamSchedule.objects.get(
                            id=sched_info["schedule_id"]
                        )
                        time_info = sched_info.get("time_slot", "—")
                        summary += f"{subj}: {schedule_obj} Время: {time_info}\n"
                    except ExamSchedule.DoesNotExist:
                        continue
                self._send_message(message=summary, keyboard=keyboard_main())
                cache_user["status"] = Statuses.REGISTRATION_COMPLETE.value
                cache.set(self.user_id, cache_user, timeout=300)

            case "final_selection", "final_cancel":
                # Сброс состояния и возврат в главное меню
                cache.delete(self.user_id)
                self._send_message(
                    message="Регистрация отменена. Возвращаем вас в главное меню.",
                    keyboard=keyboard_main(),
                )

            case "final_selection", "final_reselect":
                # Возврат к выбору даты и времени для всех предметов
                cache_user["current_subject_index"] = 0
                cache_user["selected_schedule"] = {}
                available_schedules = self._get_aviable_time()
                current_subject = cache_user["selected_subjects"][0]
                self._edit_message(
                    message_id=cache_user["message_id_for_choice_datetime"],
                    message=f".",
                )
                first_message_id = self._send_message(
                    message=f"Выберите дату проведения экзамена для предмета {current_subject}",
                    keyboard=keyboard_choice_datetime(available_schedules),
                )
                cache_user["message_id_for_choice_datetime"] = first_message_id
                cache_user["status"] = Statuses.CHOICE_DATETIME.value
                cache.set(self.user_id, cache_user, timeout=300)
