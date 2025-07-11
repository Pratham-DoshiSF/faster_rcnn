import cv2
import numpy as np
import json
import os
from datetime import datetime
from database.data_utils import fetch_cordinates

TRIM_VIDEO_PATH = "trimmedVideo/"
TRIM_VIDEO_METADATA_PATH = "trimmedVideoMetadata/"
THRESHOLD = 20000000
LOG_PATH = "logs/"

for folder in [TRIM_VIDEO_PATH, TRIM_VIDEO_METADATA_PATH, LOG_PATH]:
    os.makedirs(folder, exist_ok=True)

def write_log(log_file, message):
    with open(log_file, "a") as f:
        f.write(f"{datetime.now()} - {message}\n")


def process_video(customer_id, location_id, path):
    start_time = datetime.now()
    video_name = os.path.splitext(os.path.basename(path))[0]
    log_file = os.path.join(LOG_PATH, f"{video_name}.log")
    roi_points = fetch_cordinates(customer_id, location_id)
    write_log(log_file, f"Processing started for video: {path}")

    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        write_log(log_file, "Error: Could not open video.")
        return

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_sec = total_frames / fps

    output_video_path = f'{TRIM_VIDEO_PATH}{video_name}.avi'
    output_log = f"{TRIM_VIDEO_METADATA_PATH}{video_name}.json"

    out = cv2.VideoWriter(output_video_path, 
                          cv2.VideoWriter_fourcc(*'XVID'),
                          1, (width, height))

    previous_gray = None
    frame_number = 0
    trimmed_frame_count = 0
    metadata_list = []

    if not roi_points or len(roi_points) != 4:
        write_log(log_file, "Error: Invalid ROI coordinates.")
        return


    roi_polygon = np.array(roi_points, dtype=np.int32)

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
    duration = (end_time - start_time).total_seconds()

    if trimmed_frame_count == 0:
        os.remove(output_video_path)
        write_log(log_file, "No motion detected, trimmed video deleted.")
    else:
        write_log(log_file, f"Trimmed video saved: {output_video_path}")
        write_log(log_file, f"Metadata saved: {output_log}")

    write_log(log_file, f"Processing completed in {duration:.2f} seconds")
    write_log(log_file, f"Original Frames: {total_frames}, Trimmed Frames: {trimmed_frame_count}")
    write_log(log_file, f"Video Duration: {duration_sec:.2f} seconds")
    write_log(log_file, "-" * 60)
    
    return f"{output_video_path}"



# process_video("2" , "1" , "temm_video/video_20250607_083114.mp4")

