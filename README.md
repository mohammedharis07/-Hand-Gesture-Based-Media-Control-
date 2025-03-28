# ✋ Hand Gesture-Based Media Control 🎵  

A Python-based hand gesture recognition system using **MediaPipe** and **OpenCV** to control system volume and media playback with simple hand gestures.  

## 🚀 Features  

✅ **Volume Control**  
- **Primary Hand:** Adjust volume by changing the distance between **thumb** and **index finger**.  
- **Secondary Hand Appears:** Locks the current volume.  
- **Secondary Hand Disappears:** Unlocks the volume.  

✅ **Media Playback Control**  
- **Swipe Right with Secondary Hand:** Skips to the next track.  

## 🛠 Installation  

Ensure you have **Python 3.7+** installed, then install dependencies:  

```bash
pip install opencv-python mediapipe numpy pycaw pyautogui comtypes
```

## 🎮 How It Works  

1⃣ **Adjust Volume:** Move thumb & index finger apart.  
2⃣ **Lock Volume:** Show the second hand in the frame.  
3⃣ **Unlock Volume:** Remove the second hand from the frame.  
4⃣ **Skip Track:** Swipe right with the second hand.  

 

## 📌 Future Enhancements  

- Add **play/pause** and **mute/unmute** gestures.  
- Improve **gesture accuracy** using additional tracking techniques.  

## 🤝 Contribute  

Fork, improve, and submit pull requests!  

