import os, cv2, time, random, json, base64
import streamlit as st
from datetime import datetime

# Haar cascade
BASE = os.path.dirname(__file__)
CASCADE = os.path.join(BASE, "haarcascade_frontalface_default.xml")
face_cascade = cv2.CascadeClassifier(CASCADE) if os.path.exists(CASCADE) else None


def _b64(frame):
    _, buffer = cv2.imencode(".jpg", frame)
    return base64.b64encode(buffer).decode()


def _release_camera():
    cap = st.session_state.get("video_capture")
    if cap is not None:
        try:
            cap.release()
        except Exception:
            pass
    st.session_state.video_capture = None


def _frame_looks_valid(frame):
    if frame is None:
        return False
    # "Opened but black" camera streams are common with some drivers/backends.
    return float(frame.mean()) > 8.0


def ensure_camera_started() -> bool:
    """Auto-detect and open the first available camera that returns usable frames."""
    cap = st.session_state.get("video_capture")
    if cap is not None and getattr(cap, "isOpened", lambda: False)():
        return True

    backends = []
    if hasattr(cv2, "CAP_MSMF"):
        backends.append(cv2.CAP_MSMF)
    if hasattr(cv2, "CAP_DSHOW"):
        backends.append(cv2.CAP_DSHOW)
    backends.append(None)  # default backend fallback

    for backend in backends:
        for idx in range(5):
            try:
                cap = cv2.VideoCapture(idx, backend) if backend is not None else cv2.VideoCapture(idx)
                if not cap.isOpened():
                    cap.release()
                    continue

                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

                frame = None
                for _ in range(12):
                    ok, candidate = cap.read()
                    if ok and candidate is not None:
                        frame = candidate

                if not _frame_looks_valid(frame):
                    cap.release()
                    continue

                st.session_state.video_capture = cap
                st.session_state.camera_index = idx
                st.session_state.camera_backend = backend if backend is not None else "default"
                print(f"Camera started at index {idx} using backend {st.session_state.camera_backend}")
                return True
            except Exception:
                pass

    st.error("No working camera found. Please check permissions or hardware.")
    st.session_state.video_capture = None
    return False


def camera_check_ui():
    cap = st.session_state.get("video_capture")
    if not cap or not cap.isOpened():
        st.error("Camera not accessible. Please allow webcam access.")
        return False

    ok, frame = cap.read()
    if not ok or frame is None:
        st.warning("Unable to read from camera")
        if st.button("Retry Camera", key="retry_camera_unreadable"):
            _release_camera()
            st.rerun()
        return False

    if not _frame_looks_valid(frame):
        st.warning("Camera feed looks black. Close Zoom/Teams/Meet and retry camera.")
        if st.button("Switch/Retry Camera", key="retry_camera_black"):
            _release_camera()
            st.rerun()
        return False

    frame = cv2.flip(frame, 1)
    status_msg, status_color = "No Face Detected", "red"

    global face_cascade
    if face_cascade is None:
        st.error("Face detection model not loaded")
        return False

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(80, 80))

    if len(faces) == 1:
        status_msg, status_color = "Face detected - You are ready", "green"
    elif len(faces) > 1:
        status_msg, status_color = "Multiple faces detected!", "red"

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    img64 = _b64(frame)
    st.markdown(
        f"""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;">
            <img src="data:image/jpeg;base64,{img64}" style="border:2px solid #ddd;border-radius:8px;max-width:480px;">
            <p style="color:{status_color};font-weight:bold;font-size:16px;">{status_msg}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info("Make sure only your face is visible, you are in a well-lit room, and avoid multiple people in the frame.")

    ready = status_msg.startswith("Face detected")
    proceed = st.button("OK", disabled=not ready)

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
        st.warning("Camera not accessible")
        return

    ok, frame = cap.read()
    if not ok:
        return
    frame = cv2.flip(frame, 1)

    if "face_interval" not in st.session_state:
        st.session_state.face_interval = throttle_secs
    if "last_face_check" not in st.session_state:
        st.session_state.last_face_check = 0

    interval = st.session_state.face_interval
    last_check = st.session_state.last_face_check

    if now - last_check >= interval:
        st.session_state.last_face_check = now
        if randomized:
            st.session_state.face_interval = random.randint(8, 15)
        else:
            st.session_state.face_interval = throttle_secs

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

        if save_dir:
            os.makedirs(save_dir, exist_ok=True)

            snap_name = f"snapshot_{int(now)}.jpg"
            snap_path = os.path.join(save_dir, snap_name)
            cv2.imwrite(snap_path, frame)

            log_path = os.path.join(save_dir, "face_log.json")
            entry = {
                "timestamp": datetime.fromtimestamp(now).isoformat(),
                "status": status,
                "snapshot": snap_name,
            }
            if os.path.exists(log_path):
                with open(log_path, "r") as f:
                    logs = json.load(f)
            else:
                logs = []
            logs.append(entry)
            with open(log_path, "w") as f:
                json.dump(logs, f, indent=2)

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