import logging
from datetime import date
from datetime import datetime
from datetime import timedelta

from vk_api.keyboard import VkKeyboard
from vk_api.keyboard import VkKeyboardColor

from newschool.trial_exam.decorators import add_cancel_button
from newschool.trial_exam.models import ExamSchedule
from newschool.trial_exam.models import Subject


@add_cancel_button
def keyboard_type_exam():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("ОГЭ", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("ЕГЭ", color=VkKeyboardColor.POSITIVE)
    return keyboard.get_keyboard()


def keyboard_main():
    keyboard = VkKeyboard(one_time=False)
    # Кнопка для записи на пробные экзамены
    keyboard.add_button("Записаться на пробные экзамены", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()  # Перенос строки для разделения групп кнопок

    # Кнопка для просмотра своей записи на пробный экзамен
    keyboard.add_button("Посмотреть куда записан", color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()

    # Кнопка для удаления записи на пробный экзамен
    keyboard.add_button(
        "Удалить запись на пробный экзамен", color=VkKeyboardColor.NEGATIVE
    )

    return keyboard.get_keyboard()


def keyboard_choice_subjects(aviable_subjects: Subject, selected_subjects: list = []):
    keyboard = VkKeyboard(inline=True)
    column_count = 0
    max_column_count = 2

    for subject in aviable_subjects:
        if column_count >= max_column_count:
            keyboard.add_line()
            column_count = 0
        color = (
            VkKeyboardColor.POSITIVE
            if subject.name in selected_subjects
            else VkKeyboardColor.SECONDARY
        )
        payload = {"type": "subject_selection", "subject_id": subject.id}
        keyboard.add_callback_button(subject.name, color=color, payload=payload)
        column_count += 1

    if column_count == 0 and keyboard.lines:
        keyboard.lines.pop()
    keyboard.add_line()
    keyboard.add_callback_button(
        "Выбраны", color=VkKeyboardColor.PRIMARY, payload={"type": "confirm_selection"}
    )

    return keyboard.get_keyboard()


def keyboard_choice_datetime(schedules, selected_schedules=None):
    """
    Создает inline-клавиатуру для выбора даты экзамена.

    Аргументы:
        schedules (QuerySet[ExamSchedule]): доступные объекты расписания экзамена.
        selected_schedules (dict, опционально): если передан, должен быть словарем, где ключ – id расписания,
            а значение – название предмета, для которого этот слот уже выбран.
            Кнопки с такими расписаниями будут отображаться зелёным (VkKeyboardColor.POSITIVE)
            и callback payload будет пустым (то есть, нажатие не приводит к дальнейшей обработке).

    Размещает не более 1 кнопок в ряду.
    """
    keyboard = VkKeyboard(inline=True)
    max_buttons_per_row = 1
    buttons_in_current_row = 0

    if selected_schedules is None:
        selected_schedules = {}

    # Карта номеров дней недели на их названия на русском языке
    days = {
        1: "Понедельник",
        2: "Вторник",
        3: "Среда",
        4: "Четверг",
        5: "Пятница",
        6: "Суббота",
        7: "Воскресенье",
    }

    for schedule in schedules:
        if buttons_in_current_row >= max_buttons_per_row:
            keyboard.add_line()
            buttons_in_current_row = 0

        # Если schedule.weekday.name хранит номер дня (например, 1 для понедельника)
        if schedule.weekday and schedule.weekday.name:
            try:
                day_number = int(schedule.weekday.name)
                weekday_name = days.get(day_number, "Неизвестный")
            except ValueError:
                weekday_name = "Неизвестный"
        else:
            weekday_name = "Неизвестный"

        label = f"{weekday_name} ({schedule.start_exam.strftime('%H:%M')}-{schedule.end_exam.strftime('%H:%M')})"

        if schedule.id in selected_schedules:
            # Если расписание уже выбрано для какого-либо предмета, перекрашиваем кнопку в зелёный
            # и добавляем название предмета (payload пустой: кнопка неактивна)
            label = f"{label} - {selected_schedules[schedule.id]}"
            color = VkKeyboardColor.POSITIVE
            payload = {}
        else:
            color = VkKeyboardColor.PRIMARY
            payload = {"type": "date_selection", "schedule_id": schedule.id}

        keyboard.add_callback_button(label, color=color, payload=payload)
        buttons_in_current_row += 1

    if buttons_in_current_row == 0 and keyboard.lines:
        keyboard.lines.pop()

    return keyboard.get_keyboard()


def keyboard_choice_final():
    keyboard = VkKeyboard(inline=True)
    keyboard.add_callback_button(
        "Подтвердить", color=VkKeyboardColor.POSITIVE, payload={"type": "final_confirm"}
    )
    keyboard.add_callback_button(
        "Отменить", color=VkKeyboardColor.NEGATIVE, payload={"type": "final_cancel"}
    )
    keyboard.add_callback_button(
        "Выбрать время заного",
        color=VkKeyboardColor.PRIMARY,
        payload={"type": "final_reselect"},
    )
    return keyboard.get_keyboard()
