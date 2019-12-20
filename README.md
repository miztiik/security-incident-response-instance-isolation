
# AWS Security - Incident Response

  Lets isolate that errant instances and dump it for analysis
  
  ![Recover or Rotate SSH Keys using SSM](images/setup-ssh-key-recovery-using-userdata-valaxy-00.png)

  Follow this article in **[Youtube](https://youtu.be/a4gOXBrVe6w)**



![dynamodb-streams-processor](images/ec2_credentials_exfiltration.png)

## Follow this article in [Youtube](https://youtube.com/c/valaxytechnologies)

0. ### Prerequisites

- AWS CLI pre-configured - [Get help here](https://youtu.be/TPyyfmQte0U)
- GuardDuty Enabled in the same region[Get help here](https://youtu.be/ybh_556IMpk)

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
    ```

1. ## Deployment

    We will use the `deploy.sh` in the `helper_scripts` directory to deploy our [AWS SAM](https://github.com/awslabs/serverless-application-model) template

    ```bash
    chmod +x ./helper_scripts/deploy.sh
    ./helper_scripts/deploy.sh
    ```
  
1. ## Insert few Items

    Insert a simple item to the table, either from the GUI/CLI

    ```json
    ddb_name="dynamodb-table-cleanup-001-DynamoDBTable-15IKZNGW1NLET"
    for i in {1..10}
     do
      val=${RANDOM}
      aws dynamodb put-item \
        --table-name "${ddb_name}" \
        --item '{ "Username": {"S":"User_'${i}'"},"Timestamp": {"S":"'$(date +"%d/%m/%Y-%H:%M:%S")'"},"Message":{"S":"Mystique_Msg_'${val}'"} }'
     done
    ```

1. Backup DDB Schema & Delete Table

    ```bash
    yum -y install jq
    aws dynamodb describe-table --table-name "${ddb_name}" | jq '.Table | del(.TableId, .TableArn, .ItemCount, .TableSizeBytes, .CreationDateTime, .TableStatus, .LatestStreamArn, .LatestStreamLabel, .ProvisionedThroughput.NumberOfDecreasesToday, .ProvisionedThroughput.LastIncreaseDateTime)' > schema.json

    aws dynamodb delete-table --table-name "${ddb_name}"
    ```

    At this moment, if you check the stack for drift, you will notice it had identified the table had been deleted.
    ![dynamodb-streams-processor](images/drift-deleted.png)

1. ReCreate Table & Verify Stack still owns the DDB

    Using the schema of the old table, We should be able to create a new table with the same attributes. _If you have a hugh table, wait for couple of minutes and confirm table deletion before executing the below command for table creation._

    ```bash
    aws dynamodb create-table --cli-input-json file://schema.json
    ```

    Under Cloudformation, We have a new `Detect Drift` option(_[More on this here](https://www.youtube.com/watch?v=YN4UOXSb74A)_). Initiate Drift Detection. You will find that the `Dynamo DB` resources had been tagged as modified but still under the managed of cloudformation stack.

    ![dynamodb-streams-processor](images/drift-modified.png)

### CleanUp

  If you want to destroy all the resources created by the stack, Execute the below command to delete the stack, or _you can delete the stack from console as well_

  ```bash
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