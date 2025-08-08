#!/bin/bash

# Azure deployment script for lngvty-flask
# This script helps deploy the containerized application to Azure Container Instances

# Configuration - modify these variables
RESOURCE_GROUP="lngvty"
CONTAINER_NAME="lngvty-flask"
REGISTRY_NAME="csabattilaszabo/lngvty-flask"
IMAGE_NAME="lngvty-flask"
IMAGE_TAG="latest"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting Azure deployment for lngvty-flask...${NC}"

# Create Azure Container Instance
echo -e "${YELLOW}Creating Azure Container Instance...${NC}"
az container create \
    --resource-group $RESOURCE_GROUP \
    --name $CONTAINER_NAME \
    --image ${IMAGE_NAME}:${IMAGE_TAG} \
    --dns-name-label $CONTAINER_NAME \
    --ports 5000 \
    --environment-variables FLASK_APP=app.py FLASK_ENV=production \
    --registry-login-server ${REGISTRY_NAME}.azurecr.io \
    --registry-username $(az acr credential show --name $REGISTRY_NAME --query username -o tsv) \
    --registry-password $(az acr credential show --name $REGISTRY_NAME --query passwords[0].value -o tsv) \
    --cpu 1 \
    --memory 1.5

# Get the FQDN
FQDN=$(az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --query ipAddress.fqdn -o tsv)

echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${GREEN}Your application is available at: http://$FQDN:5000${NC}"
