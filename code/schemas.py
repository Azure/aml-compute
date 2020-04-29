azure_credentials_schema = {
    "$id": "http://azure-ml.com/schemas/azure_credentials.json",
    "$schema": "http://json-schema.org/schema",
    "title": "azure_credentials",
    "description": "JSON specification for your azure credentials",
    "type": "object",
    "required": ["clientId", "clientSecret", "subscriptionId", "tenantId"],
    "properties": {
        "clientId": {
            "type": "string",
            "description": "The client ID of the service principal."
        },
        "clientSecret": {
            "type": "string",
            "description": "The client secret of the service principal."
        },
        "subscriptionId": {
            "type": "string",
            "description": "The subscription ID that should be used."
        },
        "tenantId": {
            "type": "string",
            "description": "The tenant ID of the service principal."
        }
    }
}

parameters_schema = {
    "$id": "http://azure-ml.com/schemas/compute.json",
    "$schema": "http://json-schema.org/schema",
    "title": "aml-compute",
    "description": "JSON specification for your compute details",
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "The name of the of the Compute object to retrieve or create.",
            "minLength": 2,
            "maxLength": 16
        },
        "compute_type": {
            "type": "string",
            "description": "Specifies the type of compute target that should be created by the action if a compute target with the specified name was not found.",
            "pattern": "amlcluster|akscluster"
        },
        "vm_size": {
            "type": "string",
            "description": "The size of agent VMs. Note that not all sizes are available in all regions."
        },
        "vm_priority": {
            "type": "string",
            "description": "The VM priority.",
            "pattern": "dedicated|lowpriority"
        },
        "min_nodes": {
            "type": "integer",
            "description": "The minimum number of nodes to use on the cluster.",
            "minimum": 0
        },
        "max_nodes": {
            "type": "integer",
            "description": "The maximum number of nodes to use on the cluster.",
            "minimum": 1
        },
        "idle_seconds_before_scaledown": {
            "type": "integer",
            "description": "Node idle time in seconds before scaling down the cluster.",
            "minimum": 0
        },
        "vnet_resource_group_name": {
            "type": "string",
            "description": "The name of the resource group where the virtual network is located."
        },
        "vnet_name": {
            "type": "string",
            "description": "The name of the virtual network."
        },
        "subnet_name": {
            "type": "string",
            "description": "The name of the subnet inside the VNet."
        },
        "remote_login_port_public_access": {
            "type": "string",
            "description": "State of the public SSH port.",
            "pattern": "Enabled|Disabled|NotSpecified"
        },
        "agent_count": {
            "type": "integer",
            "description": "The number of agents (VMs) to host containers.",
            "minimum": 1
        },
        "location": {
            "type": "string",
            "description": "The location to provision cluster in."
        },
        "service_cidr": {
            "type": "string",
            "description": "A CIDR notation IP range from which to assign service cluster IPs."
        },
        "dns_service_ip": {
            "type": "string",
            "description": "Containers DNS server IP address."
        },
        "docker_bridge_cidr": {
            "type": "string",
            "description": "A CIDR notation IP for Docker bridge."
        },
        "cluster_purpose": {
            "type": "string",
            "description": "Targeted usage of the cluster.",
            "pattern": "DevTest|FastProd"
        },
        "ssl_cname": {
            "type": "string",
            "description": "A CName to use if enabling SSL validation on the cluster. Must provide all three CName, cert file, and key file to enable SSL validation."
        },
        "ssl_cert_pem_file": {
            "type": "string",
            "description": "A file path to a file containing cert information for SSL validation. Must provide all three CName, cert file, and key file to enable SSL validation."
        },
        "ssl_key_pem_file": {
            "type": "string",
            "description": "A file path to a file containing key information for SSL validation. Must provide all three CName, cert file, and key file to enable SSL validation."
        },
        "load_balancer_type": {
            "type": "string",
            "description": "Load balancer type of AKS cluster.",
            "pattern": "PublicIp|InternalLoadBalancer"
        },
        "load_balancer_subnet": {
            "type": "string",
            "description": "Load balancer subnet of AKS cluster. It can be used only when Internal Load Balancer is used as load balancer type."
        }
    }
}