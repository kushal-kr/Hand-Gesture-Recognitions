import cv2
import mediapipe as mp
import pyautogui

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Open webcam
cap = cv2.VideoCapture(0)

# Track last action to avoid repeating too fast
last_action = None

def fingers_up(hand_landmarks):
    """
    Returns a list [thumb, index, middle, ring, pinky]
    1 if finger is up, 0 if down
    """
    finger_tips = [4, 8, 12, 16, 20]
    finger_pips = [2, 6, 10, 14, 18]
    fingers = []

    # Thumb (check x instead of y because it's sideways)
    if hand_landmarks.landmark[finger_tips[0]].x < hand_landmarks.landmark[finger_pips[0]].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other four fingers
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

    # Flip for natural display
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process with MediaPipe
    results = hands.process(rgb_frame)

    gesture = "None"

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            fingers = fingers_up(hand_landmarks)

            # ✋ Open palm → Play/Pause
            if fingers == [1,1,1,1,1]:
                gesture = "Play/Pause"
                if last_action != gesture:
                    pyautogui.press('space')
                    last_action = gesture

            # 👍 Thumb up → Volume Up
            elif fingers == [1,0,0,0,0]:
                gesture = "Volume Up"
                if last_action != gesture:
                    pyautogui.press('volumeup')
                    last_action = gesture

            # 👎 Thumb down → Volume Down
            elif fingers == [0,0,0,0,0]:
                gesture = "Volume Down"
                if last_action != gesture:
                    pyautogui.press('volumedown')
                    last_action = gesture

            # 👉 Index finger only → Next video
            elif fingers == [0,1,0,0,0]:
                gesture = "Next Video"
                if last_action != gesture:
                    pyautogui.hotkey('shift', 'n')
                    last_action = gesture

            # 👈 Index + middle finger → Previous video
            elif fingers == [0,1,1,0,0]:
                gesture = "Previous Video"
                if last_action != gesture:
                    pyautogui.hotkey('shift', 'p')
                    last_action = gesture

            else:
                last_action = None

    # Show gesture on screen
    cv2.putText(frame, f"Gesture: {gesture}", (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    cv2.imshow("YouTube Gesture Control", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
        break

cap.release()
cv2.destroyAllWindows()
