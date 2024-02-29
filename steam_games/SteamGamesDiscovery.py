import requests
import time

import pandas as pd

from user_interfaces.SteamTraderUI import SteamTraderUI
from data_models import QueryDB, PersistToDB


class SteamGamesDiscovery:

    def discover_new_apps(self, qtd: int = 2700, wait_time: int = 4) -> None:
        df = self._get_steam_all_apps()
        steam_discovered_apps = self._get_discovered_steam_app_ids()
        undiscovered_apps_series = df.loc[~df['appid'].isin(steam_discovered_apps), 'appid']
        app_ids = undiscovered_apps_series.sample(n=qtd)
        app_ids.reset_index(drop=True, inplace=True)

        for index, app_id in app_ids.items():
            name = df.loc[df['appid'] == app_id, 'name'].iat[0]
            SteamTraderUI.game_header_with_counter(game_name=f'{app_id} - {name}', index=index)
            result = requests.get(f'https://store.steampowered.com/api/appdetails?appids={app_id}')
            result_dict = result.json()[str(app_id)]
            if result_dict['success']:
                app_raw_data = result_dict['data']
                coming_soon = app_raw_data['release_date']['coming_soon']
                app_data = [{
                    'app_id': app_id,
                    'request_success': True,
                    'name': app_raw_data['name'],
                    'processed': False,
                    'app_type': app_raw_data['type'],
                    'full_game_app_id': app_raw_data['fullgame']['appid'] if 'fullgame' in app_raw_data.keys() else None,
                    'has_cards': self._get_has_cards(app_raw_data),
                    'coming_soon': coming_soon,
                    'release_date': app_raw_data['release_date']['date']
                }]
            else:
                app_data = [{
                    'app_id': app_id,
                    'request_success': False,
                    'name': None,
                    'processed': False,
                    'app_type': None,
                    'full_game_app_id': None,
                    'has_cards': False,
                    'coming_soon': False,
                    'release_date': None,
                }]
            PersistToDB.persist('game', source='discovery',
                data=app_data
            )
            time.sleep(wait_time)


    def process_discovered_apps(self) -> None:
        pass

    @staticmethod
    def _get_steam_all_apps() -> pd.DataFrame:
        result = requests.get('https://api.steampowered.com/ISteamApps/GetAppList/v2/')
        result_json = result.json()
        df = pd.DataFrame(result_json['applist']['apps'])
        df.drop_duplicates(inplace=True)
        return df

    @staticmethod
    def _get_discovered_steam_app_ids() -> list:
        db_data = QueryDB.get_repo('games').get_all_discovered_app_ids()
        db_data_as_list = [int(item[0]) for item in db_data]
        return db_data_as_list

    @staticmethod
    def _get_has_cards(raw_data: dict) -> bool:
        if 'categories' not in raw_data.keys():
            return False
        for cat in raw_data['categories']:
            if cat['id'] == 29:  # same as cat['description'] == 'Steam Trading Cards'
                return True
        return False
