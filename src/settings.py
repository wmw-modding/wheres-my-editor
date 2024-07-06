# ==================================
# Created by ego-lay-atman-bay
# Under the GNU v3 license.
# If used, please give credit
# 
# Repository: https://github.com/ego-lay-atman-bay/python-settings
# ==================================

__version__ = '1.0.0'
__author__ = 'ego-lay-atman-bay'

import json
from copy import deepcopy
from typing import Any
import os

class Settings(dict):
    def __init__(
        self,
        filename : str = 'settings.json',
        default_settings : dict[str, Any] = None,
    ) -> None:
        """Settings object.

        Args:
            filename (str, optional): Path to settings file. Defaults to 'settings.json'.
            default_settings (dict, optional): Default settings. Defaults to {'version' : 1}.
        """
        
        self.filename = filename
        if default_settings == None:
            default_settings = {'version' : 1}
        self.default_settings = deepcopy(default_settings)
        super().__init__(self.default_settings)
        
        self.load()
    
    def load(self, **kwargs):
        """Load the settings file. If the file does not exist, then create it.

        Returns:
            dict: Loaded settings.
        """
        if kwargs.get('settings'):
            self.update(kwargs['settings'])
        else:
            if os.path.isfile(self.filename):
                with open(self.filename, 'r') as file:
                    settings = json.load(file)
                
                self.update(settings)
            self.save()
    
    def save(self):
        """Save the settings.
        """
        with open(self.filename, 'w') as file:
            json.dump(self, file, indent=2)
    
    def set(self, name : str, value):
        """Set a setting.

        Args:
            name (str): The name of the setting to change
            value (Any): The value to save.
        """
        option = self._split_option(name)
        settings = self._get_settings(option, self)
        settings[option[-1]] = value
        self.save()
    
    def get(self, name : str):
        """Get a setting.

        Args:
            name (str): Name of the setting to get.

        Returns:
            Any: The value that the setting is set to.
        """
        option = self._split_option(name)
        settings = self._get_settings(option, self)
        return settings[option[-1]]
    
    def remove(self, name : str):
        """Delete a setting.

        Args:
            name (str): Name of setting to delete.
        """
        option = self._split_option(name)
        settings = self._get_settings(option, self)
        del settings[option[-1]]
        self.save()
    
    def initialize(self):
        """Initialize the settings. This resets the settings, then saves.
        """
        self.clear()
        self.update(self.default_settings)
        self.save()
    
    def _split_option(self, value : str | list) -> list[str]:
        if isinstance(value, (list, tuple)):
            return list(value)
        elif isinstance(value, str):
            return value.split('.')
        else:
            raise [value]
    
    def _get_settings(self, value : list, settings : dict):
        if len(value) <= 1:
            return settings
        else:
            try:
                items = settings[value[0]]
            except:
                settings[value[0]] = {}
                items = settings[value[0]]
            
            return self._get_settings(value[1::], items)
