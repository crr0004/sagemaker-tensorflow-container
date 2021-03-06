#  Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License").
#  You may not use this file except in compliance with the License.
#  A copy of the License is located at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  or in the "license" file accompanying this file. This file is distributed
#  on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
#  express or implied. See the License for the specific language governing
#  permissions and limitations under the License.
from __future__ import absolute_import

import logging
import os

import boto3
import pytest
from sagemaker import LocalSession, Session
from sagemaker.tensorflow import TensorFlow

logger = logging.getLogger(__name__)
logging.getLogger('boto').setLevel(logging.INFO)
logging.getLogger('botocore').setLevel(logging.INFO)
logging.getLogger('factory.py').setLevel(logging.INFO)
logging.getLogger('auth.py').setLevel(logging.INFO)
logging.getLogger('connectionpool.py').setLevel(logging.INFO)

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))


def pytest_addoption(parser):
    parser.addoption('--docker-base-name', default='preprod-tensorflow')
    parser.addoption('--tag', default=None)
    parser.addoption('--region', default='us-west-2')
    parser.addoption('--framework-version', default=TensorFlow.LATEST_VERSION)
    parser.addoption('--processor', default='cpu', choices=['gpu', 'cpu'])
    parser.addoption('--py-version', default='3', choices=['2', '3'])
    parser.addoption('--account-id', default='142577830533')
    parser.addoption('--instance-type', default=None)


@pytest.fixture(scope='session')
def docker_base_name(request):
    return request.config.getoption('--docker-base-name')


@pytest.fixture(scope='session')
def processor(request):
    return request.config.getoption('--processor')


@pytest.fixture(scope='session')
def region(request):
    return request.config.getoption('--region')


@pytest.fixture(scope='session')
def py_version(request):
    return request.config.getoption('--py-version')


@pytest.fixture(scope='session')
def framework_version(request):
    return request.config.getoption('--framework-version')


@pytest.fixture(scope='session')
def tag(request, framework_version, processor, py_version):
    provided_tag = request.config.getoption('--tag')
    default_tag = '{}-{}-py{}'.format(framework_version, processor, py_version)
    return provided_tag if provided_tag is not None else default_tag


@pytest.fixture(scope='session')
def sagemaker_session(region):
    return Session(boto_session=boto3.Session(region_name=region))


@pytest.fixture(scope='session')
def sagemaker_local_session(region):
    return LocalSession(boto_session=boto3.Session(region_name=region))


@pytest.fixture(scope='session')
def account_id(request):
    return request.config.getoption('--account-id')


@pytest.fixture(scope='session')
def instance_type(request, processor):
    provided_instance_type = request.config.getoption('--instance-type')
    default_instance_type = 'ml.c4.xlarge' if processor == 'cpu' else 'ml.p2.xlarge'
    return provided_instance_type if provided_instance_type is not None else default_instance_type


@pytest.fixture(autouse=True)
def skip_by_device_type(request, processor):
    is_gpu = (processor == 'gpu')
    if (request.node.get_closest_marker('skip_gpu') and is_gpu) or \
            (request.node.get_closest_marker('skip_cpu') and not is_gpu):
        pytest.skip('Skipping because running on \'{}\' instance'.format(processor))


@pytest.fixture(scope='session')
def docker_image(docker_base_name, tag):
    return '{}:{}'.format(docker_base_name, tag)


@pytest.fixture(scope='session')
def ecr_image(account_id, docker_base_name, tag, region):
    return '{}.dkr.ecr.{}.amazonaws.com/{}:{}'.format(
        account_id, region, docker_base_name, tag)
