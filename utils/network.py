import sys
import threading

# in the browser build (pygbag/emscripten) there are no real threads, and the
# backend only speaks plain http without CORS, which an https page can't reach
IS_WEB = sys.platform == "emscripten"
if not IS_WEB:
    import requests

# status code used when the backend can't be reached at all
UNAVAILABLE = 503


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
        "register": Response(),
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

    def _start_worker(self, target, args):
        if IS_WEB:
            # online features are unavailable in the browser, fail right away
            response = Response()
            response.status_code = UNAVAILABLE
            self._cache[args[1]] = response
            return
        threading.Thread(target=target, args=args, daemon=True).start()

    def fetch_global_highscores(self):
        # clear response from cache
        self._cache["global_highscores"] = Response()

        # perform the global highscores get request
        self._start_worker(
            self._requests_get_worker,
            (self._GLOBAL_HIGHSCORES_URL, "global_highscores"),
        )
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
        self._start_worker(self._requests_get_worker, (url, "local_highscores"))
        return {"result": True, "status": None}

    def get_local_highscores(self):
        return self._cache["local_highscores"]

    def perform_register(self, username, password, email):
        # clear response from cache
        self._cache["register"] = Response()

        # perform the register post request
        url = self._REGISTER_URL
        params = {"username": username, "password": password, "email": email}
        self._start_worker(self._requests_post_worker, (url, "register", params))

    def get_register_status(self):
        return self._cache["register"]

    def perform_login(self, username, password):
        # clear response from cache
        self._cache["login"] = Response()

        # perform the login post request
        url = self._LOGIN_URL
        params = {"username": username, "password": password}
        self._start_worker(self._requests_post_worker, (url, "login", params))

    def get_login_result(self):
        return self._cache["login"]

    def _requests_get_worker(self, url, key):
        # fetch the response
        try:
            result = requests.get(url, timeout=10)
        except requests.RequestException as e:
            print(e)
            response = Response()
            response.status_code = UNAVAILABLE
            self._cache[key] = response
            return
        response = Response()
        response.status_code = result.status_code
        if response.status_code == 200:
            response.data = result.json()

        # copy the response object into the _cache
        self._cache[key] = response

    def _requests_post_worker(self, url, key, params):
        # perform the post request
        try:
            result = requests.post(url, params, timeout=10)
        except requests.RequestException as e:
            print(e)
            response = Response()
            response.status_code = UNAVAILABLE
            self._cache[key] = response
            return
        print(result)
        response = Response()
        response.status_code = result.status_code
        if response.status_code == 200:
            response.data = result.json()
            print(response.data)

        # copy the response object into the _cache
        self._cache[key] = response
