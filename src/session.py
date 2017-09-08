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


class Session(object):
    def __init__(self, temeva, talisman_ip):
        self.temeva = temeva
        self.url = 'http://%s' % talisman_ip


    def get_user_id(self):
        return self.temeva.get_user_id()


    def _append_api_key(self, kwargs):
        headers = kwargs.get('headers', None)
        token = 'Bearer {}'.format(
            self.temeva.access_token())
        if headers:
            headers['Authorization'] = token
        else:
            kwargs['headers'] = { 'Authorization': token }


    def post(self, url, **kwargs):
        self._append_api_key(kwargs)
        return requests.post(url, **kwargs)


    def get(self, url, **kwargs):
        self._append_api_key(kwargs)
        return requests.get(url, **kwargs)


    def put(self, url, **kwargs):
        self._append_api_key(kwargs)
        return requests.put(url, **kwargs)


    def delete(self, url, **kwargs):
        self._append_api_key(kwargs)
        return requests.delete(url, **kwargs)