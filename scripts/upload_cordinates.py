import cv2
import numpy as np
import json
from database.data_utils import insert_cordinates , update_cordinates

CUSTOMER_ID = "test_client_1"
LOCATION_ID = "test_cam_1"
roi_points = []
frame_copy = None
cap = cv2.VideoCapture("temm_video/video_20250607_083114.mp4")

def sort_points(pts):
    pts = np.array(pts, dtype="float32")

    sorted_by_y = pts[np.argsort(pts[:, 1])]

    top_two = sorted_by_y[:2]
    bottom_two = sorted_by_y[2:]

    top_left, top_right = top_two[np.argsort(top_two[:, 0])]

    bottom_left, bottom_right = bottom_two[np.argsort(bottom_two[:, 0])]

    return [
        tuple(map(int, top_left)),
        tuple(map(int, top_right)),
        tuple(map(int, bottom_right)),
        tuple(map(int, bottom_left)),
    ]

def draw_quadrilateral(event, x, y, flags, param):
    global roi_points, frame, frame_copy

    if event == cv2.EVENT_LBUTTONDOWN:
        if len(roi_points) < 4:
            roi_points.append((x, y))
            print(f"Point {len(roi_points)}: ({x}, {y})")
            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
            cv2.imshow("Video Frame", frame)

        if len(roi_points) == 4:
            sorted_pts = sort_points(roi_points)

            pts_array = np.array(sorted_pts, np.int32).reshape((-1, 1, 2))
            cv2.polylines(frame, [pts_array], isClosed=True, color=(255, 0, 0), thickness=2)
            cv2.imshow("Video Frame", frame)

            print("\nQuadrilateral ROI selected:")
            labels = ['Top-left', 'Top-right', 'Bottom-right', 'Bottom-left']
            for label, pt in zip(labels, sorted_pts):
                print(f"{label}: {tuple(pt)}")

            roi_points[:] = sorted_pts  

def main():
    global frame, frame_copy, roi_points

    paused = False

    while True:
        if not paused:
            ret, frame = cap.read()
            if not ret:
                break
            frame_copy = frame.copy()
            cv2.imshow("Video Frame", frame)

        key = cv2.waitKey(30) & 0xFF

        if key == ord("p"):
            paused = not paused
            if paused:
                roi_points = []
                frame = frame_copy.copy()
                print("\n Video paused. Click 4 points to draw a quadrilateral ROI.")
                cv2.imshow("Video Frame", frame)
                cv2.setMouseCallback("Video Frame", draw_quadrilateral)

        elif key == ord("r"):
            roi_points = []
            frame = frame_copy.copy()
            print("\nROI reset. Click 4 points again.")
            cv2.imshow("Video Frame", frame)

        elif key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    if len(roi_points) == 4:
        print("\nFinal ROI points:", roi_points)
        return roi_points
    else:
        print("\nROI not fully selected (need 4 points). Nothing saved.")
        return None

# print(roi_points)
# print(type(roi_points))
# print("-------")
# print(roi_points[-1])

roi_points = main()
if roi_points:
    user_input = input("Enter i for insert and u for update : ")
    if user_input == "i":
        insert_cordinates(CUSTOMER_ID , LOCATION_ID , roi_points)
    elif user_input == "u":
        update_cordinates(CUSTOMER_ID , LOCATION_ID , roi_points)
    else :
        print("Invalid input")