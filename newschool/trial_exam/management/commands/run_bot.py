import json
import logging

import vk_api
from django.conf import settings
from django.core.management.base import BaseCommand
from vk_api.bot_longpoll import VkBotEventType
from vk_api.bot_longpoll import VkBotLongPoll

from newschool.trial_exam.handlers.message_event import HandlersCallbackEvent
from newschool.trial_exam.handlers.message_new import HandlersMessagesNew
from newschool.trial_exam.handlers.message_reply import HandlersMessagesReply


class Command(BaseCommand):
    help = "Run VK bot"

    vk_session = vk_api.VkApi(token=settings.VK_GROUP_TOKEN)
    vk = vk_session.get_api()
    longpoll = VkBotLongPoll(vk_session, settings.VK_GROUP_ID)
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            logging.info("message new")
            logging.info(json.dumps(event.object, ensure_ascii=False, indent=2))
            handler = HandlersMessagesNew(vk, event)
            handler.run_handler()
        elif event.type == VkBotEventType.MESSAGE_EVENT:
            logging.info("message event")
            logging.info(json.dumps(event.object, ensure_ascii=False, indent=2))
            handler = HandlersCallbackEvent(vk, event)
            handler.run_handler()
        elif event.type == VkBotEventType.MESSAGE_REPLY:
            logging.info("Message reply")
            logging.info(json.dumps(event.object, ensure_ascii=False, indent=2))
            handler = HandlersMessagesReply(vk, event)
            handler.run_handler()
