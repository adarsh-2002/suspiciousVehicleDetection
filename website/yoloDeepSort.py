import os
import random
import sys
import cv2
from ultralytics import YOLO
from .tracker import Tracker

def yoloDeepSort(vid):
    video_path = os.path.join('videos',vid)
    video_out_path = os.path.join( 'videos/outputs/video', 'out.mp4')

    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()

    cap_out = cv2.VideoWriter(video_out_path, cv2.VideoWriter_fourcc(*'MP4V'), cap.get(cv2.CAP_PROP_FPS),
                            (frame.shape[1], frame.shape[0]))

    model = YOLO("best.pt")

    tracker = Tracker()
    saved_tracks = []

    colors = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for j in range(10)]

    detection_threshold = 0.5
    while ret:

        results = model(frame)

        for result in results:
            detections = []
            for r in result.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = r
                x1 = int(x1)
                x2 = int(x2)
                y1 = int(y1)
                y2 = int(y2)
                class_id = int(class_id)
                if score > detection_threshold:
                    detections.append([x1, y1, x2, y2, score])
            try:
                tracker.update(frame, detections)
            except:
                continue

            for track in tracker.tracks:
                bbox = track.bbox
                x1, y1, x2, y2 = bbox
                track_id = track.track_id
                if track_id not in saved_tracks:
                    if y1<(14700-3*x1)/22:
                        try:
                            cv2.imwrite("videos/outputs/crops/{}/vehicle_{}.jpg".format(vid.split('.')[0], track_id), frame[int(y1):int(y2), int(x1):int(x2)])
                        except:
                            print("Error")
                        saved_tracks.append(track_id)
                

                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (colors[track_id % len(colors)]), 3)

        cap_out.write(frame)
        ret, frame = cap.read()

    cap.release()
    cap_out.release()
    cv2.destroyAllWindows()