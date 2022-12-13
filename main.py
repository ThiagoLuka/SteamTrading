from user_interfaces.MainUI import MainUI
from user_interfaces.GenericUI import GenericUI
from steam_users.SteamUserController import SteamUserController
from db.DBController import DBController


if __name__ == '__main__':

    SteamUserController()
    DBController()

    while True:
        command = MainUI.run()
        user = SteamUserController().get_active_user()

        if command == 1:
            SteamUserController().run_ui()
        if command == 2:
            user.get_badges()
        if command == 3:
            user.update_inventory()
        if command == 4:
            game_name = GenericUI.get_string('Digite o nome do jogo: ')
            user.open_booster_packs(game_name)

        if command == 0:
            MainUI.goodbye()
            break
