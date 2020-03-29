![Integration Test](https://github.com/Azure/aml-compute/workflows/Integration%20Test/badge.svg)
![Lint](https://github.com/Azure/aml-compute/workflows/Lint/badge.svg)

# Azure Machine Learning Compute Action

## Usage

The Azure Machine Learning Compute action will allow you to create a new compute target or check whether the specified compute target is available so you can later run your Machine Learning experiments or deploy your models remotely. If the compute target exists, it will just connect to it, otherwise the action can create a new compute target based on the provided parameters. Currently, the action only supports Azure ML Clusters and AKS Clusters. You will need to have azure credentials that allow you to create and/or connect to a workspace.

### Example workflow

```yaml
name: My Workflow
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@master
    - name: Run action

    # AML Workspace Action
    - uses: Azure/aml-workspace
      with:
        azure_credentials: ${{ secrets.AZURE_CREDENTIALS }}

      # AML Compute Action
    - uses: Azure/aml-compute
      with:
        # required inputs as secrets
        azure_credentials: ${{ secrets.AZURE_CREDENTIALS }}
        # optional
        parameters_file: compute.json
```

### Inputs

| Input | Required | Default | Description |
| ----- | -------- | ------- | ----------- |
| azure_credentials | x | - | Output of `az ad sp create-for-rbac --name <your-sp-name> --role contributor --scopes /subscriptions/<your-subscriptionId>/resourceGroups/<your-rg> --sdk-auth`. This should be stored in your secrets |
| parameters_file |  | `"compute.json"` | JSON file in the `.ml/.azure` folder specifying your Azure Machine Learning compute target details. |

#### Azure Credentials

Install the [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest) and execute the following command to generate the credentials:

```sh
# Replace {service-principal-name}, {subscription-id} and {resource-group} with your Azure subscription id and resource group and any name
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

Add the JSON output as [a secret](https://help.github.com/en/actions/configuring-and-managing-workflows/creating-and-storing-encrypted-secrets#creating-encrypted-secrets) with the name `AZURE_CREDENTIALS` in the GitHub repository.

#### Parameter File

The action expects a JSON file in the `.ml/.azure` folder in your repository, which specifies details of your Azure Machine Learning compute target. By default, the action expects a file with the name `compute.json`. If your JSON file has a different name, you can specify it with this parameter. Currently, the action only supports Azure ML Clusters and AKS Clusters.

Sample files for AML and AKS clusters can be found in this repository in the folder `.ml/.azure`. The JSON file can include the following parameters:

##### AML Cluster

| Parameter | Required | Allowed Values       | Description |
| --------- | -------- | -------------------- | ----------- |
| name                            | x        | str                 | |
| compute_type                    | x        | str: `"amlcluster"` |
| vm_size                         |          | str: 
| vm_priority                     |          | str: 
| min_nodes                       |          | int: [0, inf[
| max_nodes                       |          | int: [1, inf[
| idle_seconds_before_scaledown   |          | int: [0, inf[
| vnet_resource_group_name        |          | str
| vnet_name                       |          | str
| subnet_name                     |          | str
| admin_username                  |          | str
| admin_user_password             |          | str
| admin_user_ssh_key              |          | str
| remote_login_port_public_access |          | str

Please visit [this website]() for more details.

##### AKS Cluster

| Parameter | Required | Allowed Values       | Description |
| --------- | -------- | -------------------- | ----------- |
| name                            | x        | str                 | |
| compute_type                    | x        |

Please visit [this website]() for more details.

### Outputs

This action does not provide any outputs.

### Other Azure Machine Learning Actions

- [aml-workspace](https://github.com/Azure/aml-workspace) - Connects to or creates a new workspace
- [aml-compute](https://github.com/Azure/aml-compute) - Connects to or creates a new compute target in Azure Machine Learning
- [aml-run](https://github.com/Azure/aml-run) - Submits a ScriptRun, an Estimator or a Pipeline to Azure Machine Learning
- [aml-registermodel](https://github.com/Azure/aml-registermodel) - Registers a model to Azure Machine Learning
- [aml-deploy](https://github.com/Azure/aml-deploy) - Deploys a model and creates an endpoint for the model

# Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

https://docs.microsoft.com/en-us/azure/templates/Microsoft.ContainerService/2020-02-01/managedClusters?toc=%2Fen-us%2Fazure%2Fazure-resource-manager%2Ftoc.json&bc=%2Fen-us%2Fazure%2Fbread%2Ftoc.json#managedclusteragentpoolprofile-object
