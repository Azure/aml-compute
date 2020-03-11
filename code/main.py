import os
import json
from azureml.core import Workspace
from azureml.core.compute import ComputeTarget, AmlCompute
from azureml.exceptions import ComputeTargetException, AuthenticationException, ProjectSystemException
from azureml.core.authentication import ServicePrincipalAuthentication
from adal.adal_error import AdalError
from msrest.exceptions import AuthenticationError


def main():
    # Loading input values
    print("::debug::Loading input values")
    parameters_file = os.environ.get("INPUT_PARAMETERSFILE", default="workspace.json")
    azure_credentials = os.environ.get("INPUT_AZURECREDENTIALS", default="{}")
    azure_credentials = json.loads(azure_credentials)

    # Loading parameters file
    print("::debug::Loading parameters file")
    parameters_file_path = os.path.join(".aml", parameters_file)
    try:
        with open(parameters_file_path) as f:
            parameters = json.load(f)
    except FileNotFoundError:
        print(f"::error::Could not find parameter file in {parameters_file_path}. Please provide a parameter file in your repository (e.g. .aml/workspace.json).")
        return

    # Loading Workspace
    sp_auth = ServicePrincipalAuthentication(
        tenant_id=azure_credentials.get("tenantId", ""),
        service_principal_id=azure_credentials.get("clientId", ""),
        service_principal_password=azure_credentials.get("clientSecret", "")
    )
    try:
        print("::debug::Loading existing Workspace")
        ws = Workspace.get(
            name=parameters.get("name", None),
            subscription_id=azure_credentials.get("subscriptionId", ""),
            resource_group=parameters.get("resourceGroup", None),
            auth=sp_auth
        )
        print("::debug::Successfully loaded existing Workspace")
    except AuthenticationException as exception:
        print(f"::error::Could not retrieve user token. Please paste output of `az ad sp create-for-rbac --name <your-sp-name> --role contributor --scopes /subscriptions/<your-subscriptionId>/resourceGroups/<your-rg> --sdk-auth` as value of secret variable: AZURE_CREDENTIALS: {exception}")
        return
    except AuthenticationError as exception:
        print(f"::error::Microsoft REST Authentication Error: {exception}")
        return
    except AdalError as exception:
        print(f"::error::Active Directory Authentication Library Error: {exception}")
        return
    except ProjectSystemException as exception:
        print(f"::error::Workspace authorizationfailed: {exception}")
        return

    # TODO: Create compute if not existing.
    try:
        # Loading AMLCompute
        print("::debug::Loading existing AML Compute")
        cluster = AmlCompute(workspace=ws, name=parameters["name"])

        # Check settings and redeploy if required settings have changed
        print("::debug::Found existing cluster")
        if cluster.vm_size.lower() != parameters["vm_size"].lower() or cluster.vm_priority.lower() != parameters["vm_priority"].lower():
            cluster.delete()
            cluster.wait_for_completion(show_output=True)
            raise ComputeTargetException("Cluster is of incorrect size or has incorrect priority. Deleting cluster and provisioning a new one.")
        
        # Update AMLCompute
        #if cluster.provisioning_configuration.min_nodes != aml_settings["min_nodes"] or cluster.provisioning_configuration.max_nodes != aml_settings["max_nodes"] or cluster.provisioning_configuration.idle_seconds_before_scaledown != aml_settings["idle_seconds_before_scaledown"]:
        print("::debug::Updating settings of Cluster")
        cluster.update(min_nodes=parameters["min_nodes"],
                    max_nodes=parameters["max_nodes"],
                    idle_seconds_before_scaledown=parameters["idle_seconds_before_scaledown"])
        
        # Wait until the operation has completed
        cluster.wait_for_completion(show_output=True)
        
        print("::debug::Successfully updated Cluster definition")
    except ComputeTargetException:
        print("::debug::Loading failed")
        print("::debug::Creating new AML Compute resource")
        compute_config = AmlCompute.provisioning_configuration(vm_size=parameters["vm_size"],
                                                            vm_priority=parameters["vm_priority"],
                                                            min_nodes=parameters["min_nodes"],
                                                            max_nodes=parameters["max_nodes"],
                                                            idle_seconds_before_scaledown=parameters["idle_seconds_before_scaledown"],
                                                            tags=parameters["tags"],
                                                            description=parameters["description"])
        
        # Deploy to VNET if provided 
        if parameters["vnet_resource_group_name"] and parameters["vnet_name"] and parameters["subnet_name"]:
            compute_config.vnet_resourcegroup_name = parameters["vnet_resource_group_name"]
            compute_config.vnet_name = parameters["vnet_name"]
            compute_config.subnet_name = parameters["subnet_name"]
        
        # Set Credentials if provided
        if parameters["admin_username"] and parameters["admin_user_password"]:
            compute_config.admin_username = parameters["admin_username"]
            compute_config.admin_user_password = parameters["admin_user_password"]
        elif parameters["admin_username"] and parameters["admin_user_ssh_key"]:
            compute_config.admin_username = parameters["admin_username"]
            compute_config.admin_user_ssh_key = parameters["admin_user_ssh_key"]
        
        # Create Compute Target
        cluster = ComputeTarget.create(workspace=ws, name=parameters["name"], provisioning_configuration=compute_config)

        # Wait until the cluster is attached
        cluster.wait_for_completion(show_output=True)

    # Checking status of AMLCompute Cluster
    print("::debug::Checking status of AMLCompute Cluster")
    if cluster.provisioning_state == "Failed":
        cluster.delete()
        raise Exception(
            "::debug::Deployment of AMLCompute Cluster failed with the following status: {} and logs: \n{}".format(
                cluster.provisioning_state, cluster.provisioning_errors
            )
        )

    print(parameters)
    print("::debug::Successfully finished Azure Machine Learning Compute Action")


if __name__ == "__main__":
    main()
