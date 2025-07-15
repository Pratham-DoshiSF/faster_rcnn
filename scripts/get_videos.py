import os
from dotenv import load_dotenv

from utils_function.s3_utils import s3_setup
from scripts.motion_detector import motion_extractor


load_dotenv()
TEMPORY_PATH = "temm_video"
BUCKET_NAME = "testing-cvat-load"
os.makedirs(TEMPORY_PATH, exist_ok=True)

class video_extractor():
    def __init__(self , customer_id  ):
        self.CUSTOMER_ID = customer_id
        self.DOWNLOAD_OBJECT_KEY = f"abc/{self.CUSTOMER_ID}"
        self.motion_extractor_obj = motion_extractor()
        self.setup()
        
    def setup(self):
        self.s3 , self.s3_client = s3_setup().get_s3()

    def process_videos(self ,LOCATION_ID, VIDEO_DATE):
        self.DOWNLOAD_OBJECT_KEY = f"{self.DOWNLOAD_OBJECT_KEY}/{LOCATION_ID}/{VIDEO_DATE}"
        for obj in self.s3.Bucket(BUCKET_NAME).objects.filter(Prefix = self.DOWNLOAD_OBJECT_KEY):
            path, filename = os.path.split(obj.key)
            if VIDEO_DATE in filename:
                print("Downloading Video" , filename)
                download_location = f"{TEMPORY_PATH}/{filename}"
                self.s3_client.download_file(
                        Filename=download_location,
                        Bucket=BUCKET_NAME,
                        Key=obj.key
                )

                trimmed_video_path = self.motion_extractor_obj.process_video(self.CUSTOMER_ID,self.LOCATION_ID ,download_location)

                if os.path.exists(trimmed_video_path):
                    os.remove(download_location)
                else:
                    print("No motion detected for " , filename)


# video_extractor_obj = video_extractor("test_client_1" , "test_cam_1" )

# video_extractor_obj.process_videos("20250711")