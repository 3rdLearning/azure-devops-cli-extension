# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from knack.arguments import enum_choice_list, ArgumentsContext

_on_off_switch_values = ['on', 'off']


def load_build_arguments(cli_command_loader):
    with ArgumentsContext(cli_command_loader, 'build') as ac:
        ac.argument('open_browser', options_list='--open')
        ac.argument('project', options_list=('--team-project', '-p'))
        ac.argument('team_instance', options_list=('--team-instance', '-i'))
        ac.argument('detect', **enum_choice_list(_on_off_switch_values))

    with ArgumentsContext(cli_command_loader, 'build show') as ac:
        ac.argument('build_id', options_list='--id', type=int)

    with ArgumentsContext(cli_command_loader, 'build show') as ac:
        ac.argument('definition_id', options_list='--id')
