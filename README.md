![Integration Test](https://github.com/Azure/aml-compute/workflows/Integration%20Test/badge.svg)
![Lint](https://github.com/Azure/aml-compute/workflows/Lint/badge.svg)

# Azure Machine Learning Compute Action

## Usage

The Azure Machine Learning Compute action will allow you to create a new compute target or check whether the specified compute target is available so you can later run your Machine Learning experiments or deploy your models remotely. If the compute target exists, it will just connect to it, otherwise the action can create a new compute target based on the provided parameters. Currently, the action only supports Azure ML Clusters and AKS Clusters. You will need to have azure credentials that allow you to create and/or connect to a workspace.

This action requires an AML workspace to be created or attached to via the [aml-workspace](https://github.com/Azure/aml-workspace) action.

## Template repositories

This action is one in a series of actions that can be used to setup an ML Ops process. Examples of these can be found at
1. Simple example: [ml-template-azure](https://github.com/machine-learning-apps/ml-template-azure) and
2. Comprehensive example: [aml-template](https://github.com/Azure/aml-template).

### Example workflow

```yaml
name: My Workflow
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    # Checks-out your repository under $GITHUB_WORKSPACE, so your job can access it
    - name: Check Out Repository
      id: checkout_repository
      uses: actions/checkout@v2

    # AML Workspace Action
    - uses: Azure/aml-workspace
      id: aml_workspace
      with:
        azure_credentials: ${{ secrets.AZURE_CREDENTIALS }}

    # AML Compute Action
    - uses: Azure/aml-compute
      id: aml_compute
      with:
        # required inputs as secrets
        azure_credentials: ${{ secrets.AZURE_CREDENTIALS }}
        # optional
        parameters_file: "compute.json"
```

### Inputs

| Input | Required | Default | Description |
| ----- | -------- | ------- | ----------- |
| azure_credentials | x | - | Output of `az ad sp create-for-rbac --name <your-sp-name> --role contributor --scopes /subscriptions/<your-subscriptionId>/resourceGroups/<your-rg> --sdk-auth`. This should be stored in your secrets |
| parameters_file |  | `"compute.json"` | JSON file in the `.cloud/.azure` folder specifying your Azure Machine Learning compute target details. |

#### Azure Credentials

Azure credentials are required to connect to your Azure Machine Learning Workspace. These may have been created for an action you are already using in your repository, if so, you can skip the steps below.

Install the [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest) on your computer or use the Cloud CLI and execute the following command to generate the required credentials:

```sh
# Replace {service-principal-name}, {subscription-id} and {resource-group} with your Azure subscription id and resource group name and any name for your service principle
az ad sp create-for-rbac --name {service-principal-name} \
                         --role contributor \
                         --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group} \
                         --sdk-auth
```

This will generate the following JSON output:

```sh
{
  "clientId": "<GUID>",
  "clientSecret": "<GUID>",
  "subscriptionId": "<GUID>",
  "tenantId": "<GUID>",
  (...)
}
```

Add this JSON output as [a secret](https://help.github.com/en/actions/configuring-and-managing-workflows/creating-and-storing-encrypted-secrets#creating-encrypted-secrets) with the name `AZURE_CREDENTIALS` in your GitHub repository.

#### Parameter File

The action tries to load a JSON file in the `.cloud/.azure` folder in your repository, which specifies details of your Azure Machine Learning compute target. By default, the action is looking for a file with the name `compute.json`. If your JSON file has a different name, you can specify it with this input parameter. Currently, the action only supports Azure ML Clusters and AKS Clusters. Note that none of these values are required and in the absence, defaults will be created with the repo name.

Sample files for AML and AKS clusters can be found in this repository in the folder `.cloud/.azure`. The JSON file can include the following parameters:

##### Common parameters

| Parameter | Required | Allowed Values       | Default | Description |
| --------- | -------- | -------------------- | ------- | ----------- |
| name                            |  | str | <REPOSITORY_NAME> | The name of the of the Compute object to retrieve or create. max characters is 16 and it can include letters, digits and dashes. It must start with a letter and end with a letter or number |
| compute_type                    | (only for creating compute target) | str: `"amlcluster"`, `"akscluster"` | - | Specifies the type of compute target that should be created by the action if a compute target with the specified name was not found. |

##### AML Cluster

| Parameter | Required | Allowed Values       | Default | Description |
| --------- | -------- | -------------------- | ------- | ----------- |
| vm_size                         |          | str: [`"Basic_A0"`, `"Standard_DS3_v2"`, etc.](https://docs.microsoft.com/en-us/azure/templates/Microsoft.Compute/2019-07-01/virtualMachines?toc=%2Fen-us%2Fazure%2Fazure-resource-manager%2Ftoc.json&bc=%2Fen-us%2Fazure%2Fbread%2Ftoc.json#hardwareprofile-object) | `"Standard_NC6"` | The size of agent VMs. Note that not all sizes are available in all regions. |
| vm_priority                     |          | str: `"dedicated"`, `"lowpriority"` | `"dedicated"` | The VM priority. |
| min_nodes                       |          | int: [0, inf[ | 0 | The minimum number of nodes to use on the cluster. |
| max_nodes                       |          | int: [1, inf[ | 4 | The maximum number of nodes to use on the cluster. |
| idle_seconds_before_scaledown   |          | int: [0, inf[ | 120 | Node idle time in seconds before scaling down the cluster. |
| vnet_resource_group_name        |          | str | null | The name of the resource group where the virtual network is located. |
| vnet_name                       |          | str | null | The name of the virtual network. |
| subnet_name                     |          | str | null | The name of the subnet inside the VNet. |
| remote_login_port_public_access |          | str: `"Enabled"`, `"Disabled"`, `"NotSpecified"` | `"NotSpecified"` | State of the public SSH port. `"Disabled"` indicates that the public ssh port is closed on all nodes of the cluster. `"Enabled"` indicates that the public ssh port is open on all nodes of the cluster. `"NotSpecified"` indicates that the public ssh port is closed on all nodes of the cluster if VNet is defined, else is open all public nodes. It can be this default value only during cluster creation time. After creation, it will be either enabled or disabled. |

Please visit [this website]() for more details.

##### AKS Cluster

| Parameter | Required | Allowed Values       | Default | Description |
| --------- | -------- | -------------------- | ------- | ----------- |
| agent_count |  | int: [1, inf[ | 3 | The number of agents (VMs) to host containers. |
| vm_size |  | str: [`"Standard_A1_v2"`, `"Standard_D3_v2"`, etc.](https://docs.microsoft.com/en-us/azure/templates/Microsoft.ContainerService/2020-02-01/managedClusters?toc=%2Fen-us%2Fazure%2Fazure-resource-manager%2Ftoc.json&bc=%2Fen-us%2Fazure%2Fbread%2Ftoc.json#managedclusteragentpoolprofile-object) | `"Standard_D3_v2"` | The size of agent VMs. |
| location |  | str: [supported region](https://azure.microsoft.com/en-us/global-infrastructure/services/?regions=all&products=kubernetes-service) | location of workspace | The location to provision cluster in. |
| service_cidr |  | str | null | A CIDR notation IP range from which to assign service cluster IPs. |
| dns_service_ip |  | str | null | Containers DNS server IP address. |
| docker_bridge_cidr |  | str | null | A CIDR notation IP for Docker bridge. |
| cluster_purpose |  | str: `"DevTest"`, `"FastProd"` | `"FastProd"` | Targeted usage of the cluster. This is used to provision Azure Machine Learning components to ensure the desired level of fault-tolerance and QoS. `"FastProd"` will provision components to handle higher levels of traffic with production quality fault-tolerance. This will default the AKS cluster to have 3 nodes. `"DevTest"` will provision components at a minimal level for testing. This will default the AKS cluster to have 1 node. |
| vnet_resource_group_name |  | str | null | The name of the resource group where the virtual network is located. |
| vnet_name |  | str | null | The name of the virtual network. |
| subnet_name |  | str | null | The name of the subnet inside the vnet. |
| ssl_cname |  | str | null | A CName to use if enabling SSL validation on the cluster. Must provide all three CName, cert file, and key file to enable SSL validation. |
| ssl_cert_pem_file |  | str | null | A file path to a file containing cert information for SSL validation. Must provide all three CName, cert file, and key file to enable SSL validation. |
| ssl_key_pem_file |  | str | null | A file path to a file containing key information for SSL validation. Must provide all three CName, cert file, and key file to enable SSL validation. |
| load_balancer_type |  | str: `"PublicIp"`, `"InternalLoadBalancer"` | `"PublicIp"` | Load balancer type of AKS cluster. |
| load_balancer_subnet |  | str | equal to subnet_name | Load balancer subnet of AKS cluster. It can be used only when Internal Load Balancer is used as load balancer type. |

Please visit [this website](https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.compute.amlcompute%28class%29?view=azure-ml-py#provisioning-configuration-vm-size-----vm-priority--dedicated---min-nodes-0--max-nodes-none--idle-seconds-before-scaledown-none--admin-username-none--admin-user-password-none--admin-user-ssh-key-none--vnet-resourcegroup-name-none--vnet-name-none--subnet-name-none--tags-none--description-none--remote-login-port-public-access--notspecified--) for more details.

### Outputs

This action does not provide any outputs.

### Environment variables

Certain parameters are considered secrets and should therefore be passed as environment variables from your secrets, if you want to use custom values.

| Environment variable        | Required | Allowed Values | Default | Description |
| --------------------------- | -------- | -------------- | ------- | ----------- |
| ADMIN_USER_NAME             |          | str            | null    | The name of the administrator user account which can be used to SSH into nodes. This parameter is AML Cluster specific. |
| ADMIN_USER_PASSWORD         |          | str            | null    | The password of the administrator user account. This parameter is AML Cluster specific. |
| ADMIN_USER_SSH_KEY          |          | str            | null    | The SSH public key of the administrator user account. This parameter is AML Cluster specific. |

### Other Azure Machine Learning Actions

- [aml-workspace](https://github.com/Azure/aml-workspace) - Connects to or creates a new workspace
- [aml-compute](https://github.com/Azure/aml-compute) - Connects to or creates a new compute target in Azure Machine Learning
- [aml-run](https://github.com/Azure/aml-run) - Submits a ScriptRun, an Estimator or a Pipeline to Azure Machine Learning
- [aml-registermodel](https://github.com/Azure/aml-registermodel) - Registers a model to Azure Machine Learning
- [aml-deploy](https://github.com/Azure/aml-deploy) - Deploys a model and creates an endpoint for the model

### Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
