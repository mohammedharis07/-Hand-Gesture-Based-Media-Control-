import cv2
import mediapipe as mp
import numpy as np
import math
import os
import time
import pyautogui  # Added for media control
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Initialize MediaPipe Hand module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Initialize webcam
cap = cv2.VideoCapture(0)

# Initialize Pycaw for volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Variables for control
locked_volume = None
lock_active = False
circle_buffer = []
circle_threshold = 30
unlock_timer = None
unlock_threshold = 1
primary_hand_id = None

# Swipe detection
swipe_threshold = 100  # Minimum horizontal movement for a swipe
swipe_start = None  # Stores initial position for swiping

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Flip and convert to RGB
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    
    hand_data = []
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            lm_list = []
            for id, lm in enumerate(hand_landmarks.landmark):
                h, w, c = frame.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append((cx, cy))
            hand_data.append(lm_list)
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    
    if len(hand_data) >= 1:
        hand_data.sort(key=lambda h: h[0][0])
        if primary_hand_id is None or abs(primary_hand_id[0][0] - hand_data[0][0][0]) < 50:
            primary_hand_id = hand_data[0]
        primary_hand = primary_hand_id
        secondary_hand = hand_data[1] if len(hand_data) > 1 else None
    else:
        primary_hand = secondary_hand = None
    
    if primary_hand and len(primary_hand) >= 9:
        x1, y1 = primary_hand[4]
        x2, y2 = primary_hand[8]
        cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)
        length = math.hypot(x2 - x1, y2 - y1)
        
        if not lock_active:
            min_vol, max_vol = volume.GetVolumeRange()[:2]
            vol = np.interp(length, [30, 200], [min_vol, max_vol])
            volume.SetMasterVolumeLevel(vol, None)
            cv2.putText(frame, f'Volume: {int(np.interp(length, [30, 200], [0, 100]))}%', 
                        (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        else:
            volume.SetMasterVolumeLevel(locked_volume, None)
    
    if secondary_hand:
        index_tip = secondary_hand[8]
        circle_buffer.append(index_tip)
        if len(circle_buffer) > circle_threshold:
            circle_buffer.pop(0)
        
        if len(circle_buffer) == circle_threshold:
            dx = np.diff([p[0] for p in circle_buffer])
            dy = np.diff([p[1] for p in circle_buffer])
            distances = np.sqrt(dx**2 + dy**2)
            total_movement = np.sum(distances)
            
            avg_x = np.mean([p[0] for p in circle_buffer])
            avg_y = np.mean([p[1] for p in circle_buffer])
            radius_variation = np.mean([math.hypot(p[0] - avg_x, p[1] - avg_y) for p in circle_buffer])
            
            if total_movement > 500 and radius_variation < 15:
                locked_volume = volume.GetMasterVolumeLevel()
                lock_active = True
                circle_buffer.clear()
                cv2.putText(frame, 'Volume Locked', (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        elif not lock_active:
            cv2.putText(frame, 'Draw Circle to Lock Volume', (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        
        open_palm = all(finger[1] < secondary_hand[0][1] for finger in secondary_hand[1:])
        if open_palm:
            if unlock_timer is None:
                unlock_timer = time.time()
            elif time.time() - unlock_timer > unlock_threshold:
                lock_active = False
                locked_volume = None
                unlock_timer = None
                cv2.putText(frame, 'Volume Unlocked', (50, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        else:
            unlock_timer = None
        
        # Swipe detection for media control
        if swipe_start is None:
            swipe_start = index_tip[0]
        else:
            swipe_distance = index_tip[0] - swipe_start
            if swipe_distance > swipe_threshold:
                pyautogui.press('nexttrack')
                swipe_start = None  # Reset after swipe
                cv2.putText(frame, 'Media Skipped', (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    else:
        swipe_start = None  
    
    cv2.imshow("Hand Gesture Volume Control", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
