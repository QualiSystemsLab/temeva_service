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

import requests
import subprocess
import json


class Temeva(object):
    """ Temeva applications require a bearer token from the
        Temeva IAM API. This class provides that functionality to obtain
        the token.
    """
    def __init__(self, username, password, subdomain, base_url=None):
        if not base_url:
            base_url = 'https://{}.temeva.com'.format(subdomain)
        self.base_url = base_url

        scope = self._get_org_id(subdomain)

        token_url = base_url + '/api/iam/oauth2/token'

        self.oauth_info = self._get_oauth_info(token_url,
                                               username,
                                               password,
                                               scope)


    def _get_oauth_info(self, token_url, username, password, scope):
        data = {
            'grant_type': 'password',
            'username': username,
            'password': password,
            'scope': scope
        }
        headers = {'ACCEPT': 'application/json'}
        resp = requests.post(token_url, headers=headers, data=data)
        if (resp.status_code != 200):
            raise RuntimeError('Unexpected response {}: {}'.format(
                resp.status_code, resp.content))
        return resp.json()

        
    def _get_org_id(self, subdomain):
        url = self.base_url + '/api/iam/organizations'
        params = {'subdomain': subdomain}
        headers = {'ACCEPT': 'application/json'}
        resp = requests.get(url, headers=headers, params=params)
        if (resp.status_code != 200):
            raise RuntimeError('Unexpected response {}: {}'.format(
                resp.status_code, resp.content))

        orgs = resp.json()
        for org in orgs:
            if org['subdomain'] == subdomain:
                return org['id']
        return ''


    def get_user_id(self):
        url = self.base_url + '/api/iam/users/my'
        headers = {'ACCEPT': 'application/json', 'AUTHORIZATION': "Bearer {}".format(self.access_token())}
        resp = requests.get(url, headers=headers)
        if (resp.status_code != 200):
            raise RuntimeError('Unexpected response {}: {}'.format(
                resp.status_code, resp.content))

        user = resp.json()
        return user['id']


    def access_token(self):
        return self.oauth_info['access_token']


    def refresh_token(self):
        return self.oauth_info['refresh_token']


    def expires_in(self):
        return self.oauth_info['expires_in']


    def token_type(self):
        return self.oauth_info['token_type']
