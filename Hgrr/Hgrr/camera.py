import cv2
import mediapipe as mp
import time
import os

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Open webcam
cap = cv2.VideoCapture(0)

# Track photo count
photo_count = 0
countdown_start = None
capturing = False

def fingers_up(hand_landmarks):
    """
    Returns list [thumb, index, middle, ring, pinky]
    1 if finger is up, 0 if down
    """
    finger_tips = [4, 8, 12, 16, 20]
    finger_pips = [2, 6, 10, 14, 18]
    fingers = []

    # Thumb (check x)
    if hand_landmarks.landmark[finger_tips[0]].x < hand_landmarks.landmark[finger_pips[0]].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other fingers (check y)
    for tip, pip in zip(finger_tips[1:], finger_pips[1:]):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Mirror image
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb_frame)
    gesture = "None"

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            fingers = fingers_up(hand_landmarks)

            # 👍 Thumbs up = [1,0,0,0,0]
            if fingers == [1,0,0,0,0] and not capturing:
                gesture = "Thumbs Up"
                countdown_start = time.time()
                capturing = True

    # Handle countdown
    if capturing and countdown_start is not None:
        elapsed = time.time() - countdown_start
        remaining = 5 - int(elapsed)

        if remaining > 0:
            cv2.putText(frame, f"Capturing in: {remaining}", (150, 200),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
        else:
            photo_count += 1
            filename = f"capture_{photo_count}.jpg"
            cv2.imwrite(filename, frame)
            print(f"✅ Saved {filename}")
            capturing = False
            countdown_start = None

    cv2.putText(frame, f"Gesture: {gesture}", (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    cv2.imshow("Hand Gesture Capture with Countdown", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
        break

cap.release()
cv2.destroyAllWindows()
