def send_message(vk, user_id, message, keyboard=None):
    vk.messages.send(user_id=user_id, message=message, random_id=0, keyboard=keyboard)


def get_user_url(vk, user_id) -> str:
    user_info = vk.users.get(user_ids=user_id, fields="domain")
    if user_info and "domain" in user_info[0]:
        user_domain = user_info[0]["domain"]
        user_url = f"https://vk.com/{user_domain}"
    else:
        user_url = f"https://vk.com/id{user_id}"
    return user_url
