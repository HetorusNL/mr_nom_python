import asyncio
import json
import sys
import threading

# in the browser build (pygbag/emscripten) there are no threads and no
# requests library, the browser's fetch is used instead (see _web_worker)
IS_WEB = sys.platform == "emscripten"
if IS_WEB:
    import platform
else:
    import requests

# javascript helper for the browser build: performs the request and resolves
# to a JSON string {status, body}, so only a plain string crosses to python
_JS_FETCH_HELPER = """
window.mrNomFetch = (url, method, body) => fetch(url, method === "POST" ? {
    method: "POST",
    body: body,
    // the server parses the body as JSON regardless of the content type, and
    // text/plain avoids a CORS preflight request (not handled by the proxy)
    headers: {"Content-Type": "text/plain"},
} : {})
    .then(async (r) => JSON.stringify({status: r.status, body: await r.text()}))
    .catch((e) => JSON.stringify({status: 503, body: String(e)}));
"""

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
        "post_highscore": Response(),
        "access_token": None,
        "username": None,
    }

    # url related constants
    _BASE_URL = "https://mr-nom-server-python.hetorus.nl"
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
            # args is (url, key) for GET and (url, key, params) for POST
            asyncio.get_event_loop().create_task(self._web_worker(*args))
            return
        threading.Thread(target=target, args=args, daemon=True).start()

    async def _web_worker(self, url, key, params=None):
        if not getattr(platform.window, "mrNomFetch", None):
            platform.window.eval(_JS_FETCH_HELPER)
        method = "GET" if params is None else "POST"
        body = "" if params is None else json.dumps(params)
        response = Response()
        try:
            # platform.jsprom is broken in pygbag 0.9.3, so convert the
            # promise to an iterator and await that (which jsprom would do)
            promise = platform.window.mrNomFetch(url, method, body)
            raw = await platform.jsiter(platform.window.iterator(promise))
            result = json.loads(raw)
            response.status_code = result["status"]
            if response.status_code == 200:
                response.data = json.loads(result["body"])
        except Exception as e:
            print("request failed:", e)
            response.status_code = UNAVAILABLE

        # copy the response object into the _cache
        self._cache[key] = response

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

    def post_highscore(self, score, time_ms):
        if not self._cache["access_token"]:
            return False

        # clear response from cache
        self._cache["post_highscore"] = Response()

        # perform the post highscore request
        url = self._POST_HIGHSCORE_URL.format(self._cache["access_token"])
        params = {"score": score, "time": time_ms}
        self._start_worker(
            self._requests_post_worker, (url, "post_highscore", params)
        )
        return True

    def get_post_highscore_result(self):
        return self._cache["post_highscore"]

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
            result = requests.post(url, json=params, timeout=10)
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
