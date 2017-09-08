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
import time


class Report(object):
    def __init__(self, session):
        self.session = session
        self.report_url = session.url + '/api/reports'
        self.jobs_url = session.url + '/api/jobs'
        self.files_url = session.url + '/api/files'
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def _poll_job(self, job_id):
        VALID_STATUS = ['IN_PROGRESS', 'COMPLETE', 'FAILED']
        while True:
            r = self.session.get(self.jobs_url + '/' + job_id)
            if (r.status_code != 200):
                raise RuntimeError('Unexpected response {}: {}'.format(
                    r.status_code, r.content))
            job = r.json()
            status = job['status']
            if status not in VALID_STATUS:
                raise RuntimeError('Invalid report job status: {}.'.format(status))
            if status == 'FAILED':
                error = job['error_message']
                raise RuntimeError('Report generation job failed: {}'.format(error))
            if status == 'COMPLETE':
                return job['result']['filename']
            time.sleep(5)


    def _save_file(self, file_id, file_name):
        headers = {
            'Accept': 'application/octet-stream'
        }
        r = self.session.get(self.files_url + '/' + file_id,
                                headers=headers)
        if (r.status_code != 200):
            raise RuntimeError('Unexpected response {}: {}'.format(
                r.status_code, r.content))
        with open(file_name, 'wb') as report:
            report.write(r.content)


    def _save_report(self, report_id, report_type, file_name=None):
        VALID_DOC_TYPE = ['DOCX', 'XLSX', 'PDF']
        if report_type not in VALID_DOC_TYPE:
            raise RuntimeError('Invalid report type: {}.'.format(report_type))

        data = {
            'document_type': report_type
        }
        r = self.session.post(
            self.report_url + '/{}/doc-generation'.format(report_id), json=data)

        if (r.status_code != 202):
            raise RuntimeError('Unexpected response {}: {}'.format(
                r.status_code, r.content))

        job_info = r.json()
        file_id = self._poll_job(job_info['job_id'])

        if not file_name:
            report = self.get_by_id(report_id)
            file_name = '{} {}'.format(report['info']['test_name'],
                                       report['info']['end_time'])
            if not file_name:
                file_name = 'report'
            file_name += '.{}'.format(report_type.lower())

        self._save_file(file_id, file_name)


    def get_by_id(self, id):
        r = self.session.get(self.report_url + '/{}'.format(id),
                                headers=self.headers)
        if (r.status_code != 200):
            raise RuntimeError('Unexpected response {}: {}'.format(
                r.status_code, r.content))
        return r.json()


    def get_reports_for_test(self, test_id, meta_only=False):
        params = {'test_id': test_id }
        headers = self.headers
        if meta_only:
            headers = copy.copy(self.headers)
            headers['X-Spirent-Metadata-Only'] = 'true'
        r = self.session.get(self.report_url, headers=headers,
                                params=params)
        if (r.status_code != 200):
            raise RuntimeError('Unexpected response {}: {}'.format(
                r.status_code, r.content))
        return r.json()


    def save_as_pdf(self, report_id, file_name=None):
        self._save_report(report_id, 'PDF', file_name)


    def save_as_xlsx(self, report_id, file_name=None):
        self._save_report(report_id, 'XLSX', file_name)


    def save_as_docx(self, report_id, file_name=None):
        self._save_report(report_id, 'DOCX', file_name)
