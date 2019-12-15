import requests
import threading


class Borg(object):
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class Response(object):
    def __init__(self):
        self.data = None
        self.status_code = 0


# the Borg pattern is used to ensure there is only 1 network "state"
class Network(Borg):
    _cache = {
        "global_highscores": Response(),
        "local_highscores": Response(),
        "login": Response(),
        "access_token": None,
        "username": None,
    }

    # url related constants
    _BASE_URL = "http://hetorus.nl:1338"
    _GLOBAL_HIGHSCORES_URL = _BASE_URL + "/highscores/global"
    _PERSONAL_HIGHSCORES_URL = _BASE_URL + "/highscores/local?accessToken={}"
    _POST_HIGHSCORE_URL = _BASE_URL + "/highscores?accessToken={}"
    _POST_FCM_TOKEN_URL = _BASE_URL + "/fcm_registration_token?accessToken={}"
    _REGISTER_URL = _BASE_URL + "/register"
    _LOGIN_URL = _BASE_URL + "/login"

    def __init__(self):
        Borg.__init__(self)

    def fetch_global_highscores(self):
        # clear response from cache
        self._cache["global_highscores"] = Response()

        # perform the global highscores get request
        threading.Thread(
            target=self._requests_get_worker,
            args=(self._GLOBAL_HIGHSCORES_URL, "global_highscores"),
        ).start()
        return {"result": True, "status": None}

    def get_global_highscores(self):
        return self._cache["global_highscores"]

    def fetch_local_highscores(self):
        if not self._cache["access_token"]:
            self._cache["local_highscores"].status_code = 400
            return {"result": False, "status": "not logged in!"}

        # clear response from cache
        self._cache["local_highscores"] = Response()

        # perform the global highscores get request
        url = self._PERSONAL_HIGHSCORES_URL.format(self._cache["access_token"])
        threading.Thread(
            target=self._requests_get_worker, args=(url, "local_highscores")
        ).start()
        return {"result": True, "status": None}

    def get_local_highscores(self):
        return self._cache["local_highscores"]

    def perform_login(self, username, password):
        # clear response from cache
        self._cache["login"] = Response()

        # perform the login post request
        url = self._LOGIN_URL
        params = {"username": username, "password": password}
        threading.Thread(
            target=self._requests_post_worker, args=(url, "login", params)
        ).start()

    def get_login_result(self):
        return self._cache["login"]

    def _requests_get_worker(self, url, key):
        # fetch the response
        result = requests.get(url)
        response = Response()
        response.status_code = result.status_code
        if response.status_code == 200:
            response.data = result.json()

            # copy the response object into the _cache
            self._cache[key] = response

    def _requests_post_worker(self, url, key, params):
        # perform the post request
        result = requests.post(url, params)
        print(result)
        response = Response()
        response.status_code = result.status_code
        if response.status_code == 200:
            response.data = result.json()
            print(response.data)

        # copy the response object into the _cache
        self._cache[key] = response
