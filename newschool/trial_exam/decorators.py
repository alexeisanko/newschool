import json

from vk_api.keyboard import VkKeyboard
from vk_api.keyboard import VkKeyboardColor


def add_cancel_button(func):
    def wrapper(*args, **kwargs):
        # Получаем JSON клавиатуры, вызвав оригинальную функцию
        keyboard_json = func(*args, **kwargs)

        # Загружаем данные JSON в словарь
        keyboard_data = json.loads(keyboard_json)

        # Создаем новый объект VkKeyboard
        vk_keyboard = VkKeyboard(one_time=keyboard_data.get("one_time", False))

        # Восстанавливаем кнопки из исходного JSON
        for line in keyboard_data["buttons"]:
            for button in line:
                action = button["action"]
                color = button.get("color", VkKeyboardColor.PRIMARY)
                vk_keyboard.add_button(action["label"], color=color)
            vk_keyboard.add_line()  # Добавляем новую строку после каждой линии кнопок

        # Добавляем кнопку "Отмена"
        vk_keyboard.add_button("Отмена", color=VkKeyboardColor.NEGATIVE)

        # Возвращаем клавиатуру в формате JSON
        return vk_keyboard.get_keyboard()

    return wrapper
