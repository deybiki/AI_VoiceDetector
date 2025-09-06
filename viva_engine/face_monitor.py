

# # face_monitor.py
# import os, cv2, base64
# import streamlit as st
# from collections import deque

# # Haar cascade
# BASE = os.path.dirname(__file__)
# CASCADE = os.path.join(BASE, "haarcascade_frontalface_default.xml")
# face_cascade = cv2.CascadeClassifier(CASCADE) if os.path.exists(CASCADE) else None

# def _b64(frame):
#     ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 40])
#     return base64.b64encode(buf).decode() if ok else ""

# # def ensure_camera_started(camera_index: int = 0) -> bool:
# #     """Open & cache camera immediately; fast on Windows with CAP_DSHOW."""
# #     cap = st.session_state.get("video_capture")
# #     if cap is not None and getattr(cap, "isOpened", lambda: False)():
# #         return True

# #     # Try requested index first, then a couple more
# #     for idx in (camera_index, camera_index + 1, camera_index + 2):
# #         try:
# #             # CAP_DSHOW avoids long delays on Windows
# #             cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
# #             if cap.isOpened():
# #                 cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
# #                 cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
# #                 st.session_state.video_capture = cap
# #                 st.session_state.camera_index = idx
# #                 return True
# #             cap.release()
# #         except Exception:
# #             pass

# #     st.session_state.video_capture = None
# #     return False


# def ensure_camera_started() -> bool:
#     """Auto-detect and open the first available camera."""
#     cap = st.session_state.get("video_capture")
#     if cap is not None and getattr(cap, "isOpened", lambda: False)():
#         return True

#     # Try indices 0..4 automatically
#     for idx in range(5):
#         try:
#             cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)  # CAP_DSHOW = faster on Windows
#             if cap.isOpened():
#                 ret, _ = cap.read()
#                 if ret:
#                     cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
#                     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
#                     st.session_state.video_capture = cap
#                     st.session_state.camera_index = idx
#                     print(f"✅ Camera started at index {idx}")
#                     return True
#             cap.release()
#         except Exception:
#             pass

#     st.error("❌ No working camera found. Please check permissions or hardware.")
#     st.session_state.video_capture = None
#     return False




# def render_face_monitor():
#     """Draw a small live preview + centered-face alert. No forced reruns here."""
#     if "face_history" not in st.session_state:
#         st.session_state.face_history = deque(maxlen=15)

#     cap = st.session_state.get("video_capture")
#     if not cap or not cap.isOpened():
#         # Soft UI if camera not ready yet
#         st.markdown(
#             """
#             <div style="position: fixed; bottom: 20px; right: 20px; width: 300px; height: 300px;
#                         border: 2px solid #DC3545; border-radius: 10px; background-color: #0E1117;
#                         z-index: 999; display: flex; justify-content: center; align-items: center;
#                         font-family: sans-serif; color: #DC3545; text-align: center;">
#                 <p>⚠️ Camera not accessible.<br>Check permissions.</p>
#             </div>
#             """,
#             unsafe_allow_html=True,
#         )
#         return

#     ok, frame = cap.read()
#     if not ok:
#         return

#     frame = cv2.flip(frame, 1)

#     # Detect
#     alert_msg, alert_color = "Looking Good!", "#198754"
#     if face_cascade is not None:
#         small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
#         gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
#         faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(40, 40))
#         st.session_state.face_history.append(len(faces) > 0)
#         if len(faces) > 0:
#             x_s, y_s, w_s, h_s = faces[0]
#             x, y, w, h = [v * 2 for v in (x_s, y_s, w_s, h_s)]
#             img_w = small.shape[1]
#             centered = abs((x_s + w_s / 2) - (img_w / 2)) < (img_w * 0.3)
#             color = (0, 255, 0) if centered else (0, 165, 255)
#             cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
#             if not centered:
#                 alert_msg, alert_color = "Please Center Face", "#FFC107"
#         elif sum(st.session_state.face_history) < 5:
#             alert_msg, alert_color = "No Face Detected!", "#DC3545"

#     img64 = _b64(frame)
#     st.markdown(
#         f"""
#         <style>
#           .face-monitor {{
#             position: fixed; bottom: 20px; right: 20px; width: 300px; height: 300px;
#             border: 2px solid #6c757d; border-radius: 10px; overflow: hidden;
#             background-color: #0E1117; z-index: 999; padding: 8px;
#             box-shadow: 0 4px 8px rgba(0,0,0,0.2); font-family: sans-serif;
#             font-size: 0.9rem; text-align: center; display: flex;
#             flex-direction: column; justify-content: center;
#           }}
#           .face-monitor img {{ width: 100%; height: auto; border-radius: 5px; max-height: 250px; }}
#           .alert {{ padding-top: 8px; color: {alert_color}; font-weight: bold; }}
#         </style>
#         <div class="face-monitor">
#           <img src="data:image/jpeg;base64,{img64}">
#           <p class="alert">{alert_msg}</p>
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )




























































# import os, cv2, base64, time, random
# import streamlit as st

# # Haar cascade
# BASE = os.path.dirname(__file__)
# CASCADE = os.path.join(BASE, "haarcascade_frontalface_default.xml")
# face_cascade = cv2.CascadeClassifier(CASCADE) if os.path.exists(CASCADE) else None

# def _b64(frame):
#     ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 40])
#     return base64.b64encode(buf).decode() if ok else ""

# def ensure_camera_started() -> bool:
#     """Auto-detect and open the first available camera."""
#     cap = st.session_state.get("video_capture")
#     if cap is not None and getattr(cap, "isOpened", lambda: False)():
#         return True

#     for idx in range(3):
#         try:
#             cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
#             if cap.isOpened():
#                 ret, _ = cap.read()
#                 if ret:
#                     cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
#                     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
#                     st.session_state.video_capture = cap
#                     st.session_state.camera_index = idx
#                     print(f"✅ Camera started at index {idx}")
#                     return True
#             cap.release()
#         except Exception:
#             pass

#     st.error("❌ No working camera found. Please check permissions or hardware.")
#     st.session_state.video_capture = None
#     return False


# def render_face_monitor(throttle_secs: int = 10, save_dir: str = None, randomized: bool = True):
#     """
#     Snapshot-based face monitor with optional randomization.
#     Shows floating camera preview at bottom-right.
#     """
#     now = time.time()
#     cap = st.session_state.get("video_capture")
#     if not cap or not cap.isOpened():
#         st.warning("⚠️ Camera not accessible")
#         return

#     # Grab a frame every render (for preview)
#     ok, frame = cap.read()
#     if not ok:
#         return
#     frame = cv2.flip(frame, 1)

#     # Decide interval (fixed or random)
#     if "face_interval" not in st.session_state:
#         st.session_state.face_interval = throttle_secs
#     if "last_face_check" not in st.session_state:
#         st.session_state.last_face_check = 0

#     interval = st.session_state.face_interval
#     last_check = st.session_state.last_face_check

#     if now - last_check >= interval:
#         st.session_state.last_face_check = now
#         # reset interval
#         if randomized:
#             st.session_state.face_interval = random.randint(8, 15)
#         else:
#             st.session_state.face_interval = throttle_secs

#         alert_msg, alert_color = "Looking Good!", "#198754"
#         if face_cascade is not None:
#             gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#             faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(80, 80))
#             if len(faces) == 0:
#                 alert_msg, alert_color = "No Face Detected!", "#DC3545"
#             elif len(faces) > 1:
#                 alert_msg, alert_color = "Multiple Faces Detected!", "#DC3545"
#             else:
#                 alert_msg, alert_color = "Face Detected", "#198754"

#         st.session_state.last_face_status = (alert_msg, alert_color, frame.copy())

#         # Save snapshot for audit
#         if save_dir:
#             os.makedirs(save_dir, exist_ok=True)
#             snap_path = os.path.join(save_dir, f"snapshot_{int(now)}.jpg")
#             cv2.imwrite(snap_path, frame)

#     # Display last snapshot + alert in floating box (bottom-right)
#     if "last_face_status" in st.session_state:
#         alert_msg, alert_color, frame = st.session_state.last_face_status
#         img64 = _b64(frame)
#         st.markdown(
#             f"""
#             <style>
#               .face-monitor {{
#                 position: fixed; bottom: 20px; right: 20px; width: 300px; height: 300px;
#                 border: 2px solid #6c757d; border-radius: 10px; overflow: hidden;
#                 background-color: #0E1117; z-index: 999; padding: 8px;
#                 box-shadow: 0 4px 8px rgba(0,0,0,0.2); font-family: sans-serif;
#                 font-size: 0.9rem; text-align: center; display: flex;
#                 flex-direction: column; justify-content: center;
#               }}
#               .face-monitor img {{ width: 100%; height: auto; border-radius: 5px; max-height: 250px; }}
#               .alert {{ padding-top: 8px; color: {alert_color}; font-weight: bold; }}
#             </style>
#             <div class="face-monitor">
#               <img src="data:image/jpeg;base64,{img64}">
#               <p class="alert">{alert_msg}</p>
#             </div>
#             """,
#             unsafe_allow_html=True,
#         )


























import os, cv2, time, random, json,base64
import streamlit as st
from datetime import datetime

# Haar cascade
BASE = os.path.dirname(__file__)
CASCADE = os.path.join(BASE, "haarcascade_frontalface_default.xml")
face_cascade = cv2.CascadeClassifier(CASCADE) if os.path.exists(CASCADE) else None


# def _b64(frame):
#     ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
#     return base64.b64encode(buf).decode() if ok else ""




def _b64(frame):
    _, buffer = cv2.imencode(".jpg", frame)
    return base64.b64encode(buffer).decode()


# def ensure_camera_started() -> bool:
#     """Auto-detect and open the first available camera."""
#     cap = st.session_state.get("video_capture")
#     if cap is not None and getattr(cap, "isOpened", lambda: False)():
#         return True

#     for idx in range(3):
#         try:
#             cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
#             if cap.isOpened():
#                 ret, _ = cap.read()
#                 if ret:
#                     cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
#                     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
#                     cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)   # ✅ reduce lag
#                     st.session_state.video_capture = cap
#                     st.session_state.camera_index = idx
#                     print(f"✅ Camera started at index {idx}")
#                     return True
#             cap.release()
#         except Exception:
#             pass

#     st.error("❌ No working camera found. Please check permissions or hardware.")
#     st.session_state.video_capture = None
#     return False



# def camera_check_ui():
#     """Pre-test camera check with live preview + face status indicator."""
#     cap = st.session_state.get("video_capture")
#     if not cap or not cap.isOpened():
#         st.error("❌ Camera not accessible. Please allow webcam access.")
#         return False

#     ok, frame = cap.read()
#     if not ok:
#         st.warning("⚠️ Unable to read from camera")
#         return False

#     frame = cv2.flip(frame, 1)
#     status_msg, status_color = "No Face Detected", "red"

#     # Run face detection
#     if face_cascade is not None:
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(80, 80))
#         if len(faces) == 1:
#             status_msg, status_color = "✅ Face detected – You are ready", "green"
#         elif len(faces) > 1:
#             status_msg, status_color = "❌ Multiple faces detected!", "red"

#         # Draw rectangle for feedback
#         for (x, y, w, h) in faces:
#             cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

#     # Convert frame for display
#     img64 = _b64(frame)
#     st.markdown(
#         f"""
#         <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;">
#             <img src="data:image/jpeg;base64,{img64}" style="border:2px solid #ddd;border-radius:8px;max-width:480px;">
#             <p style="color:{status_color};font-weight:bold;font-size:16px;">{status_msg}</p>
#         </div>
#         """,
#         unsafe_allow_html=True
#     )

#     # ✅ Extra guidance for candidates
#     st.info("💡 Make sure only your face is visible, you are in a well-light room, and avoid multiple people in the frame.")

#     # Proceed button only enabled if exactly one face
#     ready = (status_msg.startswith("✅"))
#     proceed = st.button("OK", disabled=not ready)

#     if proceed and ready:
#         return True
#     return False


def ensure_camera_started() -> bool:
    """Auto-detect and open the first available camera."""
    cap = st.session_state.get("video_capture")
    if cap is not None and getattr(cap, "isOpened", lambda: False)():
        return True

    for idx in range(3):
        try:
            cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
            if cap.isOpened():
                # Flush black frames
                for _ in range(5):
                    cap.read()
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
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



def camera_check_ui():
    cap = st.session_state.get("video_capture")
    if not cap or not cap.isOpened():
        st.error("❌ Camera not accessible. Please allow webcam access.")
        return False

    ok, frame = cap.read()
    if not ok or frame is None:
        st.warning("⚠️ Unable to read from camera")
        return False

    frame = cv2.flip(frame, 1)
    status_msg, status_color = "No Face Detected", "red"

    # ✅ Safely access cascade
    # face_cascade = st.session_state.face_cascade
    global face_cascade
    if face_cascade is None:
       st.error("❌ Face detection model not loaded")
       return False
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(80, 80))




    if len(faces) == 1:
        status_msg, status_color = "✅ Face detected – You are ready", "green"
    elif len(faces) > 1:
        status_msg, status_color = "❌ Multiple faces detected!", "red"

    # Draw rectangle(s)
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Show preview
    img64 = _b64(frame)
    st.markdown(
        f"""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;">
            <img src="data:image/jpeg;base64,{img64}" style="border:2px solid #ddd;border-radius:8px;max-width:480px;">
            <p style="color:{status_color};font-weight:bold;font-size:16px;">{status_msg}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.info("💡 Make sure only your face is visible, you are in a well-lit room, and avoid multiple people in the frame.")

    ready = (status_msg.startswith("✅"))
    proceed = st.button("OK", disabled=not ready)

    # 🔄 auto-refresh so frame updates
    if not ready:
        time.sleep(0.1)
        st.rerun()

    return proceed and ready



def render_face_monitor(throttle_secs: int = 10, save_dir: str = None, randomized: bool = True):
    """
    Silent snapshot-based face monitor (Mettl-style).
    - Stores snapshots + face_log.json inside candidate_dir.
    - Candidate only sees a 'Camera Active' badge.
    """
    now = time.time()
    cap = st.session_state.get("video_capture")
    if not cap or not cap.isOpened():
        st.warning("⚠️ Camera not accessible")
        return

    # Always grab a frame
    ok, frame = cap.read()
    if not ok:
        return
    frame = cv2.flip(frame, 1)

    # Decide interval (fixed or random)
    if "face_interval" not in st.session_state:
        st.session_state.face_interval = throttle_secs
    if "last_face_check" not in st.session_state:
        st.session_state.last_face_check = 0

    interval = st.session_state.face_interval
    last_check = st.session_state.last_face_check

    if now - last_check >= interval:
        st.session_state.last_face_check = now
        # reset interval
        if randomized:
            st.session_state.face_interval = random.randint(8, 15)
        else:
            st.session_state.face_interval = throttle_secs

        # Run detection only when needed
        status = "unknown"
        if face_cascade is not None:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(80, 80))
            if len(faces) == 0:
                status = "no_face"
            elif len(faces) > 1:
                status = "multi_face"
            else:
                status = "ok"

        # --- Save snapshot + log ---
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)

            snap_name = f"snapshot_{int(now)}.jpg"
            snap_path = os.path.join(save_dir, snap_name)
            cv2.imwrite(snap_path, frame)

            log_path = os.path.join(save_dir, "face_log.json")
            entry = {
                "timestamp": datetime.fromtimestamp(now).isoformat(),
                "status": status,
                "snapshot": snap_name
            }
            if os.path.exists(log_path):
                with open(log_path, "r") as f:
                    logs = json.load(f)
            else:
                logs = []
            logs.append(entry)
            with open(log_path, "w") as f:
                json.dump(logs, f, indent=2)

    # Candidate-side UI: only show "Camera Active"
    st.markdown(
        """
        <style>
          .camera-indicator {
            position: fixed; bottom: 20px; right: 20px;
            background-color: #dc3545; color: white;
            padding: 6px 14px; border-radius: 20px;
            font-size: 14px; font-weight: bold;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
            z-index: 999;
          }
        </style>
        <div class="camera-indicator">Camera Active</div>
        """,
        unsafe_allow_html=True,
    )
