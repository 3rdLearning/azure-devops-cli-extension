# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging


from .vsts import raise_authentication_error
from knack.util import CLIError
from vsts.exceptions import VstsAuthenticationError


def handle_command_exception(exception):
    logging.exception(exception)
    if type(exception) is CLIError:
        raise exception
    if type(exception) is VstsAuthenticationError:
        raise_authentication_error(exception)
    raise CLIError(exception)
