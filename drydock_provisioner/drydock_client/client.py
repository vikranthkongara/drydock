# Copyright 2017 AT&T Intellectual Property.  All other rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
import requests
import logging

from drydock_provisioner import error as errors


class DrydockClient(object):
    """"
    A client for the Drydock API

    :param DrydockSession session: A instance of DrydockSession to be used by this client
    """

    def __init__(self, session):
        self.session = session
        self.logger = logging.getLogger(__name__)

    def get_design_ids(self):
        """
        Get list of Drydock design_ids

        :return: A list of string design_ids
        """
        endpoint = 'v1.0/designs'

        resp = self.session.get(endpoint)

        self._check_response(resp)

        return resp.json()

    def get_design(self, design_id, source='designed'):
        """
        Get a full design based on the passed design_id

        :param string design_id: A UUID design_id
        :param string source: The model source to return. 'designed' is as input, 'compiled' is after merging
        :return: A dict of the design and all currently loaded design parts
        """
        endpoint = "v1.0/designs/%s" % design_id

        resp = self.session.get(endpoint, query={'source': source})

        self._check_response(resp)

        return resp.json()

    def create_design(self, base_design=None):
        """
        Create a new design context for holding design parts

        :param string base_design: String UUID of the base design to build this design upon
        :return string: String UUID of the design ID
        """
        endpoint = 'v1.0/designs'

        if base_design is not None:
            resp = self.session.post(
                endpoint, data={'base_design_id': base_design})
        else:
            resp = self.session.post(endpoint)

        self._check_response(resp)

        design = resp.json()
        return design.get('id', None)

    def get_part(self, design_id, kind, key, source='designed'):
        """
        Query the model definition of a design part

        :param string design_id: The string UUID of the design context to query
        :param string kind: The design part kind as defined in the Drydock design YAML schema
        :param string key: The design part key, generally a name.
        :param string source: The model source to return. 'designed' is as input, 'compiled' is after merging
        :return: A dict of the design part
        """

        endpoint = "v1.0/designs/%s/parts/%s/%s" % (design_id, kind, key)

        resp = self.session.get(endpoint, query={'source': source})

        self._check_response(resp)

        return resp.json()

    def load_parts(self, design_id, yaml_string=None):
        """
        Load new design parts into a design context via YAML conforming to the Drydock design YAML schema

        :param string design_id: String uuid design_id of the design context
        :param string yaml_string: A single or multidoc YAML string to be ingested
        :return: Dict of the parsed design parts
        """

        endpoint = "v1.0/designs/%s/parts" % (design_id)

        resp = self.session.post(
            endpoint, query={'ingester': 'yaml'}, body=yaml_string)

        self._check_response(resp)

        return resp.json()

    def get_tasks(self):
        """
        Get a list of all the tasks, completed or running.

        :return: List of string uuid task IDs
        """

        endpoint = "v1.0/tasks"

        resp = self.session.get(endpoint)

        self._check_response(resp)

        return resp.json()

    def get_task(self, task_id):
        """
        Get the current description of a Drydock task

        :param string task_id: The string uuid task id to query
        :return: A dict representing the current state of the task
        """

        endpoint = "v1.0/tasks/%s" % (task_id)

        resp = self.session.get(endpoint)

        self._check_response(resp)

        return resp.json()

    def create_task(self, design_id, task_action, node_filter=None):
        """
        Create a new task in Drydock

        :param string design_id: A string uuid identifying the design context the task should operate on
        :param string task_action: The action that should be executed
        :param dict node_filter: A filter for narrowing the scope of the task. Valid fields are 'node_names',
                                 'rack_names', 'node_tags'.
        :return: The string uuid of the create task's id
        """

        endpoint = 'v1.0/tasks'

        task_dict = {
            'action': task_action,
            'design_id': design_id,
            'node_filter': node_filter,
        }

        self.logger.debug("drydock_client is calling %s API: body is %s" %
                          (endpoint, str(task_dict)))

        resp = self.session.post(endpoint, data=task_dict)

        self._check_response(resp)

        return resp.json().get('task_id')

    def _check_response(self, resp):
        if resp.status_code == 401:
            raise errors.ClientUnauthorizedError(
                "Unauthorized access to %s, include valid token." % resp.url)
        elif resp.status_code == 403:
            raise errors.ClientForbiddenError(
                "Forbidden access to %s" % resp.url)
        elif not resp.ok:
            raise errors.ClientError(
                "Error - received %d: %s" % (resp.status_code, resp.text),
                code=resp.status_code)
