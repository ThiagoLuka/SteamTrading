import requests
from typing import Union

from .SteamWebPage import SteamWebPage


class SteamWebCrawler:

    valid_cookies = 'sessionid', 'steamMachineAuth', 'steamLoginSecure', 'timezoneOffset'

    def __init__(self, steam_id: str, steam_alias: str, cookies_data: dict):
        self.__steam_id = steam_id
        self.__steam_alias = steam_alias
        self.__cookies: dict = {}
        self.__set_crawler_cookies(cookies_data)
        # self.__web_session = None  # it should be implemented later

    def interact(self, page_name: str, logged_in = False, **kwargs) -> (int, Union[str, requests.Response]):

        try:
            concrete_web_page_reference = SteamWebPage.page_names[page_name]
            web_page = concrete_web_page_reference()
        except IndexError:
            return 404, 'page not implemented'

        kwargs['steam_id'] = self.__steam_id
        kwargs['steam_alias'] = self.__steam_alias
        required_data: tuple = web_page.required_user_data()
        missing_required_data: list = self.__missing_required_data(required_data, **kwargs)
        if missing_required_data:
            return 400, f'missing user data: {missing_required_data}'

        required_cookies: tuple = web_page.required_cookies()
        cookies, missing_cookies = self.__get_interaction_cookies(logged_in, required_cookies)
        if missing_cookies:
            return 403, f'missing cookies: {missing_cookies}'

        required_referer = web_page.required_referer()
        kwargs['referer'] = self.__get_page_referer(required_referer, **kwargs)

        try:
            result = web_page.interact(cookies, **kwargs)
            return result.status_code, result
        except Exception as e:
            return 500, e

    def __set_crawler_cookies(self, cookies_to_add: dict):
        for name, cookie in cookies_to_add.items():
            if name == 'steamMachineAuth':
                self.__cookies[name + self.__steam_id] = cookie
                continue
            if name in self.valid_cookies:
                self.__cookies[name] = cookie

    @staticmethod
    def __missing_required_data(req_data, **kwargs) -> list:
        missing = []
        for data in req_data:
            if data not in kwargs.keys():
                missing.append(data)
        return missing

    def __get_interaction_cookies(self, logged_in: bool, required_cookies: tuple) -> tuple[dict, list]:
        request_cookies = {}
        missing_cookies = []

        if logged_in:
            if 'steamLoginSecure' in self.__cookies:
                request_cookies['steamLoginSecure'] = self.__cookies['steamLoginSecure']
            else:
                missing_cookies.append('steamLoginSecure')

        for cookie in required_cookies:
            if cookie == 'steamMachineAuth':
                cookie = 'steamMachineAuth' + self.__steam_id
            if cookie not in self.__cookies.keys():
                missing_cookies.append(cookie)
            request_cookies[cookie] = self.__cookies[cookie]

        return request_cookies, missing_cookies

    @staticmethod
    def __get_page_referer(req_referer: str, **kwargs) -> str:
        if not req_referer:
            return ''
        referer_web_page = SteamWebPage.page_names[req_referer]()
        referer_url = referer_web_page.generate_url(**kwargs)
        return referer_url


if __name__ == '__main__':
    # mock setup
    MOCK_steam_id = ''
    MOCK_steam_alias = ''
    MOCK_cookies = {}
    MOCK_crawler = SteamWebCrawler(MOCK_steam_id, MOCK_steam_alias, MOCK_cookies)

    # test
    status_code, response = MOCK_crawler.interact('')