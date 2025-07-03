import cv2, mediapipe as mp, numpy as np, os, pandas as pd, joblib
from tinydb import TinyDB
from sklearn.svm import SVC

db = TinyDB("gestures_mappings.json")
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
csv_file = "output/keypoints.csv"
model_file = "gesture_svm_linear_model.pkl"

def store_gesture(gesture_name, action_name, key_binding, image_path):
    db.insert({"id": gesture_name, "action": action_name, "keys": key_binding, "image": image_path})

def extract_keypoints(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    if results.multi_hand_landmarks:
        landmarks = results.multi_hand_landmarks[0]
        return [coord for lm in landmarks.landmark for coord in (lm.x, lm.y)]
    return None

def save_keypoints_to_csv(gesture_name, keypoints_list):
    df = pd.read_csv(csv_file)
    for k in keypoints_list:
        df.loc[len(df)] = k + [gesture_name]
    df.to_csv(csv_file, index=False)

def extract_frames(video_path, gesture_name, frame_interval=2):
    cap = cv2.VideoCapture(video_path)
    save_dir = f"static/gesture_dataset/{gesture_name}"
    os.makedirs(save_dir, exist_ok=True)
    frame_idx, img_count, keypoints_list = 0, 0, []
    
    while cap.isOpened() and img_count < 150:
        ret, frame = cap.read()
        if not ret: break
        if frame_idx % frame_interval == 0:
            img_path = f"{save_dir}/{gesture_name}_{img_count}.jpg"
            cv2.imwrite(img_path, frame)
            keypoints = extract_keypoints(frame)
            if keypoints:
                keypoints_list.append(keypoints)
                img_count += 1
        frame_idx += 1
    cap.release()
    save_keypoints_to_csv(gesture_name, keypoints_list)

def retrain_existing_svm():
    df = pd.read_csv(csv_file)
    if df.empty: return False
    X, y = df.iloc[:, :-1], df.iloc[:, -1]
    svm = joblib.load(model_file)
    svm.fit(X, y)
    joblib.dump(svm, model_file)
    return True
