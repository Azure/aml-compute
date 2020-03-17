from azureml.core.compute import ComputeTarget, AmlCompute, AksCompute


def create_aml_cluster(workspace, parameters):
    print("::debug::Creating aml cluster configuration")
    aml_config = AmlCompute.provisioning_configuration(
        vm_size=parameters.get("vm_size", "STANDARD_D2_V2"),
        vm_priority=parameters.get("vm_priority", "dedicated"),
        min_nodes=parameters.get("min_nodes", 0),
        max_nodes=parameters.get("max_nodes", 4),
        idle_seconds_before_scaledown=parameters.get("idle_seconds_before_scaledown", 300),
        tags={"Created": "GitHub Action: Azure/aml-compute"},
        description="AML Cluster created by Azure/aml-compute GitHubb Action",
        remote_login_port_public_access=parameters.get("remote_login_port_public_access", "NotSpecified")
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
    if parameters.get("vnet_resource_group_name", None) and parameters.get("vnet_name", None) and parameters.get("subnet_name", None):
        aks_config.vnet_resourcegroup_name = parameters.get("vnet_resource_group_name", None)
        aks_config.vnet_name = parameters.get("vnet_name", None)
        aks_config.subnet_name = parameters.get("subnet_name", None)
    
    print("::debug::Adding SSL settings to configuration if all required settings were provided")
    if parameters.get("ssl_cname", None) and parameters.get("ssl_cert_pem_file", None) and parameters.get("ssl_key_pem_file", None):
        aks_config.ssl_cname = parameters.get("ssl_cname", None)
        aks_config.ssl_cert_pem_file = parameters.get("ssl_cert_pem_file", None)
        aks_config.ssl_key_pem_file = parameters.get("ssl_key_pem_file", None)
    
    print("::debug::Adding load balancer settings to configuration if all required settings were provided")
    if parameters.get("load_balancer_type", None) == "InternalLoadBalancer" and parameters.get("load_balancer_subnet", None):
        aks_config.load_balancer_type = parameters.get("load_balancer_type", None)
        aks_config.load_balancer_subnet = parameters.get("load_balancer_subnet", None)
    
    print("::debug::Creating compute target")
    aks_cluster = ComputeTarget.create(
        workspace=workspace,
        name=parameters.get("name", None),
        provisioning_configuration=aks_config
    )
    return aks_cluster
