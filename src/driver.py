from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.context import ResourceCommandContext, InitCommandContext
import cloudshell.api.cloudshell_api as cs_api
from cloudshell.api.common_cloudshell_api import CloudShellAPIError
from methodology import Methodology
from temeva import Temeva
from session import Session
from report import Report
from time import sleep

class TemevaServiceDriver (ResourceDriverInterface):

    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        pass

    def initialize(self, context):
        """
        Initialize the driver session, this function is called everytime a new instance of the driver is created
        This is a good place to load and cache the driver configuration, initiate sessions etc.
        :param InitCommandContext context: the context the command runs on
        """
        self.cs_session = self.start_cloudshell_api()
        self._start_temeva_session
        self.temeva_meth = Methodology(self.temeva_session)
        self.temeva_report = Report(self.temeva_session)

    def start_cloudshell_api(self, context):
        """
        
        :param ResourceCommandContext context: 
        :return: 
        """
        if not self.cs_session:
            try:
                self.cs_session = cs_api.CloudShellAPISession(context.connectivity.server_address,
                                                              token_id=context.connectivity.admin_auth_token,
                                                              domain=context.reservation.domain
                                                              )
            except CloudShellAPIError as e:
                print e.message

    def _decrypt_password(self, password):
        if not self.cs_session:
            self.start_cloudshell_api()
        return  self.cs_session.DecryptPassword(password).Value

    def _start_temeva_session(self, context):
        """
        
        :param ResourceCommandContext context: 
        """
        self.temeva = Temeva(context.ATTRIBUTE_MAP['User'],
                             self._decrypt_password(context.ATTRIBUTE_MAP['Password']),
                             context.resource.ATTRIBUTE_MAP['Subdomain'],
                             'https://%s.temeva.com' % context.resource.address
                             )

        self.temeva_session = Session(self.temeva, context.resource.ATTRIBUTE_MAP['Tailsman IP'])

    def _write_message(self, message):
        return message

    def run_test(self, context, test_id):
        """
        A simple example function
        :param ResourceCommandContext context: the context the command runs on
        """
        my_test = self.temeva_meth.get_test_by_id(test_id)
        if not my_test:
            return 'Test ID %s not found' % test_id

        if not my_test['running']:
            my_test['running'] = True
            my_test = self.temeva_meth.update(my_test)
        self._wait_for_test_stop_by_execution(my_test)
        my_test = self.temeva_meth.get_test_by_id(my_test['id'])
        report = self.temeva_report.get_by_id(my_test['last_report_id'])
        self._write_message('Test ID %s Complete - Result: %s' % (my_test['id'], report['verdict']))

    def _wait_for_test_stop_by_execution(self, test):
        """
        
        :param get_test_by_id test: 
        """
        exec_info = self.temeva_meth.get_execution_info(test)
        exec_id = exec_info[0]['id']
        check_status = exec_info[0]['status']

        self._write_message('Test ID %s Status: %s' % (test['id'], check_status))

        while check_status != 'Stopped':
            sleep(5)
            exec_info = self.temeva_meth.get_execution_info_by_id(exec_id)
            curr_status = exec_info['status']
            self._write_message('Test ID %s Status %s' % (test['id'], curr_status))
            if check_status != curr_status:
                check_status = curr_status


    def _wait_for_test_stop_by_status(self, test):
        """
        
        :param get_test_by_id test: 
        """
        while test['running']:
            sleep(5)
            try:
                test = self.temeva_meth.get_test_by_id(test['id'])
            except RuntimeError as e:
                self._write_message(e.message)

            if test['running']:
                self._write_message('Test ID %s in progress . . .' % test['id'])
            else:
                self._write_message('Test ID %s COMPLETE' % test['id'])
                break


    def example_function_with_params(self, context, user_param1, user_param2):
        """
        An example function that accepts two user parameters
        :param ResourceCommandContext context: the context the command runs on
        :param str user_param1: A user parameter
        :param str user_param2: A user parameter
        """
        pass
        
    def cleanup(self):
        """
        Destroy the driver session, this function is called everytime a driver instance is destroyed
        This is a good place to close any open sessions, finish writing to log files
        """
        pass