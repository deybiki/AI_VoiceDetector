

# face_monitor.py
import os, cv2, base64
import streamlit as st
from collections import deque

# Haar cascade
BASE = os.path.dirname(__file__)
CASCADE = os.path.join(BASE, "haarcascade_frontalface_default.xml")
face_cascade = cv2.CascadeClassifier(CASCADE) if os.path.exists(CASCADE) else None

def _b64(frame):
    ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 40])
    return base64.b64encode(buf).decode() if ok else ""

# def ensure_camera_started(camera_index: int = 0) -> bool:
#     """Open & cache camera immediately; fast on Windows with CAP_DSHOW."""
#     cap = st.session_state.get("video_capture")
#     if cap is not None and getattr(cap, "isOpened", lambda: False)():
#         return True

#     # Try requested index first, then a couple more
#     for idx in (camera_index, camera_index + 1, camera_index + 2):
#         try:
#             # CAP_DSHOW avoids long delays on Windows
#             cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
#             if cap.isOpened():
#                 cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
#                 cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
#                 st.session_state.video_capture = cap
#                 st.session_state.camera_index = idx
#                 return True
#             cap.release()
#         except Exception:
#             pass

#     st.session_state.video_capture = None
#     return False


def ensure_camera_started() -> bool:
    """Auto-detect and open the first available camera."""
    cap = st.session_state.get("video_capture")
    if cap is not None and getattr(cap, "isOpened", lambda: False)():
        return True

    # Try indices 0..4 automatically
    for idx in range(5):
        try:
            cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)  # CAP_DSHOW = faster on Windows
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    st.session_state.video_capture = cap
                    st.session_state.camera_index = idx
                    print(f"✅ Camera started at index {idx}")
                    return True
            cap.release()
        except Exception:
            pass

    st.error("❌ No working camera found. Please check permissions or hardware.")
    st.session_state.video_capture = None
    return False




def render_face_monitor():
    """Draw a small live preview + centered-face alert. No forced reruns here."""
    if "face_history" not in st.session_state:
        st.session_state.face_history = deque(maxlen=15)

    cap = st.session_state.get("video_capture")
    if not cap or not cap.isOpened():
        # Soft UI if camera not ready yet
        st.markdown(
            """
            <div style="position: fixed; bottom: 20px; right: 20px; width: 300px; height: 300px;
                        border: 2px solid #DC3545; border-radius: 10px; background-color: #0E1117;
                        z-index: 999; display: flex; justify-content: center; align-items: center;
                        font-family: sans-serif; color: #DC3545; text-align: center;">
                <p>⚠️ Camera not accessible.<br>Check permissions.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    ok, frame = cap.read()
    if not ok:
        return

    frame = cv2.flip(frame, 1)

    # Detect
    alert_msg, alert_color = "Looking Good!", "#198754"
    if face_cascade is not None:
        small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(40, 40))
        st.session_state.face_history.append(len(faces) > 0)
        if len(faces) > 0:
            x_s, y_s, w_s, h_s = faces[0]
            x, y, w, h = [v * 2 for v in (x_s, y_s, w_s, h_s)]
            img_w = small.shape[1]
            centered = abs((x_s + w_s / 2) - (img_w / 2)) < (img_w * 0.3)
            color = (0, 255, 0) if centered else (0, 165, 255)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            if not centered:
                alert_msg, alert_color = "Please Center Face", "#FFC107"
        elif sum(st.session_state.face_history) < 5:
            alert_msg, alert_color = "No Face Detected!", "#DC3545"

    img64 = _b64(frame)
    st.markdown(
        f"""
        <style>
          .face-monitor {{
            position: fixed; bottom: 20px; right: 20px; width: 300px; height: 300px;
            border: 2px solid #6c757d; border-radius: 10px; overflow: hidden;
            background-color: #0E1117; z-index: 999; padding: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2); font-family: sans-serif;
            font-size: 0.9rem; text-align: center; display: flex;
            flex-direction: column; justify-content: center;
          }}
          .face-monitor img {{ width: 100%; height: auto; border-radius: 5px; max-height: 250px; }}
          .alert {{ padding-top: 8px; color: {alert_color}; font-weight: bold; }}
        </style>
        <div class="face-monitor">
          <img src="data:image/jpeg;base64,{img64}">
          <p class="alert">{alert_msg}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


