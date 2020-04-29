import os
import json
import jsonschema

from azureml.core.compute import ComputeTarget, AmlCompute, AksCompute
from azureml.exceptions import ComputeTargetException


class AMLConfigurationException(Exception):
    pass


class AMLComputeException(Exception):
    pass


def create_compute_target(workspace, name, config):
    # Creating compute target
    print("::debug::Creating compute target")
    try:
        compute_target = ComputeTarget.create(
            workspace=workspace,
            name=name,
            provisioning_configuration=config
        )
        compute_target.wait_for_completion(show_output=True)
    except AttributeError as exception:
        print(f"::error::Could not create compute target with specified parameters: {exception}")
        raise AMLConfigurationException(f"Could not create compute target with specified parameters. Please review the provided parameters.")
    except ComputeTargetException as exception:
        print(f"::error::Could not create compute target with specified parameters: {exception}")
        raise AMLConfigurationException(f"Could not create compute target with specified parameters. Please review the provided parameters.")

    # Checking state of compute target
    print("::debug::Checking state of compute target")
    if compute_target.provisioning_state != "Succeeded":
        print(f"::error::Deployment of compute target '{compute_target.name}' failed with state '{compute_target.provisioning_state}'. Please delete the compute target manually and retry.")
        raise AMLComputeException(f"Deployment of compute target '{compute_target.name}' failed with state '{compute_target.provisioning_state}'. Please delete the compute target manually and retry.")
    return compute_target


def create_aml_cluster(workspace, parameters):
    print("::debug::Creating aml cluster configuration")
    aml_config = AmlCompute.provisioning_configuration(
        vm_size=parameters.get("vm_size", None),
        vm_priority=parameters.get("vm_priority", "dedicated"),
        min_nodes=parameters.get("min_nodes", 0),
        max_nodes=parameters.get("max_nodes", 4),
        idle_seconds_before_scaledown=parameters.get("idle_seconds_before_scaledown", None),
        tags={"Created": "GitHub Action: Azure/aml-compute"},
        description="AML Cluster created by Azure/aml-compute GitHub Action",
        remote_login_port_public_access=parameters.get("remote_login_port_public_access", "NotSpecified")
    )

    print("::debug::Adding VNET settings to configuration if all required settings were provided")
    if parameters.get("vnet_resource_group_name", None) is not None and parameters.get("vnet_name", None) is not None and parameters.get("subnet_name", None) is not None:
        aml_config.vnet_resourcegroup_name = parameters.get("vnet_resource_group_name", None)
        aml_config.vnet_name = parameters.get("vnet_name", None)
        aml_config.subnet_name = parameters.get("subnet_name", None)

    print("::debug::Adding credentials to configuration if all required settings were provided")
    if os.environ.get("ADMIN_USER_NAME", None) is not None and os.environ.get("ADMIN_USER_PASSWORD", None) is not None:
        aml_config.admin_username = os.environ.get("ADMIN_USER_NAME", None)
        aml_config.admin_user_password = os.environ.get("ADMIN_USER_PASSWORD", None)
    elif os.environ.get("ADMIN_USER_NAME", None) is not None and os.environ.get("ADMIN_USER_SSH_KEY", None) is not None:
        aml_config.admin_username = os.environ.get("ADMIN_USER_NAME", None)
        aml_config.admin_user_ssh_key = os.environ.get("ADMIN_USER_SSH_KEY", None)

    print("::debug::Creating compute target")
    # Default compute target name
    repository_name = str(os.environ.get("GITHUB_REPOSITORY")).split("/")[-1][:16]
    aml_cluster = create_compute_target(
        workspace=workspace,
        name=parameters.get("name", repository_name),
        config=aml_config
    )
    return aml_cluster


def create_aks_cluster(workspace, parameters):
    print("::debug::Creating aks cluster configuration")
    aks_config = AksCompute.provisioning_configuration(
        agent_count=parameters.get("agent_count", None),
        vm_size=parameters.get("vm_size", None),
        location=parameters.get("location", None),
        service_cidr=parameters.get("service_cidr", None),
        dns_service_ip=parameters.get("dns_service_ip", None),
        docker_bridge_cidr=parameters.get("docker_bridge_cidr", None)
    )

    print("::debug::Changing cluster purpose if specified settings were provided")
    if "dev" in parameters.get("cluster_purpose", "").lower() or "test" in parameters.get("cluster_purpose", "").lower():
        aks_config.cluster_purpose = AksCompute.ClusterPurpose.DEV_TEST

    print("::debug::Adding VNET settings to configuration if all required settings were provided")
    if parameters.get("vnet_resource_group_name", None) is not None and parameters.get("vnet_name", None) is not None and parameters.get("subnet_name", None) is not None:
        aks_config.vnet_resourcegroup_name = parameters.get("vnet_resource_group_name", None)
        aks_config.vnet_name = parameters.get("vnet_name", None)
        aks_config.subnet_name = parameters.get("subnet_name", None)

    print("::debug::Adding SSL settings to configuration if all required settings were provided")
    if parameters.get("ssl_cname", None) is not None and parameters.get("ssl_cert_pem_file", None) is not None and parameters.get("ssl_key_pem_file", None) is not None:
        aks_config.ssl_cname = parameters.get("ssl_cname", None)
        aks_config.ssl_cert_pem_file = parameters.get("ssl_cert_pem_file", None)
        aks_config.ssl_key_pem_file = parameters.get("ssl_key_pem_file", None)

    print("::debug::Adding load balancer settings to configuration if all required settings were provided")
    if parameters.get("load_balancer_type", None) == "InternalLoadBalancer" and parameters.get("load_balancer_subnet", None) is not None:
        aks_config.load_balancer_type = parameters.get("load_balancer_type", None)
        aks_config.load_balancer_subnet = parameters.get("load_balancer_subnet", None)

    print("::debug::Creating compute target")
    # Default compute target name
    repository_name = str(os.environ.get("GITHUB_REPOSITORY")).split("/")[-1]
    aks_cluster = create_compute_target(
        workspace=workspace,
        name=parameters.get("name", repository_name),
        config=aks_config
    )
    return aks_cluster


def mask_parameter(parameter):
    print(f"::add-mask::{parameter}")


def load_json(file_path):
    with open(file_path) as f:
        json_object = json.load(f)
    return json_object


def validate_json(data, schema, input_name):
    validator = jsonschema.Draft7Validator(schema)
    errors = validator.iter_errors(data)
    if len(list(errors)) > 0:
        for error in errors:
            print(f"::error::JSON validation error: {error}")
        raise AMLConfigurationException(f"JSON validation error for '{input_name}'. Provided object does not match schema. Please check the output for more details.")
    else:
        print(f"::debug::JSON validation passed for '{input_name}'. Provided object does match schema.")
