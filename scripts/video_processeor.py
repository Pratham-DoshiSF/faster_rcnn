import os
from utils.s3_utils import setup_s3_client
from dotenv import load_dotenv
from scripts.video_processing import process_video

load_dotenv()
CUSTOMER_ID = "test_client_1"
LOCATION_ID = "test_cam_1"
VIDEO_DATE = "20250711"
DOWNLOAD_OBJECT_KEY  = f"abc/{CUSTOMER_ID}/{LOCATION_ID}/{VIDEO_DATE}/"
TEMPORY_PATH = "temm_video"
BUCKET_NAME = "testing-cvat-load"
# os.makedirs(TEMPORY_PATH)
s3 , s3_client = setup_s3_client()

def process_video_one_by_one():

    for obj in s3.Bucket(BUCKET_NAME).objects.filter(Prefix = DOWNLOAD_OBJECT_KEY):
        path, filename = os.path.split(obj.key)
 
        if VIDEO_DATE in filename:
            print("We found video" , filename)
            download_location = f"{TEMPORY_PATH}/{filename}"
            s3_client.download_file(
                    Filename=download_location,
                    Bucket=BUCKET_NAME,
                    Key=obj.key
            )

            trimmed_video_path = process_video(CUSTOMER_ID,LOCATION_ID ,download_location)

            if os.path.exists(trimmed_video_path):
                os.remove(download_location)
            else:
                print("No motion detected for " , filename)

process_video_one_by_one()