
# AWS Security - Incident Response

  Lets isolate that errant instances and dump it for analysis
  
  ![Recover or Rotate SSH Keys using SSM](images/setup-ssh-key-recovery-using-userdata-valaxy-00.png)

  Follow this article in **[Youtube](https://youtu.be/a4gOXBrVe6w)**



![dynamodb-streams-processor](images/ec2_credentials_exfiltration.png)

## Follow this article in [Youtube](https://youtube.com/c/valaxytechnologies)

0. ### Prerequisites

- AWS CLI pre-configured - [Get help here](https://youtu.be/TPyyfmQte0U)
- GuardDuty Enabled in the same region[Get help here](https://youtu.be/ybh_556IMpk)
- EC2 Instance Running with an IAM Role

1. ## Clone the repository

   ```bash
   git clone git@github.com:miztiik/security-incident-response-instance-isolation.git
   cd security-incident-response-instance-isolation
   ```

1. ## Customize the deployment

    Edit the `./helper_scripts/deploy.sh` to update your environment variables.
  
    ```bash
    AWS_PROFILE="default"
    AWS_REGION="us-east-1"
    BUCKET_NAME="sam-templates-011" # bucket must exist in the SAME region the deployment is taking place
    SERVICE_NAME="dynamodb-cleanup-demo"
    TEMPLATE_NAME="${SERVICE_NAME}.yaml" # The CF Template should be the same name, If not update it.
    STACK_NAME="${SERVICE_NAME}-001"
    OUTPUT_DIR="./outputs/"
    PACKAGED_OUTPUT_TEMPLATE="${OUTPUT_DIR}${STACK_NAME}-packaged-template.yaml"
    SNS_EMAIL="abc@example.com"
    ```

1. ## Deployment

    We will use the `deploy.sh` in the `helper_scripts` directory to deploy our [AWS SAM](https://github.com/awslabs/serverless-application-model) template

    ```bash
    chmod +x ./helper_scripts/deploy.sh
    ./helper_scripts/deploy.sh
    ```
  
1. Testing the Solution

    - Connect to EC2 instance and execute the following command, Dont forget to update the `role_name` with the IAM Role attached to the EC2 instance.

    ```bash
    role_name="s3_access"
    curl http://169.254.169.254/latest/meta-data/iam/security-credentials/${role_name}
    ```

    - Open a local terminal,(not the EC2 instance).  
    From the prevous output, replace the values for these, and run them,
    _**Note**: Make sure the token does not have line breaks_

    ```bash
    export AWS_ACCESS_KEY_ID="YOUR-ACCESS-KEY"
    export AWS_SECRET_ACCESS_KEY="YOU-SECRET-KEY"
    export AWS_SESSION_TOKEN="YOUR-TOKEN"
    ```

    - Lets check if we can query S3 with these new credentials,

    ```bash
      aws sts get-caller-identity
      aws s3 ls
      unset AWS_ACCESS_KEY_ID
      unset AWS_SECRET_ACCESS_KEY
      unset AWS_SESSION_TOKEN
      aws sts get-caller-identity
      date
      ```

    _**Note**: Typically, it takes about ~20 to 30 minutes for GuardDuty to raise a finding. Within 5 Minutes of a finding, A CloudWatch Event is triggered._


### CleanUp

  If you want to destroy all the resources created by the stack, Execute the below command to delete the stack, or _you can delete the stack from console as well_

  ```bash
  # Delete QURANTINE EBS Snapshots
  # Delete QUARANTINE Security Group

  # Delete the CF Stack
  ./helper_scripts/deploy.sh nuke
  ```

### Buy me a coffee

Buy me a coffee ☕ here `https://paypal.me/valaxy`, _or_ You can reach out to get more details through [here](https://youtube.com/c/valaxytechnologies/about).

#### References

1. [Amazon GuardDuty findings](https://docs.aws.amazon.com/guardduty/latest/ug//get-findings.html#get-findings-response-syntax)
1. [CloudWatch Events Event Examples From Supported Services](https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/EventTypes.html)
1. [Configure a CloudWatch events rule for GuardDuty](https://aws.amazon.com/premiumsupport/knowledge-center/guardduty-cloudwatch-sns-rule/)

### Metadata

**Level**: 400