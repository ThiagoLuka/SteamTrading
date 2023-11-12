"""
This is a one-time use script to import the data from my old software.
I stored the buy order in a json file with the structure that lies below.
A simple ETL pipeline will do the job. It's a bit messy but it works.
File format:
{
game_name:
    {
    item_name:
        [
            {
            'qtd': int,
            'price': int
            'date_begin': date as isoformat
            'last_update': date as isoformat
            },
            {another_buy_order}, ...
        ],
    },
    "another_item": [], ...
},
"another_game": {}, ...
"""

import json

import pandas as pd

from data_models.SteamGames import SteamGames
from data_models.ItemsSteam import ItemsSteam
from data_models.PandasUtils import PandasUtils
from repositories.QueryBuilderPG import QueryBuilderPG
from db.DBController import DBController

def data_extraction() -> dict:
    with open('db/buy_orders.json', encoding='utf-8') as file:
        file_content = json.load(file)
        return file_content


def data_flattener(dict_data: dict) -> pd.DataFrame:
    # first, the key values should be adjusted to be the same in every record
    new_data = []
    for game_name, item_dict in dict_data.items():
        new_data.append({
            'game_name': game_name,
            'item_dicts': item_dict,
        })

    new_data2 = []
    for entry in new_data:
        for item_name, buy_orders in entry['item_dicts'].items():
            new_data2.append({
                'game_name': entry['game_name'],
                'item_name': item_name,
                'buy_orders': buy_orders
            })

    # now data can be easily flattened by pandas
    data_df = pd.json_normalize(new_data2, record_path='buy_orders', meta=['game_name', 'item_name'])
    return data_df


def add_game_id(data_df: pd.DataFrame) -> pd.DataFrame:
    data_df.replace({
        'game_name': {
            'Ball 3D': 'Ball 3D: Soccer Online',
            'Battlefield 4™': 'Battlefield 4™ ',
            'Company of Heroes': 'Company of Heroes ',
            'Dead Space': 'Dead Space (2008)',
            'EARTH DEFENSE FORCE 4.1 WINGDIVER THE SHOOTER': 'EARTH DEFENSE FORCE 4.1  WINGDIVER THE SHOOTER',
            'FINAL FANTASY IV': 'Final Fantasy IV (3D Remake)',
            'Party Hard 2': 'Party Hard 2 ',
            'Resident Evil 4': 'resident evil 4 (2005)',
            'Ro\u0308ki': 'Röki',
            'SpellForce 3': 'SpellForce 3 Reforced',
            'THE GAME OF LIFE': 'THE GAME OF LIFE ',
            'Need for Speed™ Heat': 'Need for Speed™ Heat ',
            'Layers of Fear': 'Layers of Fear (2016)'
        }
    }, inplace=True)

    games = SteamGames.get_all().df
    games.rename(columns={'id': 'game_id', 'name': 'game_name', 'market_id': 'game_market_id'}, inplace=True)

    data_df = pd.merge(data_df, games[['game_id', 'game_name']])

    return data_df


def add_item_steam_id(data_df: pd.DataFrame) -> pd.DataFrame:
    data_df.replace({
        'item_name': {
            'Ball 3D Booster Pack': 'Ball 3D: Soccer Online Booster Pack',
            'Battlefield 4™ Booster Pack': 'Battlefield 4™  Booster Pack',
            'Company of Heroes Booster Pack': 'Company of Heroes  Booster Pack',
            'Dead Space Booster Pack': 'Dead Space (2008) Booster Pack',
            'EARTH DEFENSE FORCE 4.1 WINGDIVER THE SHOOTER Booster Pack':
                'EARTH DEFENSE FORCE 4.1  WINGDIVER THE SHOOTER Booster Pack',
            'THE QUICK BOW': ' THE QUICK BOW',
            "Death's Gambit Booster Pack": "Death's Gambit: Afterlife Booster Pack",
            'Lord Dredmor': ' Lord Dredmor',
            'FINAL FANTASY IV Booster Pack': 'Final Fantasy IV (3D Remake) Booster Pack',
            'Mass Effect™: Andromeda Deluxe Edition Booster Pack': 'Mass Effect™: Andromeda Booster Pack',
            'Abstraction': ' Abstraction',
            "It's GOTTA be purple!": " It's GOTTA be purple!",
            'Party Hard 2 Booster Pack': 'Party Hard 2  Booster Pack',
            'Resident Evil 4 Booster Pack': 'resident evil 4 (2005) Booster Pack',
            'Ro\u0308ki Booster Pack': 'Röki Booster Pack',
            'SpellForce 3 Booster Pack': 'SpellForce 3 Reforced Booster Pack',
            'THE GAME OF LIFE Booster Pack': 'THE GAME OF LIFE  Booster Pack',
            'Need for Speed™ Heat Booster Pack': 'Need for Speed™ Heat  Booster Pack',
            'Four Virtues': ' Four Virtues',
            "It's our home": " It's our home",
            'The city on fire': ' The city on fire',
            "Uptown's tranquility": " Uptown's tranquility",
            'Ork Warboss Ghazghkull Mag Uruk Thraka': ' Ork Warboss Ghazghkull Mag Uruk Thraka',
        },
    }, inplace=True)

    items = ItemsSteam.get_all().df
    items.rename(columns={'id': 'item_steam_id', 'name': 'item_name'}, inplace=True)

    data_df = pd.merge(data_df, items[['item_steam_id', 'item_name', 'game_id']], how='left')

    data_df.loc[data_df['item_name'] == 'Operator -3', 'item_steam_id'] = 62
    data_df.loc[data_df['item_name'] == 'Operator -4', 'item_steam_id'] = 63
    data_df.loc[data_df['item_name'].str.contains('Mass Effect'), 'item_steam_id'] = 3657

    return data_df


def transform(data_df: pd.DataFrame) -> pd.DataFrame:
    data_df = data_df[['item_steam_id', 'price', 'qtd', 'date_begin', 'last_update']]

    data_df.rename(columns={
        'qtd': 'qtd_current',
        'date_begin': 'created_at',
        'last_update': 'updated_at',
    }, inplace=True)

    data_df.loc[data_df['qtd_current'] == 0, 'active'] = False
    data_df.loc[data_df['qtd_current'] != 0, 'active'] = True

    data_df['qtd_start'] = 100  # I almost always set the buy order with 100 of qtd
    data_df['qtd_estimate'] = data_df['qtd_current']

    data_df['created_at'] = pd.to_datetime(data_df['created_at'])
    data_df['updated_at'] = pd.to_datetime(data_df['updated_at'])
    data_df.loc[data_df['active'] == True, 'removed_at'] = None
    data_df.loc[data_df['active'] == False, 'removed_at'] = data_df['updated_at']

    columns = [
        'item_steam_id', 'active', 'price', 'qtd_start', 'qtd_estimate', 'qtd_current',
        'created_at', 'updated_at', 'removed_at'
    ]
    data_df = data_df[columns]

    return data_df


def data_load(data_df: pd.DataFrame, columns: list) -> None:
    zipped_data = PandasUtils.zip_df_columns(data_df, columns)
    values = QueryBuilderPG.unzip_to_query_values_str(zipped_data)
    query = f"""
        INSERT INTO buy_orders ({', '.join(columns)})
        VALUES {values};
    """
    DBController.execute(query=query)


if __name__ == '__main__':

    data = data_extraction()

    df = data_flattener(data)

    df = add_game_id(df)
    df = add_item_steam_id(df)

    df = transform(df)

    df['steam_buy_order_id'] = None
    df['user_id'] = 1
    df['removed_at'].fillna('None', inplace=True)

    buy_orders_columns = [
        'steam_buy_order_id', 'user_id', 'item_steam_id', 'active', 'price',
        'qtd_start', 'qtd_estimate', 'qtd_current', 'created_at', 'updated_at', 'removed_at'
    ]

    df = df[buy_orders_columns]

    data_load(df, buy_orders_columns)
