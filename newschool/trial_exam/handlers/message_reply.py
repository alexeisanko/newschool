from django.core.cache import cache
from vk_api.bot_longpoll import VkBotMessageEvent
from vk_api.vk_api import VkApiMethod

from newschool.trial_exam.statuses import Statuses


class HandlersMessagesReply:
    def __init__(self, vk: VkApiMethod, event: VkBotMessageEvent):
        self.user_id = event.obj["peer_id"]
        self.vk = vk
        self.message_id = event.obj["id"]
        self.message = event.obj["text"]

    def _get_cache_user(self) -> str | None:
        if not cache.has_key(self.user_id):
            cache.set(self.user_id, {}, timeout=300)
        return cache.get(self.user_id)

    def run_handler(self):
        cache_user: dict = self._get_cache_user()
        status = cache_user.get("status")
        match status, self.message:
            case (
                Statuses.CHOICE_SUBJECTS.value,
                "Выберите предметы которые хотите сдать",
            ):
                cache_user["message_id_for_choice_subjects"] = self.message_id
        cache.set(self.user_id, cache_user, timeout=300)
