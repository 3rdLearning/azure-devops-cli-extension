# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import logging
import urllib
import webbrowser

from knack.util import CLIError
from vsts.core.v4_0.models.team_project import TeamProject
from vsts.exceptions import VstsClientRequestError
from vsts.git.v4_0.models.git_pull_request import GitPullRequest
from vsts.git.v4_0.models.git_pull_request_completion_options import GitPullRequestCompletionOptions
from vsts.git.v4_0.models.git_pull_request_search_criteria import GitPullRequestSearchCriteria
from vsts.git.v4_0.models.identity_ref import IdentityRef
from vsts.git.v4_0.models.identity_ref_with_vote import IdentityRefWithVote
from vsts.git.v4_0.models.resource_ref import ResourceRef
from vsts.work_item_tracking.v4_0.models.json_patch_operation import JsonPatchOperation
from vsts.work_item_tracking.v4_0.models.work_item_relation import WorkItemRelation
from vsts.cli.common.arguments import resolve_on_off_switch, should_detect
from vsts.cli.common.exception_handling import handle_command_exception
from vsts.cli.common.operations import wait_for_long_running_operation
from vsts.cli.common.git import get_current_branch_name, resolve_git_ref_heads, setup_git_alias
from vsts.cli.common.identities import ME, resolve_identity_as_id
from vsts.cli.common.uuid import EMPTY_UUID
from vsts.cli.common.vsts import (get_base_url,
                                  get_core_client,
                                  get_operations_client,
                                  get_vsts_info_from_current_remote_url,
                                  get_work_item_tracking_client,
                                  resolve_project)


def create_project(name, team_instance=None, process=None, source_control='git', description=None, detect=None):
    """Create a team project.
    :param name: Name of the new project.
    :type name: str
    :param team_instance: The URI for the VSTS account (https://<account>.visualstudio.com) or your TFS project
                          collection.
    :type team_instance: str
    :param process: Process to use. Default if not specified.
    :type process: str
    :param source_control: Source control type of the initial code repository created.
                           Valid options: git (the default) and tfvc.
    :type source_control: str
    :param description: Description for the new project.
    :type description: str
    """
    try:
        if should_detect(detect):
            if team_instance is None:
                git_info = get_vsts_info_from_current_remote_url()
                team_instance = git_info.uri

        team_project = TeamProject()
        team_project.name = name
        team_project.description = description
        team_project.visibility = 'private'

        core_client = get_core_client(team_instance)

        # get process template id
        process_id = None
        process_list = core_client.get_processes()
        if process is not None:
            process_lower = process.lower()
            for process in process_list:
                if process.name.lower() == process_lower:
                    process_id = process.id
                    break
            if process_id is None:
                raise CLIError('Could not find a process template with name: "{}"'.format(name))
        if process_id is None:
            for process in process_list:
                if process.is_default:
                    process_id = process.id
                    break
            if process_id is None:
                raise CLIError('Could not find a default process template: "{}"'.format(name))

        # build capabilities
        version_control_capabilities = {VERSION_CONTROL_CAPABILITY_ATTRIBUTE_NAME: source_control}
        process_capabilities = {PROCESS_TEMPLATE_CAPABILITY_TEMPLATE_TYPE_ID_ATTRIBUTE_NAME: process_id}
        team_project.capabilities = {VERSION_CONTROL_CAPABILITY_NAME: version_control_capabilities,
                                     PROCESS_TEMPLATE_CAPABILITY_NAME: process_capabilities}

        # queue project creation
        operation_reference = core_client.queue_create_project(project_to_create=team_project)
        operation = wait_for_long_running_operation(team_instance, operation_reference.id, 1)
        status = operation.status.lower()
        if status == 'failed':
            raise CLIError('Project creation failed.')
        elif status == 'cancelled':
            raise CLIError('Project creation was cancelled.')

        team_project = core_client.get_project(project_id=name, include_capabilities=True)
        return team_project
    except Exception as ex:
        handle_command_exception(ex)


def show_project(id, team_instance=None, detect=None):
    """Get project with the specified id or name.
    :param id: Name or id of the project to show.
    :type id: str
    :param team_instance: The URI for the VSTS account (https://<account>.visualstudio.com) or your TFS project
                          collection.
    :type team_instance: str
    """
    try:
        if should_detect(detect):
            if team_instance is None:
                git_info = get_vsts_info_from_current_remote_url()
                team_instance = git_info.uri
        core_client = get_core_client(team_instance)
        team_project = core_client.get_project(project_id=id, include_capabilities=True)
        return team_project
    except Exception as ex:
        handle_command_exception(ex)


def list_projects(team_instance=None, top=None, skip=None, detect=None):
    """Get project with the specified id or name.
    :param team_instance: The URI for the VSTS account (https://<account>.visualstudio.com) or your TFS project
                          collection.
    :type team_instance: str
    :param top:
    :type top: int
    :param skip:
    :type skip: int
    """
    try:
        if should_detect(detect):
            if team_instance is None:
                git_info = get_vsts_info_from_current_remote_url()
                team_instance = git_info.uri
        core_client = get_core_client(team_instance)
        team_projects = core_client.get_projects(state_filter='all', top=top, skip=skip)
        return team_projects
    except Exception as ex:
        handle_command_exception(ex)


# capability keys
VERSION_CONTROL_CAPABILITY_NAME = 'versioncontrol'
VERSION_CONTROL_CAPABILITY_ATTRIBUTE_NAME = 'sourceControlType'
PROCESS_TEMPLATE_CAPABILITY_NAME = 'processTemplate'
PROCESS_TEMPLATE_CAPABILITY_TEMPLATE_TYPE_ID_ATTRIBUTE_NAME = 'templateTypeId'
