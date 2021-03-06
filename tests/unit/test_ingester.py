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

from drydock_provisioner.ingester import Ingester
from drydock_provisioner.statemgmt import DesignState
import drydock_provisioner.objects as objects

import logging
import pytest
import shutil
import os
import drydock_provisioner.ingester.plugins.yaml


class TestClass(object):
    def test_ingest_full_site(self, input_files):
        objects.register_all()

        input_file = input_files.join("fullsite.yaml")

        design_state = DesignState()
        design_data = objects.SiteDesign()
        design_id = design_data.assign_id()
        design_state.post_design(design_data)

        ingester = Ingester()
        ingester.enable_plugins(
            ['drydock_provisioner.ingester.plugins.yaml.YamlIngester'])
        ingester.ingest_data(
            plugin_name='yaml',
            design_state=design_state,
            filenames=[str(input_file)],
            design_id=design_id)

        design_data = design_state.get_design(design_id)

        assert len(design_data.host_profiles) == 2
        assert len(design_data.baremetal_nodes) == 2

    def test_ingest_federated_design(self, input_files):
        objects.register_all()

        profiles_file = input_files.join("fullsite_profiles.yaml")
        networks_file = input_files.join("fullsite_networks.yaml")
        nodes_file = input_files.join("fullsite_nodes.yaml")

        design_state = DesignState()
        design_data = objects.SiteDesign()
        design_id = design_data.assign_id()
        design_state.post_design(design_data)

        ingester = Ingester()
        ingester.enable_plugins(
            ['drydock_provisioner.ingester.plugins.yaml.YamlIngester'])
        ingester.ingest_data(
            plugin_name='yaml',
            design_state=design_state,
            design_id=design_id,
            filenames=[
                str(profiles_file),
                str(networks_file),
                str(nodes_file)
            ])

        design_data = design_state.get_design(design_id)

        assert len(design_data.host_profiles) == 2

    @pytest.fixture(scope='module')
    def input_files(self, tmpdir_factory, request):
        tmpdir = tmpdir_factory.mktemp('data')
        samples_dir = os.path.dirname(
            str(request.fspath)) + "/" + "../yaml_samples"
        samples = os.listdir(samples_dir)

        for f in samples:
            src_file = samples_dir + "/" + f
            dst_file = str(tmpdir) + "/" + f
            shutil.copyfile(src_file, dst_file)

        return tmpdir
