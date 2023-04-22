# Import all the modules in DataCollectors and add the functions into globals

import os
import importlib
for module_file in os.listdir(os.path.dirname(__file__)):
    if module_file == '__init__.py':
        continue

    module_name, extension = os.path.splitext(module_file)
    if extension != '.py':
        continue

    module_name = '.' + module_name
    import_mod = importlib.import_module(module_name, __name__)

    for key,value in import_mod.__dict__.items():
        if not key.startswith('_'):
            globals().update({key : value})
del module_file