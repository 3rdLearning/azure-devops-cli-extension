from azure.cli.testsdk import ScenarioTest
from azure_devtools.scenario_tests import AllowLargeResponse
from vsts.exceptions import VstsServiceError

import string
import random

def random_string(length):
    return ''.join(random.choice(string.ascii_letters) for m in range(length))

class AzureDevTests(ScenarioTest):
    @AllowLargeResponse(size_kb=3072)
    def test_workItemCreateShowUpdateDelete(self):
        wi_name = 'samplebug'
        wi_test_project_name = 'WorkItemCreateShowUpdateDeleteTests'
        wi_account_instance='https://AzureDevOpsCliTest.visualstudio.com'
        wi_account_pat = 'lwghjbj67fghokrgxsytghg75nk2ssguljk7a78qpcg2ttygviyt'

        self.cmd('az dev configure --defaults instance=' + wi_account_instance + ' token=' + wi_account_pat)
        self.cmd('az dev login --token ' + wi_account_pat)

        create_wi_command = 'az boards work-item create --detect off --project '+ wi_test_project_name +' --title ' + wi_name +' --type Bug'
        wi_create = self.cmd(create_wi_command, checks=[
            self.check('fields."System.AreaPath"', wi_test_project_name),
            self.check('fields."System.WorkItemType"', 'Bug'),
            self.check('fields."System.Title"', wi_name)
        ]).get_output_in_json()

        wi_id = wi_create['id']

        show_wi_command ='az boards work-item show -i ' + wi_account_instance + ' --detect off --id '+ str(wi_id)
        wi_show = self.cmd(show_wi_command, checks=[
            self.check("id", wi_id)
        ]).get_output_in_json()

        update_wi_command = 'az boards work-item update -i ' + wi_account_instance + ' --detect off --id '+ str(wi_id)+' --state Resolved'
        wi_update = self.cmd(update_wi_command, checks=[
            self.check("id", wi_id),
            self.check('fields."System.AreaPath"', wi_test_project_name),
            self.check('fields."System.State"','Resolved')
        ]).get_output_in_json()

        delete_wi_command = 'az boards work-item delete -i ' + wi_account_instance + ' --detect off --id '+ str(wi_id)+' --yes --project ' + wi_test_project_name
        wi_delete = self.cmd(delete_wi_command)

        #verify if the work item is deleted or not
        with self.assertRaises(VstsServiceError) as wi_except:
            wi_show = self.cmd(show_wi_command).get_output_in_json()
        self.assertEqual(str(wi_except.exception), 'TF401232: Work item ' + str(wi_id) + ' does not exist, or you do not have permissions to read it.')
