import boto3
from dotenv import load_dotenv


load_dotenv()


def setup_s3_client():
    try:
        s3 = boto3.resource(service_name = 's3' )
        s3_client = boto3.client("s3")
        return s3 , s3_client
    except Exception as e:
        print("Failed in intialization " , e)
        raise

