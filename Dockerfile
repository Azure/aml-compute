  
FROM marvinbuss/aml-docker:latest

LABEL "com.github.actions.name"="Azure Machine Learning Compute"
LABEL "com.github.actions.description"="Create or scale up an Azure Machine Learning compute cluster with this GitHub Action"
LABEL "com.github.actions.icon"="arrow-up-right"
LABEL "com.github.actions.color"="gray-dark"

LABEL version="1.0.0"
LABEL repository="https://github.com/Azure/aml-compute"
LABEL homepage="https://github.com/Azure/aml-compute"
LABEL maintainer=""

COPY /code /code
ENTRYPOINT ["/code/entrypoint.sh"]
