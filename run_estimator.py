import boto3
import json
import sagemaker as sage
from sagemaker.estimator import Estimator



SM_ROLE = "arn:aws:iam::578276202366:role/armand-basic-sm-execution-role"
AWS_ACCOUNT = "578276202366"
REGION = "us-east-1"
S3_BUCKET = "aws-tf-sm"
S3_PREFIX = "marin/armand-ssh"
JOB = "armand-ssh-test"

INSTANCE_TYPE = "ml.m4.4xlarge"
SUBNET = "subnet-21ac2f2e"
SG_IDS = ["sg-0043f63c9ad9ffc1d", "sg-0d931ecdaccd26af3", "sg-0eaeb8cc84c955b74"]


IMAGE_REPO = "sagemaker-ssh"
IMAGE_TAG = "latest"











def pretty_print_json(j):
    print(json.dumps(j, indent=4))



if __name__ == '__main__':

    sess = sage.Session(boto3.session.Session(region_name=REGION))

    image = f'{AWS_ACCOUNT}.dkr.ecr.{REGION}.amazonaws.com/{IMAGE_REPO}:{IMAGE_TAG}'
    output_path = f's3://{S3_BUCKET}/{S3_PREFIX}/{JOB}'




    estimator = Estimator(image,
                          base_job_name=f'armand-ssh-test',
                          role=SM_ROLE,
                          train_volume_size=100,
                          train_instance_count=2,
                          train_instance_type=INSTANCE_TYPE,
                          sagemaker_session=sess,
                          output_path=output_path,
                          subnets=[SUBNET],
                          security_group_ids=SG_IDS,
                          input_mode='File')



    try:
        estimator.fit(logs=True)
    except Exception as ex:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("Error during estimator.fit")
        print(str(ex))
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        raise ex






