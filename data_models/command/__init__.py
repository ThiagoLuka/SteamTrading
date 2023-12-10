import os
import importlib

from .PersistToDB import PersistToDB


for file in os.listdir(os.path.dirname(__file__)):
    if file.endswith('.py') and not file.startswith('_'):
        module_name = file[:file.find('.py')]
        module = importlib.import_module('data_models.command.' + module_name)
