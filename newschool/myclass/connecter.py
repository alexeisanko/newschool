import requests
from django.conf import settings


class MyClassConnecter:
    def __init__(self) -> None:
        self.apikey = settings.MYCLASS_API_KEY

    def _get_token(self) -> str:
        response = requests.post(
            "https://api.moyklass.com/v1/company/auth/getToken",
            data={"apiKey": self.apikey},
            timeout=10,
        ).json()

        return response["accessToken"]

    def _revoke_token(self, token: str) -> None:
        requests.post(
            "https://api.moyklass.com/v1/company/auth/revokeToken",
            data={"apiKey": self.apikey},
            timeout=10,
            headers={"x-access-token": token},
        )

    def request_to_my_class(self, method: str, path: str, params: dict):
        token = self._get_token()
        response = requests.request(
            method,
            f"https://api.moyklass.com/v1/{path}",
            timeout=10,
            headers={"x-access-token": token},
            params=params,
        )
        self._revoke_token(token)
        return response.json()
