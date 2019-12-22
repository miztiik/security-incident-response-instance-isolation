#!/bin/bash
set -e
# set -x

#----- Change these parameters to suit your environment -----#

AWS_PROFILE="default"
AWS_REGION="us-east-1"
BUCKET_NAME="sam-templates-011" # bucket must exist in the SAME region the deployment is taking place
SERVICE_NAME="Miztiik-Incident-Response"
TEMPLATE_NAME="incident_response.yaml" # The CF Template should be the same name, If not update it.
# STACK_NAME="${SERVICE_NAME}"
STACK_NAME="incidentResponse"
TEMPLATE_DIR="./templates"
OUTPUT_DIR="./outputs"
PACKAGED_OUTPUT_TEMPLATE="${TEMPLATE_DIR}/${OUTPUT_DIR}/${STACK_NAME}-packaged-template.yaml"

# You can also change these parameters but it's not required
info_sec_ops_mail="youremail@gmail.com"

#------------------  End of user parameters  -----------------------#


function build_env(){
    echo -e "\n *******************************"
    echo -e " * Environment Build Initiated *"
    echo -e " *******************************"

}

function pack_and_deploy() {
    pack
    deploy
}

# Package the code
function pack() {

    # Create the output directory if it doesn't exist
    mkdir -p "${OUTPUT_DIR}"

    # Cleanup Output directory
    rm -rf "${OUTPUT_DIR}"/*

    echo -e "\n *****************************"
    echo -e " * Stack Packaging Initiated *"
    echo -e " *****************************"
    
    aws cloudformation package \
        --template-file "${TEMPLATE_DIR}/${TEMPLATE_NAME}" \
        --s3-bucket "${BUCKET_NAME}" \
        --output-template-file "${PACKAGED_OUTPUT_TEMPLATE}"
    
}

# Validate the template
function validate() {

    echo -e "\n ******************************"
    echo -e " * Validating Template *"
    echo -e " ******************************"

    aws cloudformation validate-template \
        --template-body "${PACKAGED_OUTPUT_TEMPLATE}"
    
}

# Deploy the stack
function deploy() {
    echo -e "\n ******************************"
    echo -e " * Stack Deployment Initiated *"
    echo -e " ******************************"
    
    aws cloudformation deploy \
        --profile "${AWS_PROFILE}" \
        --template-file "${PACKAGED_OUTPUT_TEMPLATE}" \
        --stack-name "${STACK_NAME}" \
        --tags Service="${SERVICE_NAME}" \
        --capabilities CAPABILITY_IAM \
        --region "${AWS_REGION}" \
        --parameter-overrides \
            SecurityContactEmail="${info_sec_ops_mail}"
        # --parameters ParameterKey=AcmCertificateArn,ParameterValue=ACM_CERT_ARN \
        #          ParameterKey=DomainName,ParameterValue=DOMAIN_NAME
    exit
}

function nuke_stack() {
    echo -e "\n ******************************"
    echo -e " *  Stack Deletion Initiated  *"
    echo -e " ******************************"
    aws cloudformation delete-stack \
        --stack-name "${STACK_NAME}" \
        --region "${AWS_REGION}"

    aws cloudformation wait stack-delete-complete  \
        --stack-name "${STACK_NAME}" \
        --region "${AWS_REGION}"
    exit
	}


function _cancel_update_stack() {
    echo -e "\n *****************************************"
    echo -e " *  Stack Update Cancellation Initiated  *"
    echo -e " *****************************************"

    aws cloudformation cancel-update-stack --stack-name "${STACK_NAME}" --region "${AWS_REGION}"

    exit
}

function gen_random_str1(){

    cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w ${1:-8} | head -n 1
}



function create_s3(){
    if aws s3api head-bucket --bucket "$bkt_name" 2>/dev/null; 
        then
            echo -e "Bucket '"$bkt_name"' Exists"
        else
            echo -e "bucket does not exit or permission is not there to view it."
            echo -e "Attempting to create bucket."
            aws s3 mb s3://"${BUCKET_NAME}" || { echo 'Bucket Creation failed' ; exit 1; }
    fi
}

# Check if we need to destroy the stack
if [ $# -eq 0 ]; then
 pack_and_deploy
  elif [ "$1" = "pack" ]; then
   pack
    elif [ "$1" = "deploy" ]; then
     deploy
      elif [ "$1" = "cancel" ]; then
       _cancel_update_stack
        elif [ "$1" = "nuke" ]; then
         nuke_stack
          elif [ "$1" = "build_env" ]; then
           build_env
fi
