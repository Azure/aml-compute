import os
import sys
import pytest

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(myPath, "..", "code"))

from utils import AMLConfigurationException, AMLComputeException, load_json, validate_json, create_compute_target, create_aml_cluster, create_aks_cluster
from azureml.core import Workspace
from azureml.core.compute import ComputeTarget, AmlCompute, AksCompute
from azureml.exceptions import ComputeTargetException


def test_load_json_valid_input():
    """
    Unit test to check the load_json function with valid input
    """
    file_path = os.path.join("code", "schemas", "azure_credential_schema.json")
    json_object = load_json(
        file_path=file_path
    )
    assert type(json_object) == dict


def test_load_json_invalid_input():
    """
    Unit test to check the load_json function with invalid input
    """
    with pytest.raises(FileNotFoundError):
        assert load_json(
            file_path=""
        )


def test_validate_json_valid_inputs():
    """
    Unit test to check the validate_json function with valid inputs
    """
    json_object = {
        "clientId": "",
        "clientSecret": "",
        "subscriptionId": "",
        "tenantId": ""
    }
    schema_path = os.path.join("code", "schemas", "azure_credential_schema.json")
    schema_object = load_json(
        file_path=schema_path
    )
    validate_json(
        data=json_object,
        schema=schema_object,
        input_name="PARAMETERS_FILE"
    )


def test_validate_json_invalid_json():
    """
    Unit test to check the validate_json function with invalid json_object inputs
    """
    json_object = {
        "clientId": "",
        "clientSecret": "",
        "subscriptionId": ""
    }
    schema_path = os.path.join("code", "schemas", "azure_credential_schema.json")
    schema_object = load_json(
        file_path=schema_path
    )
    with pytest.raises(AMLConfigurationException):
        assert validate_json(
            data=json_object,
            schema=schema_object,
            input_name="PARAMETERS_FILE"
        )


def test_validate_json_invalid_schema():
    """
    Unit test to check the validate_json function with invalid schema inputs
    """
    json_object = {}
    schema_object = {}
    with pytest.raises(Exception):
        assert validate_json(
            data=json_object,
            schema=schema_object,
            input_name="PARAMETERS_FILE"
        )


def test_create_compute_target_invalid_workspace():
    """
    Unit test to check the create_compute_target function with invalid workspace
    """
    workspace = object()
    name = "testname"
    config = AmlCompute.provisioning_configuration(max_nodes=1)
    with pytest.raises(AMLConfigurationException):
        assert create_compute_target(
            workspace=workspace,
            name=name,
            config=config
        )


def test_create_compute_target_invalid_name():
    """
    Unit test to check the create_compute_target function with invalid name
    """
    workspace = Workspace(
        subscription_id="",
        resource_group="",
        workspace_name="",
        _disable_service_check=True
    )
    name = ""
    config = AmlCompute.provisioning_configuration(max_nodes=1)
    with pytest.raises(AMLConfigurationException):
        assert create_compute_target(
            workspace=workspace,
            name=name,
            config=config
        )


def test_create_compute_target_invalid_config():
    """
    Unit test to check the create_compute_target function with invalid config
    """
    workspace = Workspace(
        subscription_id="",
        resource_group="",
        workspace_name="",
        _disable_service_check=True
    )
    name = ""
    config = object()
    with pytest.raises(AMLConfigurationException):
        assert create_compute_target(
            workspace=workspace,
            name=name,
            config=config
        )

def test_create_aml_cluster_invalid_workspace():
    """
    Unit test to check the create_aml_cluster function with invalid workspace
    """
    workspace = object()
    parameters = {}
    with pytest.raises(AMLConfigurationException):
        assert create_aml_cluster(
            workspace=workspace,
            parameters=parameters
        )


def test_create_aml_cluster_invalid_parameters():
    """
    Unit test to check the create_aml_cluster function with invalid parameters
    """
    workspace = Workspace(
        subscription_id="",
        resource_group="",
        workspace_name="",
        _disable_service_check=True
    )
    parameters = {
        "vnet_resource_group_name": "",
        "vnet_name": "",
        "subnet_name": 2
    }
    with pytest.raises(AMLConfigurationException):
        assert create_aml_cluster(
            workspace=workspace,
            parameters=parameters
        )
