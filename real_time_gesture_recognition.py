import cv2
import mediapipe as mp
import joblib
import numpy as np
import keyboard
import time
from tinydb import TinyDB, Query

# Load the trained SVM model
svm_model = joblib.load("gesture_svm_linear_model.pkl")

# Load gesture-action mappings from TinyDB
db = TinyDB("gestures_mappings.json")
Gesture = Query()

# Function to retrieve action mapping from TinyDB
def get_gesture_action(gesture_label):
    result = db.get(Gesture.id == gesture_label)
    return result["keys"] if result else None  # Return keyboard shortcut if found

# Initialize MediaPipe Hands for real-time keypoint extraction
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Cooldown system to prevent repeated actions
last_gesture = None
last_action_time = time.time()

# Function to execute the corresponding keyboard action
def perform_action(gesture_label):
    global last_gesture, last_action_time

    action = get_gesture_action(gesture_label)  # Fetch action from TinyDB
    if action:
        current_time = time.time()
        if gesture_label != last_gesture or (current_time - last_action_time) > 2:  # 1-second cooldown
            keyboard.press_and_release(action)
            print(f"🎯 Executed: {action}")
            last_gesture = gesture_label
            last_action_time = current_time
    else:
        print(f"⚠️ No action assigned for {gesture_label}.")
# Start capturing video from the webcam
cap = cv2.VideoCapture(0)

print("📸 Starting webcam... Press 'q' to quit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to capture image from webcam.")
        break

    # Convert the frame to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    # Check if hand landmarks are detected
    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        keypoints = [coord for landmark in hand_landmarks.landmark for coord in (landmark.x, landmark.y)]

        # Predict the gesture using the SVM model
        if len(keypoints) == 42:
            keypoints = np.array(keypoints).reshape(1, -1)
            prediction = svm_model.predict(keypoints)
            gesture_name = prediction[0]

            # Display the recognized gesture
            cv2.putText(frame, f"Gesture: {gesture_name}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                        1, (0, 255, 0), 2, cv2.LINE_AA)

            # Perform the assigned keyboard shortcut
            perform_action(gesture_name)

        # Draw hand landmarks for visualization
        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Display the webcam feed
    cv2.imshow("Gesture Recognition", frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
hands.close()
cv2.destroyAllWindows()
print("🛑 Webcam closed.")  