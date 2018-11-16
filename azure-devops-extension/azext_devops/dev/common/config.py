# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import stat
from six.moves import configparser

from knack.config import CLIConfig, get_config_parser
from knack.util import ensure_dir
from .const import (AZ_DEVOPS_CONFIG_DIR_ENVKEY,
                    AZ_DEVOPS_CONFIG_DIR,
                    CLI_ENV_VARIABLE_PREFIX)

CONFIG_FILE_NAME = 'config'
CORE_SECTION = 'core'
DEFAULTS_SECTION = 'defaults'
LOGGING_SECTION = 'logging'

_UNSET = object()


def _get_config_dir():
    azure_devops_config_dir = os.getenv(AZ_DEVOPS_CONFIG_DIR_ENVKEY, None) or AZ_DEVOPS_CONFIG_DIR
    #Create a directory if it doesn't exist
    ensure_dir(azure_devops_config_dir)
    return azure_devops_config_dir


GLOBAL_CONFIG_DIR = _get_config_dir()
GLOBAL_CONFIG_PATH = os.path.join(GLOBAL_CONFIG_DIR, CONFIG_FILE_NAME)

class AzDevopsConfig(CLIConfig):
    def __init__(self, config_dir=GLOBAL_CONFIG_DIR, config_env_var_prefix=CLI_ENV_VARIABLE_PREFIX):
        super(AzDevopsConfig, self).__init__(config_dir=config_dir, config_env_var_prefix=config_env_var_prefix)
        self.config_parser = get_config_parser()


azdevops_config = AzDevopsConfig()
azdevops_config.config_parser.read(GLOBAL_CONFIG_PATH)


def set_global_config(config):
    ensure_dir(GLOBAL_CONFIG_DIR)
    with open(GLOBAL_CONFIG_PATH, 'w') as configfile:
        config.write(configfile)
    os.chmod(GLOBAL_CONFIG_PATH, stat.S_IRUSR | stat.S_IWUSR)
    # reload config
    azdevops_config.config_parser.read(GLOBAL_CONFIG_PATH)


def set_global_config_value(section, option, value):
    config = get_config_parser()
    config.read(GLOBAL_CONFIG_PATH)
    try:
        config.add_section(section)
    except configparser.DuplicateSectionError:
        pass
    config.set(section, option, _normalize_config_value(value))
    set_global_config(config)


def _normalize_config_value(value):
    if value:
        value = '' if value in ["''", '""'] else value
    return value
