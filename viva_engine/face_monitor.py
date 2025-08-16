

#face_monitor.py

import streamlit as st
import cv2
import os
import base64
from collections import deque

# --- Load the Haar Cascade classifier ---
try:
    base_path = os.path.dirname(__file__)
    cascade_path = os.path.join(base_path, 'haarcascade_frontalface_default.xml')
    face_cascade = cv2.CascadeClassifier(cascade_path)
    if face_cascade.empty():
        st.error("FATAL: haarcascade_frontalface_default.xml not found.")
        face_cascade = None
except Exception as e:
    st.error(f"Error loading cascade file: {e}")
    face_cascade = None

def get_image_as_base64(frame):
    """Converts an OpenCV frame to a base64 encoded string for embedding in HTML."""
    is_success, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 40])
    if not is_success: return ""
    return base64.b64encode(buffer).decode()

def is_face_centered(x, w, image_width):
    """Checks if the detected face is reasonably centered."""
    face_center_x = x + w / 2
    image_center_x = image_width / 2
    return abs(face_center_x - image_center_x) < (image_width * 0.3)

def render_face_monitor():
    """Renders a self-contained face monitor component in the bottom-right corner."""
    if 'video_capture' not in st.session_state:
        camera_index = st.session_state.get('camera_index', 0)
        st.session_state.video_capture = cv2.VideoCapture(camera_index)
    if 'face_history' not in st.session_state:
        st.session_state.face_history = deque(maxlen=15)

    cap = st.session_state.video_capture
    if not cap.isOpened():
        st.markdown(
            """
            <div style="position: fixed; bottom: 20px; right: 20px; width: 300px; height: 300px;
                        border: 2px solid #DC3545; border-radius: 10px; background-color: #0E1117;
                        z-index: 999; display: flex; justify-content: center; align-items: center;
                        font-family: sans-serif; color: #DC3545; text-align: center;">
                <p>⚠️<br>Camera not accessible.<br>Check permissions.</p>
            </div>
            """, unsafe_allow_html=True)
        return

    ret, frame = cap.read()
    if not ret: return

    frame = cv2.flip(frame, 1)
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    gray_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)

    faces = []
    if face_cascade is not None:
        faces = face_cascade.detectMultiScale(
            gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
        )

    face_detected = len(faces) > 0
    st.session_state.face_history.append(face_detected)
    recent_face_detections = sum(st.session_state.face_history)

    alert_message, alert_color = "Looking Good!", "#198754"

    if face_detected:
        (x_small, y_small, w_small, h_small) = faces[0]
        x, y, w, h = [v * 2 for v in (x_small, y_small, w_small, h_small)]
        if is_face_centered(x_small, w_small, small_frame.shape[1]):
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        else:
            alert_message, alert_color = "Please Center Face", "#FFC107"
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 165, 255), 2)
    elif recent_face_detections < 5:
        alert_message, alert_color = "No Face Detected!", "#DC3545"

    base64_image = get_image_as_base64(frame)
    html_content = f"""
        <style>
        .face-monitor-container {{
            position: fixed; bottom: 20px; right: 20px; width: 300px; height: 300px;
            border: 2px solid #6c757d; border-radius: 10px; overflow: hidden;
            background-color: #0E1117; z-index: 999; padding: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2); font-family: sans-serif;
            font-size: 0.9rem; text-align: center; display: flex;
            flex-direction: column; justify-content: center;
        }}
        .face-monitor-container img {{
            width: 100%; height: auto; border-radius: 5px; max-height: 250px;
        }}
        .alert-text {{ padding-top: 8px; color: {alert_color}; font-weight: bold; }}
        </style>
        <div class="face-monitor-container">
            <img src="data:image/jpeg;base64,{base64_image}">
            <p class="alert-text">{alert_message}</p>
        </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)








































