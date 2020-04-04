import os
import json

from azureml.core import Workspace
from azureml.core.compute import ComputeTarget
from azureml.exceptions import ComputeTargetException, AuthenticationException, ProjectSystemException
from azureml.core.authentication import ServicePrincipalAuthentication
from adal.adal_error import AdalError
from msrest.exceptions import AuthenticationError
from json import JSONDecodeError
from utils import AMLConfigurationException, required_parameters_provided, create_aml_cluster, create_aks_cluster, mask_parameter


def main():
    # Loading input values
    print("::debug::Loading input values")
    parameters_file = os.environ.get("INPUT_PARAMETERS_FILE", default="compute.json")
    azure_credentials = os.environ.get("INPUT_AZURE_CREDENTIALS", default="{}")
    try:
        azure_credentials = json.loads(azure_credentials)
    except JSONDecodeError:
        print("::error::Please paste output of `az ad sp create-for-rbac --name <your-sp-name> --role contributor --scopes /subscriptions/<your-subscriptionId>/resourceGroups/<your-rg> --sdk-auth` as value of secret variable: AZURE_CREDENTIALS")
        raise AMLConfigurationException(f"Incorrect or poorly formed output from azure credentials saved in AZURE_CREDENTIALS secret. See setup in https://github.com/Azure/aml-compute/blob/master/README.md")

    # Checking provided parameters
    print("::debug::Checking provided parameters")
    required_parameters_provided(
        parameters=azure_credentials,
        keys=["tenantId", "clientId", "clientSecret"],
        message="Required parameter(s) not found in your azure credentials saved in AZURE_CREDENTIALS secret for logging in to the workspace. Please provide a value for the following key(s): "
    )

    # Mask values
    print("::debug::Masking parameters")
    mask_parameter(parameter=azure_credentials.get("tenantId", ""))
    mask_parameter(parameter=azure_credentials.get("clientId", ""))
    mask_parameter(parameter=azure_credentials.get("clientSecret", ""))
    mask_parameter(parameter=azure_credentials.get("subscriptionId", ""))

    # Loading parameters file
    print("::debug::Loading parameters file")
    parameters_file_path = os.path.join(".cloud", ".azure", parameters_file)
    try:
        with open(parameters_file_path) as f:
            parameters = json.load(f)
    except FileNotFoundError:
        print(f"::debug::Could not find parameter file in {parameters_file_path}. Please provide a parameter file in your repository if you do not want to use default settings (e.g. .cloud/.azure/compute.json).")
        parameters = {}

    # Loading Workspace
    print("::debug::Loading AML Workspace")
    sp_auth = ServicePrincipalAuthentication(
        tenant_id=azure_credentials.get("tenantId", ""),
        service_principal_id=azure_credentials.get("clientId", ""),
        service_principal_password=azure_credentials.get("clientSecret", "")
    )
    config_file_path = os.environ.get("GITHUB_WORKSPACE", default=".cloud/.azure")
    config_file_name = "aml_arm_config.json"
    try:
        ws = Workspace.from_config(
            path=config_file_path,
            _file_name=config_file_name,
            auth=sp_auth
        )
    except AuthenticationException as exception:
        print(f"::error::Could not retrieve user token. Please paste output of `az ad sp create-for-rbac --name <your-sp-name> --role contributor --scopes /subscriptions/<your-subscriptionId>/resourceGroups/<your-rg> --sdk-auth` as value of secret variable: AZURE_CREDENTIALS: {exception}")
        raise AuthenticationException
    except AuthenticationError as exception:
        print(f"::error::Microsoft REST Authentication Error: {exception}")
        raise AuthenticationError
    except AdalError as exception:
        print(f"::error::Active Directory Authentication Library Error: {exception}")
        raise AdalError
    except ProjectSystemException as exception:
        print(f"::error::Workspace authorizationfailed: {exception}")
        raise ProjectSystemException

    # Loading compute target
    try:
        # Default compute target name
        repository_name = os.environ.get("GITHUB_REPOSITORY").split("/")[-1]

        print("::debug::Loading existing compute target")
        compute_target = ComputeTarget(
            workspace=ws,
            name=parameters.get("name", repository_name)
        )
        print(f"::debug::Found compute target with same name. Not updating the compute target: {compute_target.serialize()}")
    except ComputeTargetException:
        print("::debug::Could not find existing compute target with provided name")

        # Checking provided parameters
        print("::debug::Checking provided parameters")
        required_parameters_provided(
            parameters=parameters,
            keys=["compute_type"],
            message="Required parameter(s) not found in your parameters file for loading a compute target. Please provide a value for the following key(s): "
        )

        print("::debug::Creating new compute target")
        compute_type = parameters.get("compute_type", "")
        if compute_type == "amlcluster":
            compute_target = create_aml_cluster(
                workspace=ws,
                parameters=parameters
            )
            print(f"::debug::Successfully created AML cluster: {compute_target.serialize()}")
        if compute_type == "akscluster":
            compute_target = create_aks_cluster(
                workspace=ws,
                parameters=parameters
            )
            print(f"::debug::Successfully created AKS cluster: {compute_target.serialize()}")
        else:
            print(f"::error::Compute type '{compute_type}' is not supported")
            raise AMLConfigurationException(f"Compute type '{compute_type}' is not supported.")
    print("::debug::Successfully finished Azure Machine Learning Compute Action")


if __name__ == "__main__":
    main()
