import cv2
import numpy as np
import json
import os
from datetime import datetime
from utils_function.data_utils import database_function

TRIM_VIDEO_PATH = "trimmed_video/"
TRIM_VIDEO_METADATA_PATH = "trimmed_video_metadata/"
THRESHOLD = 20000000
LOG_PATH = "logs/"

for folder in [TRIM_VIDEO_PATH, TRIM_VIDEO_METADATA_PATH, LOG_PATH]:
    os.makedirs(folder, exist_ok=True)


class motion_extractor():
    def __init__(self):
        self.database_obj = database_function()

    def write_log(self ,log_file, message):
        with open(log_file, "a") as f:
            f.write(f"{datetime.now()} - {message}\n")
    
    def process_video(self ,customer_id, location_id, path):
        self.start_time = datetime.now()
        self.video_name = os.path.splitext(os.path.basename(path))[0]
        self.log_file = os.path.join(LOG_PATH, f"{self.video_name}.log")
        self.roi_points = self.database_obj.fetch_cordinates(customer_id, location_id)
        self.write_log(self.log_file, f"Processing started for video: {path}")

        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            self.write_log( self.log_file, "Error: Could not open video.")
            return

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration_sec = total_frames / fps

        output_video_path = f'{TRIM_VIDEO_PATH}{self.video_name}.avi'
        output_log = f"{TRIM_VIDEO_METADATA_PATH}{self.video_name}.json"

        out = cv2.VideoWriter(output_video_path, 
                            cv2.VideoWriter_fourcc(*'XVID'),
                            1, (width, height))

        previous_gray = None
        frame_number = 0
        trimmed_frame_count = 0
        metadata_list = []

        if not self.roi_points or len(self.roi_points) != 4:
            self.write_log(self.log_file, "Error: Invalid ROI coordinates.")
            return


        roi_polygon = np.array(self.roi_points, dtype=np.int32)

        roi_mask = np.zeros((height, width), dtype=np.uint8)
        cv2.fillPoly(roi_mask, [roi_polygon], 255)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_roi = cv2.bitwise_and(gray, gray, mask=roi_mask)

            motion_score = 0
            if previous_gray is not None:
                prev_roi = cv2.bitwise_and(previous_gray, previous_gray, mask=roi_mask)
                diff = cv2.absdiff(gray_roi, prev_roi)
                motion_score = int(np.sum(diff))

            timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

            if motion_score > THRESHOLD:
                minutes = int(timestamp // 60)
                seconds = int(timestamp % 60)
                time_str = ""
                if minutes > 0:
                    time_str += f"{minutes} min "
                if seconds > 0 or minutes == 0:
                    time_str += f"{seconds} sec"

                label = f"Frame: {frame_number}, Time: {timestamp:.2f}s, Motion: {motion_score}"
                cv2.putText(frame, label, (30, 40), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 255, 0), 2, cv2.LINE_AA)

                cv2.polylines(frame, [roi_polygon], isClosed=True, color=(0, 255, 255), thickness=2)

                out.write(frame)

                metadata = {
                    "original_frame": frame_number,
                    "timestamp": round(timestamp, 3),
                    "motion_score": motion_score,
                    "output_frame": trimmed_frame_count,
                }

                metadata_list.append(metadata)
                trimmed_frame_count += 1

            previous_gray = gray
            frame_number += 1

        cap.release()
        out.release()

        with open(output_log, "w") as f:
            json.dump(metadata_list, f, indent=4)

        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        if trimmed_frame_count == 0:
            os.remove(output_video_path)
            self.write_log(self.log_file, "No motion detected, trimmed video deleted.")
        else:
            self.write_log(self.log_file, f"Trimmed video saved: {output_video_path}")
            self.write_log(self.log_file, f"Metadata saved: {output_log}")

        self.write_log(self.log_file, f"Processing completed in {duration:.2f} seconds")
        self.write_log(self.log_file, f"Original Frames: {total_frames}, Trimmed Frames: {trimmed_frame_count}")
        self.write_log(self.log_file, f"Video Duration: {duration_sec:.2f} seconds")
        self.write_log(self.log_file, "-" * 60)
        
        return f"{output_video_path}"
