import boto3
from dotenv import load_dotenv


load_dotenv()


class s3_setup():
    def __init__(self):
        self.service_name = "s3"
    
    def get_s3(self):
        try:
            self.s3 = boto3.resource(service_name = self.service_name)
            self.s3_client = boto3.client(self.service_name)
            return self.s3 , self.s3_client
        except Exception as e:
            print("Failed in intialization")


# s3 , s3_client = s3_setup().get_s3()

# print(s3 ,s3_client)