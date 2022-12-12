

class SteamWebPage:

    BASESTEAMURL = 'https://steamcommunity.com/'

    page_interactions: dict = {}

    def __init_subclass__(cls, **kwargs):
        SteamWebPage.page_interactions.update({kwargs['name']: cls})

    @staticmethod
    def required_user_data() -> tuple:
        pass

    @staticmethod
    def required_cookies() -> tuple:
        pass

    def interact(self, cookies: dict, **kwargs):
        pass
