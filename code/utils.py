from azureml.core.compute import ComputeTarget, AmlCompute

def create_aml_cluster(workspace, parameters):
    print("::debug::Creating aml cluster configuration")
    aml_config = AmlCompute.provisioning_configuration(
        vm_size=parameters.get("vm_size", "STANDARD_D2_V2"),
        vm_priority=parameters.get("vm_priority", "dedicated"),
        min_nodes=parameters.get("min_nodes", 0),
        max_nodes=parameters.get("max_nodes", 4),
        idle_seconds_before_scaledown=parameters.get("idle_seconds_before_scaledown", 300),
        tags={"Created": "GitHub Action: Azure/aml-compute"},
        description="AML Cluster created by Azure/aml-compute GitHubb Action"
    )
    
    print("::debug::Adding VNET settings to configuration if all required settings were provided")
    if parameters.get("vnet_resource_group_name", None) and parameters.get("vnet_name", None) and parameters.get("subnet_name", None):
        aml_config.vnet_resourcegroup_name = parameters.get("vnet_resource_group_name", None)
        aml_config.vnet_name = parameters.get("vnet_name", None)
        aml_config.subnet_name = parameters.get("subnet_name", None)
    
    print("::debug::Adding credentials to configuration if all required settings were provided")
    if parameters.get("admin_username", None) and parameters.get("admin_user_password", None):
        aml_config.admin_username = parameters.get("admin_username", None)
        aml_config.admin_user_password = parameters.get("admin_user_password", None)
    elif parameters.get("admin_username", None) and parameters.get("admin_user_ssh_key", None):
        aml_config.admin_username = parameters.get("admin_username", None)
        aml_config.admin_user_ssh_key = parameters.get("admin_user_ssh_key", None)

    print("::debug::Creating compute target")
    aml_cluster = ComputeTarget.create(
        workspace=workspace,
        name=parameters.get("name", None),
        provisioning_configuration=aml_config
    )
    return aml_cluster

