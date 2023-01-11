from typing import Any

from web_crawlers.SteamWebPage import SteamWebPage


class SteamWebCrawler:

    valid_cookies = 'sessionid', 'steamMachineAuth', 'steamLoginSecure', 'timezoneOffset'

    def __init__(self, steam_id: str, data: dict):
        self.__steam_id = steam_id
        self.__cookies: dict = {}
        self.__set_cookies(data)
        # self.__web_session = None  # it should be implemented later

    def interact(self, interaction_type: str, logged_in: bool = False, **kwargs) -> (int, Any):

        # checking if data is good
        if interaction_type not in SteamWebPage.page_interactions.keys():
            return 404, 'not implemented'

        concrete_web_page_reference = SteamWebPage.page_interactions[interaction_type]
        web_page = concrete_web_page_reference()

        required_data: list = web_page.required_user_data()
        for req_data in required_data:
            if req_data not in kwargs.keys():
                return 400, f'missing user data: {req_data}'

        # getting needed cookies
        cookies = {}

        if logged_in:
            if 'steamLoginSecure' in self.__cookies:
                cookies['steamLoginSecure'] = self.__cookies['steamLoginSecure']
            else:
                return 403, f'missing cookie: steamLoginSecure'

        for required_cookie in web_page.required_cookies():
            if required_cookie == 'steamMachineAuth':
                required_cookie = 'steamMachineAuth' + self.__steam_id
            if required_cookie not in self.__cookies.keys():
                return 403, f'missing cookie: {required_cookie}'
            cookies[required_cookie] = self.__cookies[required_cookie]

        # executing interaction
        try:
            result = web_page.interact(cookies, **kwargs)
            if result is None:
                return 200, result
            return result.status_code, result
        except Exception as e:
            return 500, e

    def __set_cookies(self, cookies_to_add: dict):
        for name, cookie in cookies_to_add.items():
            if name == 'steamMachineAuth':
                self.__cookies[name + self.__steam_id] = cookie
                continue
            if name in self.valid_cookies:
                self.__cookies[name] = cookie
