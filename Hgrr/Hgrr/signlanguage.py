import cv2
import mediapipe as mp

# Mediapipe Hands
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Gesture labels
GESTURES = {
    "Thumbs_Up": "YES",
    "Thumbs_Down": "NO",
    "Open_Palm": "HELLO",
    "Closed_Fist": "HELP",
    "Stop_Palm": "STOP",
    "ILoveYou": "GOOD"
}

def classify_landmarks(landmarks):
    """Improved gesture classification with non-overlapping rules"""
    thumb_tip = landmarks[4].y
    thumb_ip = landmarks[3].y
    index_tip = landmarks[8].y
    index_pip = landmarks[6].y
    middle_tip = landmarks[12].y
    middle_pip = landmarks[10].y
    ring_tip = landmarks[16].y
    ring_pip = landmarks[14].y
    pinky_tip = landmarks[20].y
    pinky_pip = landmarks[18].y

    # 1. Thumbs Up
    if thumb_tip < thumb_ip and index_tip > index_pip and middle_tip > middle_pip:
        return "Thumbs_Up"

    # 2. Thumbs Down
    if thumb_tip > thumb_ip and index_tip > index_pip and middle_tip > middle_pip:
        return "Thumbs_Down"

    # 3. Closed Fist
    if (index_tip > index_pip and middle_tip > middle_pip and
        ring_tip > ring_pip and pinky_tip > pinky_pip):
        return "Closed_Fist"

    # 4. Open Palm
    if (index_tip < index_pip and middle_tip < middle_pip and
        ring_tip < ring_pip and pinky_tip < pinky_pip):
        return "Open_Palm"

    # 5. Stop (Flat palm, straight fingers)
    if (index_tip < index_pip and middle_tip < middle_pip and
        ring_tip < ring_pip and pinky_tip < pinky_pip and
        thumb_tip > thumb_ip):  # thumb tucked sideways
        return "Stop_Palm"

    # 6. I Love You (🤟)
    if (index_tip < index_pip and pinky_tip < pinky_pip and
        middle_tip > middle_pip and ring_tip > ring_pip):
        return "ILoveYou"

    return None


# Webcam loop
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            gesture = classify_landmarks(hand_landmarks.landmark)
            if gesture:
                text = GESTURES[gesture]
                cv2.putText(frame, text, (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Hand Gesture Recognition", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
        break

cap.release()
cv2.destroyAllWindows()
