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

class Settings():
    def __init__(
        this,
        filename : str = 'settings.json',
        default_settings : dict[str] = {'version' : 1},
    ) -> None:
        """Settings object.

        Args:
            filename (str, optional): Path to settings file. Defaults to 'settings.json'.
            default_settings (dict, optional): Default settings. Defaults to {'version' : 1}.
        """
        
        this.filename = filename
        this.default_settings = deepcopy(default_settings)
        this.settings = deepcopy(this.default_settings)
        
        this.load()
    
    def load(this, **kwargs):
        """Load the settings file. If the file does not exist, then create it.

        Returns:
            dict: Loaded settings.
        """
        try:
            this.settings = kwargs['settings']
        except:
            try:
                with open(this.filename, 'r') as file:
                    settings = json.load(file)
                
                def addSettings(settings, default):
                    for setting in settings:
                        if isinstance(settings[setting], dict):
                            try:
                                if not isinstance(default[setting], dict):
                                    default[setting] = {}
                            except:
                                default[setting] = {}
                            
                            addSettings(settings[setting], default[setting])
                        else:
                            default[setting] = settings[setting]
                
                addSettings(settings, this.settings)
            except:
                pass
            this.save()
        return this.settings
    
    def save(this):
        """Save the settings.
        """
        with open(this.filename, 'w') as file:
            json.dump(this.settings, file, indent=2)
    
    def set(this, name : str, value):
        """Set a setting.

        Args:
            name (str): The name of the setting to change
            value (Any): The value to save.
        """
        option = this._split_option(name)
        settings = this._get_settings(option, this.settings)
        settings[option[-1]] = value
        this.save()
    
    def get(this, name : str):
        """Get a setting.

        Args:
            name (str): Name of the setting to get.

        Returns:
            Any: The value that the setting is set to.
        """
        option = this._split_option(name)
        settings = this._get_settings(option, this.settings)
        return settings[option[-1]]
    
    def remove(this, name : str):
        """Delete a setting.

        Args:
            name (str): Name of setting to delete.
        """
        option = this._split_option(name)
        settings = this._get_settings(option, this.settings)
        del settings[option[-1]]
        this.save()
    
    def initialize(this):
        """Initialize the settings. This resets the settings, then saves.
        """
        this.settings = deepcopy(this.default_settings)
        this.save()
    
    def _split_option(this, value : str | list) -> list[str]:
        if isinstance(value, (list, tuple)):
            return list(value)
        return value.split('.')
    
    def _get_settings(this, value : list, settings : dict):
        if len(value) <= 1:
            return settings
        else:
            try:
                items = settings[value[0]]
            except:
                settings[value[0]] = {}
                items = settings[value[0]]
            
            return this._get_settings(value[1::], items)
