import cv2
import mediapipe as mp
import pyautogui
import time
import math

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Webcam
cap = cv2.VideoCapture(0)

# Cooldown system (avoid repeated triggers)
last_action = None
last_time = 0
cooldown = 1  # seconds

def fingers_up(hand_landmarks):
    """
    Returns [thumb, index, middle, ring, pinky]
    1 if finger is up, 0 if down
    """
    finger_tips = [4, 8, 12, 16, 20]
    finger_pips = [2, 6, 10, 14, 18]
    fingers = []

    # Thumb (x-axis check)
    if hand_landmarks.landmark[finger_tips[0]].x < hand_landmarks.landmark[finger_pips[0]].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other fingers (y-axis check)
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

    frame = cv2.flip(frame, 1)  # Mirror effect
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb_frame)
    gesture = "None"

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            fingers = fingers_up(hand_landmarks)

            # ☝️ One finger (index only) → Next slide
            if fingers == [0, 1, 0, 0, 0]:
                gesture = "Next Slide"
                if last_action != gesture and time.time() - last_time > cooldown:
                    pyautogui.press("right")   # PowerPoint shortcut
                    last_action = gesture
                    last_time = time.time()

            # ✌️ Two fingers (index + middle) → Previous slide
            elif fingers == [0, 1, 1, 0, 0]:
                gesture = "Previous Slide"
                if last_action != gesture and time.time() - last_time > cooldown:
                    pyautogui.press("left")    # PowerPoint shortcut
                    last_action = gesture
                    last_time = time.time()

            # 👏 Snap gesture (thumb + middle finger close) → Exit slideshow
            thumb_tip = hand_landmarks.landmark[4]
            middle_tip = hand_landmarks.landmark[12]
            dist = math.hypot(
                (thumb_tip.x - middle_tip.x),
                (thumb_tip.y - middle_tip.y)
            )
            if dist < 0.05:  # Fingers close = snap
                gesture = "Exit Slideshow"
                if last_action != gesture and time.time() - last_time > cooldown:
                    pyautogui.press("esc")     # PowerPoint shortcut
                    last_action = gesture
                    last_time = time.time()

            else:
                if time.time() - last_time > cooldown:
                    last_action = None

    # Show detected gesture on screen
    cv2.putText(frame, f"Gesture: {gesture}", (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("PowerPoint Gesture Control", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit program itself
        break

cap.release()
cv2.destroyAllWindows()
