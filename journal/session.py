import requests


class Session(object):
    def __init__(
        self,
        base_url: str,
        is_json: bool = False,
        default_headers: dict = None,
        default_params: dict = None,
    ):
        self.base_url = base_url
        self.is_json = is_json

        self.default_headers = default_headers
        self.default_params = default_params

        headers = {"User-Agent": "Journal/1.0"}

        if self.default_headers is not None:
            headers.update(default_headers)

        self.session = requests.Session()
        self.session.headers.update(headers)

    def set_authorization(self, authorization):
        raise NotImplementedError

    def fetch(self, method: str = "GET", endpoint: str = "", **kwargs):
        if method == "GET":
            if kwargs.get("params"):
                kwargs["params"].update(self.default_params)

        func = getattr(self.session, method.lower())

        if not func:
            raise Exception(f"Invalid method `{method}` given.")

        resp = self.session.get(self.base_url + endpoint, **kwargs)

        if self.is_json:
            return resp.json()

        return resp.text
