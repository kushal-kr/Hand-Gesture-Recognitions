"""
Virtual Mouse - Full Screen + Left, Double, Right Click + Scroll
---------------------------------------------------------------
Controls:
- Move cursor: Index finger
- Left Click: Pinch (index + thumb once)
- Double Click: Pinch (index + thumb twice quickly)
- Right Click: Pinch (middle + thumb)
- Scroll: Move index finger up/down
"""

import cv2
import time
import math
import mediapipe as mp
import pyautogui
import numpy as np
from collections import deque

# Screen size
SCREEN_W, SCREEN_H = pyautogui.size()

# Camera size
CAM_W, CAM_H = 640, 480

# Parameters
SMOOTHING_WINDOW = 5
CLICK_DIST = 40
DEAD_ZONE = 5


class VirtualMouse:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, CAM_W)
        self.cap.set(4, CAM_H)

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1,
                                         min_detection_confidence=0.7,
                                         min_tracking_confidence=0.7)
        self.drawer = mp.solutions.drawing_utils

        self.x_buffer = deque(maxlen=SMOOTHING_WINDOW)
        self.y_buffer = deque(maxlen=SMOOTHING_WINDOW)
        self.prev_x, self.prev_y = 0, 0

        self.last_click_time = 0  # for double-click detection

    def run(self):
        print("✅ Virtual Mouse started. Press 'q' to quit.")
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb)

            if results.multi_hand_landmarks:
                lm = results.multi_hand_landmarks[0]
                self.drawer.draw_landmarks(frame, lm, self.mp_hands.HAND_CONNECTIONS)

                h, w, _ = frame.shape
                index = lm.landmark[8]   # index fingertip
                thumb = lm.landmark[4]   # thumb fingertip
                middle = lm.landmark[12] # middle fingertip

                ix, iy = int(index.x * w), int(index.y * h)
                tx, ty = int(thumb.x * w), int(thumb.y * h)
                mx, my = int(middle.x * w), int(middle.y * h)

                # Map camera coords → screen coords
                screen_x = np.interp(ix, (0, CAM_W), (0, SCREEN_W))
                screen_y = np.interp(iy, (0, CAM_H), (0, SCREEN_H))

                # Smooth cursor
                self.x_buffer.append(screen_x)
                self.y_buffer.append(screen_y)
                smooth_x = sum(self.x_buffer) / len(self.x_buffer)
                smooth_y = sum(self.y_buffer) / len(self.y_buffer)

                if abs(smooth_x - self.prev_x) > DEAD_ZONE or abs(smooth_y - self.prev_y) > DEAD_ZONE:
                    pyautogui.moveTo(smooth_x, smooth_y, _pause=False)
                    self.prev_x, self.prev_y = smooth_x, smooth_y

                cv2.circle(frame, (ix, iy), 10, (0, 255, 0), -1)

                # Distances
                dist_index_thumb = math.hypot(ix - tx, iy - ty)
                dist_middle_thumb = math.hypot(mx - tx, my - ty)

                # Left Click & Double Click
                if dist_index_thumb < CLICK_DIST:
                    current_time = time.time()
                    if current_time - self.last_click_time < 0.4:  # double click
                        pyautogui.doubleClick()
                        cv2.putText(frame, "Double Click", (10, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                    else:  # single left click
                        pyautogui.click(button="left")
                        cv2.putText(frame, "Left Click", (10, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                    self.last_click_time = current_time
                    time.sleep(0.25)

                # Right Click
                elif dist_middle_thumb < CLICK_DIST:
                    pyautogui.click(button="right")
                    cv2.putText(frame, "Right Click", (10, 90),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                    time.sleep(0.25)

                # Scroll = move finger vertically
                dy = self.prev_y - smooth_y
                if abs(dy) > 30:  # threshold
                    pyautogui.scroll(int(dy / 5))
                    cv2.putText(frame, "Scroll", (10, 130),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

            cv2.imshow("Virtual Mouse", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    VirtualMouse().run()
