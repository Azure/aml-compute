![Integration Test](https://github.com/Azure/aml-compute/workflows/Integration%20Test/badge.svg?branch=master&event=push)
![Lint and Test](https://github.com/Azure/aml-compute/workflows/Lint%20and%20Test/badge.svg?branch=master&event=push)

# GitHub Action for creating compute targets for Azure Machine Learning

## Deprecation notice

This Action is deprecated. Instead, consider using the [CLI (v2)](https://docs.microsoft.com/azure/machine-learning/how-to-configure-cli) to manage and interact with Azure Machine Learning compute in GitHub Actions.

**Important:** The CLI (v2) is not recommended for production use while in preview.

## Usage

The actions for creating compute for Azure Machine Learning will allow you to create a new compute target on [Azure Machine Learning](https://azure.microsoft.com/en-us/services/machine-learning/) using GitHub Actions.

Get started today with a [free Azure account](https://azure.com/free/open-source)!

This repository contains a GitHub Action for creating and connecting to Azure Machine Learning compute resources, so you can later train or deploy machine learning models models remotely. If the compute target exists, it will connect to it, otherwise the action can create a new compute target based on the provided parameters. Currently, the action only supports Azure ML Clusters and AKS Clusters. 


## Dependencies on other GitHub Actions
* [Checkout](https://github.com/actions/checkout) Checkout your Git repository content into GitHub Actions agent.
* [aml-workspace](https://github.com/Azure/aml-workspace) This action requires an Azure Machine Learning workspace to be present. You can either create a new one or re-use an existing one using the action. 


## Utilize GitHub Actions and Azure Machine Learning to train and deploy a machine learning model

This action is one in a series of actions that can be used to setup an ML Ops process. **We suggest getting started with one of our template repositories**, which will allow you to create an ML Ops process in less than 5 minutes.

1. **Simple template repository: [ml-template-azure](https://github.com/machine-learning-apps/ml-template-azure)**

    Go to this template and follow the getting started guide to setup an ML Ops process within minutes and learn how to use the Azure       Machine Learning GitHub Actions in combination. This template demonstrates a very simple process for training and deploying machine     learning models.

2. **Advanced template repository: [mlops-enterprise-template](https://github.com/Azure-Samples/mlops-enterprise-template)**

    This template demonstrates how the actions can be extended to include the normal pull request approval process and how training and deployment workflows can be split. More enhancements will be added to this template in the future to make it more enterprise ready.


### Example workflow for creating compute targets for Azure Machine Learning 

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
    - uses: Azure/aml-workspace@v1
      id: aml_workspace
      with:
        azure_credentials: ${{ secrets.AZURE_CREDENTIALS }}

    # AML Compute Action
    - uses: Azure/aml-compute@v1
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
| parameters_file |  | `"compute.json"` | We expect a JSON file in the `.cloud/.azure` folder in root of your repository specifying your Azure Machine Learning compute target details. If you have want to provide these details in a file other than "compute.json" you need to provide this input in the action. |

#### azure_credentials (Azure Credentials)

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

#### parameters_file (Parameter File)

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
| vm_size                         |          | str: [`"Basic_A0"`, `"Standard_DS3_v2"`, etc.](https://docs.microsoft.com/en-us/azure/templates/Microsoft.Compute/2019-07-01/virtualMachines?toc=%2Fen-us%2Fazure%2Fazure-resource-manager%2Ftoc.json&bc=%2Fen-us%2Fazure%2Fbread%2Ftoc.json#hardwareprofile-object) | `"Standard_DS3_v2"` | The size of agent VMs. Note that not all sizes are available in all regions. |
| vm_priority                     |          | str: `"dedicated"`, `"lowpriority"` | `"dedicated"` | The VM priority. |
| min_nodes                       |          | int: [0, inf[ | 0 | The minimum number of nodes to use on the cluster. |
| max_nodes                       |          | int: [1, inf[ | 4 | The maximum number of nodes to use on the cluster. |
| idle_seconds_before_scaledown   |          | int: [0, inf[ | 120 | Node idle time in seconds before scaling down the cluster. |
| vnet_resource_group_name        |          | str | null | The name of the resource group where the virtual network is located. |
| vnet_name                       |          | str | null | The name of the virtual network. |
| subnet_name                     |          | str | null | The name of the subnet inside the VNet. |
| remote_login_port_public_access |          | str: `"Enabled"`, `"Disabled"`, `"NotSpecified"` | `"NotSpecified"` | State of the public SSH port. `"Disabled"` indicates that the public ssh port is closed on all nodes of the cluster. `"Enabled"` indicates that the public ssh port is open on all nodes of the cluster. `"NotSpecified"` indicates that the public ssh port is closed on all nodes of the cluster if VNet is defined, else is open all public nodes. It can be this default value only during cluster creation time. After creation, it will be either enabled or disabled. |
| identity_type                   |          | str: `"SystemAssigned"`, `"UserAssigned"` | null | Specifies the type of identity that should be assigned to the AML Cluster. Supported is SystemAssigned or UserAssigned identity. |
| identity_id                     |          | list[ str ] | null | User assigned identities. |

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
