# Copyright 2017 Spirent Communications.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License

import copy


class Methodology(object):
    def __init__(self, session):
        self.session = session
        self.test_url = session.url + '/api/tests'
        self.exec_url = session.url + '/api/executions'
        self.meth_url = session.url + '/api/methodologies'
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Spirent-Run-Omit-Warnings': 'true'
        }


    def create(self, test, overwrite=False):
        headers = self.headers
        if overwrite:
            headers = copy.copy(self.headers)
            headers['X-Spirent-Force'] = '1'

        r = self.session.post(self.test_url, headers=headers,
                                 json=test)

        if (r.status_code != 201):
            raise RuntimeError('Unexpected response {}: {}'.format(
                r.status_code, r.content))
        return r.json()


    def update(self, test):
        r = self.session.put(self.test_url + '/' + test['id'],
                                headers=self.headers,
                                json=test)
        if (r.status_code != 200):
            raise RuntimeError('Unexpected response {}: {}'.format(
                r.status_code, r.content))
        return r.json()


    def get_test_by_name(self, test_name):
        params = {'name': test_name, 'owner_id': self.session.get_user_id()}
        r = self.session.get(self.test_url, params=params,
                                headers=self.headers)
        if (r.status_code != 200):
            raise RuntimeError('Unexpected response {}: {}'.format(
                r.status_code, r.content))

        for test in r.json()['items']:
            if test['name'].lower() == test_name.lower():
                return test
        return {}


    def get_test_by_id(self, id):
        r = self.session.get(self.test_url + '/' + id,
                                headers=self.headers)
        if (r.status_code != 200):
            raise RuntimeError('Unexpected response {}: {}'.format(
                r.status_code, r.content))
        return r.json()


    def get_execution_info(self, test):
        params = {'test_id': test['id']}
        headers = copy.copy(self.headers)
        headers.pop('Content-Type')
        r = self.session.get(self.exec_url, params=params, headers=headers)
        if (r.status_code != 200):
            raise RuntimeError('Unexpected response {}: {}'.format(
                r.status_code, r.content))
        return r.json()


    def get_execution_info_by_id(self, id):
        r = self.session.get(self.exec_url + '/' + id)
        # Execution has been deleted by the backend
        if r.status_code in [404, 504]:
            if r.status_code == 404:
                print "Execution status no longer found: {}".format(id)
            else:
                print "Gateway timeout"
            return { 'status': 'Stopped' }
        if (r.status_code != 200):
            raise RuntimeError('Unexpected response {}: {}'.format(
                r.status_code, r.content))
        return r.json()


    def list(self, key=None):
        params = None
        if key:
            params = {'methodology_key': key}

        r = self.session.get(self.meth_url, params=params, headers=self.headers)
        if (r.status_code != 200):
            raise RuntimeError('Unexpected response {}: {}'.format(
                r.status_code, r.content))
        return r.json()
