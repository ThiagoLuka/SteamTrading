import os
import importlib

from .SteamWebCrawler import SteamWebCrawler


for file in os.listdir(os.path.dirname(__file__)):
    if file.endswith('.py') and not file.startswith('_'):
        module_name = file[:file.find('.py')]
        module = importlib.import_module('steam_web_crawler.' + module_name)
