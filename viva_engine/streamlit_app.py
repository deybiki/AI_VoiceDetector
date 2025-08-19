

import streamlit as st
import time, json, os, subprocess, asyncio, tempfile, threading, datetime
import edge_tts, speech_recognition as sr, sounddevice as sd
from scipy.io.wavfile import write
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId
from textwrap import dedent 
import streamlit.components.v1 as components
# from streamlit_autorefresh import st_autorefresh

# --- COMPONENT IMPORTS ---
from face_monitor import render_face_monitor, ensure_camera_started
from llm_scoring import score_all_responses, generate_analysis_responses

st.set_page_config(page_title="AI Viva System", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""<style>[data-testid="stSidebar"], [data-testid="collapsedControl"]{display:none!important}</style>""", unsafe_allow_html=True)


st.markdown("""
<style>
@keyframes pulse { 
  0% { transform: scale(1); } 
  50% { transform: scale(1.06); } 
  100% { transform: scale(1); } 
}
</style>
""", unsafe_allow_html=True)


# ---------- helpers (unchanged in spirit) ----------
def speak(text):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:  # synthesize
            fname = tmp.name
        asyncio.run(edge_tts.Communicate(text, "en-IN-PrabhatNeural").save(fname))
        subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", fname],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    finally:
        try: os.remove(fname)
        except Exception: pass

def play_beep():
    p = os.path.abspath("beep-05.wav")
    if os.path.exists(p):
        subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", p],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def threaded_record_audio(filename, duration, fs=44100):
    try:
        audio = sd.rec(int(duration*fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        write(filename, fs, audio)
    finally:
        st.session_state['recording_complete'] = True

def transcribe_audio(filename):
    if not filename or not os.path.exists(filename): return "No audio file."
    r = sr.Recognizer()
    with sr.AudioFile(filename) as src:
        audio = r.record(src)
    try:
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        return "Could not understand audio."
    except sr.RequestError as e:
        return f"API error: {e}"

# ---------- state ----------
if 'current_q' not in st.session_state: st.session_state.current_q = 0
if 'responses' not in st.session_state: st.session_state.responses = []
if 'timer_start_time' not in st.session_state: st.session_state.timer_start_time = 0.0
if 'candidate_id' not in st.session_state: st.session_state.candidate_id = ""
for k in ['interview_started','id_confirmed','terminate_clicked','is_recording','recording_complete']:
    st.session_state.setdefault(k, False)

# ---------- load questions (your existing DB code remains) ----------
load_dotenv("../backend/.env")
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.get_database("test")
tests_collection = db.get_collection("tests")
query_params = st.query_params
test_id = str(query_params.get("testId", "")).strip()
student_id = str(query_params.get("studentId", "")).strip()
if not test_id or not student_id: st.error("❌ Missing IDs"); st.stop()
test_data = tests_collection.find_one({"sharedLinkId": test_id})
if not test_data: st.error("❌ Invalid Test ID"); st.stop()
qids = test_data.get("questions", [])
questions = [q.get("questionText","Error") for q in db.get_collection("questions")
             .find({"_id": {"$in": [ObjectId(x) for x in qids]}})]
if not questions: st.error("❌ No questions resolved"); st.stop()

# ---------- reset state on new/returning candidate ----------
if st.session_state.get("candidate_id") != student_id:
    st.session_state.candidate_id = student_id
    st.session_state.responses = []
    st.session_state.current_q = 0
    st.session_state.terminate_clicked = False
    st.session_state.interview_started = False
    st.session_state.id_confirmed = False
    st.session_state.is_recording = False
    st.session_state.recording_complete = False

def show_countdown(message, secs=3):
    ph = st.empty()
    for remaining in range(secs, 0, -1):
        render_face_monitor()
        ph.markdown(
            f"""
            <div style="
                display: flex;
                justify-content: center;
                align-items: center;
                width: 100%;
                margin-top: 20px;
                margin-bottom: 20px;
            ">
                <div style="
                    padding: 20px 40px;
                    border-radius: 12px;
                    background: #f9f9f9;
                    border: 1px solid #e5e7eb;
                    color: #111;
                    font-size: 20px;
                    font-weight: 600;
                    text-align: center;
                    box-shadow: 0 4px 10px rgba(0,0,0,.08);
                    min-width: 200px;
                ">
                    {message}<br/>
                    <span style="color:#2563eb; font-size:34px;">{remaining}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        time.sleep(1)
    ph.empty()

# Create box placeholder once
if "timer_container" not in st.session_state:
    st.session_state.timer_container = st.empty()

def render_timer_box(remaining: int):
    st.session_state.timer_container.markdown(
        f"""
        <div style="
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
            margin: 20px 0;
        ">
            <div style="
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                padding: 24px 40px;
                border-radius: 12px;
                background: #ffffff;
                border: 1px solid #e5e7eb;
                box-shadow: 0 4px 10px rgba(0,0,0,0.08);
                text-align: center;
                min-width: 220px;
            ">
                <div style="color:#2563eb; font-size:42px; font-weight:800; line-height:1;">
                    {remaining}s
                </div>
                <div style="color:#111827; font-size:18px; font-weight:600; margin-top:10px;">
                    Speak loudly & clearly
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )







RECORDING_DURATION = 15
st.title("AI-powered Viva-Voce System")

# ---------- confirm ID ----------
if not st.session_state.id_confirmed:
    try:
        r = requests.get(f"http://localhost:5000/api/student/student/{student_id}", timeout=3)
        if r.status_code == 200 and r.json().get("photo"):
            st.image(r.json()["photo"], caption="Candidate Photo", width=180)
    except Exception:
        pass

    cand_in = st.text_input("Enter your Candidate ID to begin:", value=student_id)
    if st.button("Confirm ID"):
        if cand_in == student_id:
            st.session_state.id_confirmed = True
            st.rerun()
        else:
            st.error("❌ Entered ID does not match.")
    st.stop()

# ---------- start interview: welcome is BLOCKING, then start camera ----------

if not st.session_state.interview_started:
    st.success(f"ID '{st.session_state.candidate_id}' registered. You may start the Viva")
    
    if st.button("Start Test"):
        with st.spinner("Playing welcome message..."):
            speak("Welcome to this Examination. Please listen carefully and answer within the time limit.")
        
        # auto-select and start camera
        ensure_camera_started()  
        
        st.session_state.interview_started = True
        st.rerun()
    st.stop()




# ---------- rules popup (before showing Start button) ----------


# # Initialize session state
# if "interview_started" not in st.session_state:
#     st.session_state.interview_started = False
# if "rules_done" not in st.session_state:
#     st.session_state.rules_done = False

# if not st.session_state.interview_started:

#     if not st.session_state.rules_done:
#         # ✅ Show modal popup
#         components.html(
#             """
#             <style>
#             body { margin: 0; }
#             .overlay {
#               position: fixed;
#               top: 0; left: 0;
#               width: 100%; height: 100%;
#               background: rgba(0,0,0,0.6);
#               display: flex; justify-content: center; align-items: center;
#               z-index: 9999;
#             }
#             .rules-modal {
#               background: #fff;
#               padding: 30px;
#               border-radius: 12px;
#               max-width: 600px;
#               width: 90%;
#               box-shadow: 0 8px 20px rgba(0,0,0,0.3);
#               font-size: 16px; line-height: 1.6;
#             }
#             .rules-modal h3 {
#               text-align: center;
#               margin-bottom: 15px;
#               color: #d72638;
#             }
#             .rules-modal button {
#               background-color: #d72638;
#               color: white;
#               font-weight: bold;
#               border: none;
#               border-radius: 8px;
#               padding: 10px;
#               width: 100%;
#               cursor: pointer;
#               margin-top: 15px;
#             }
#             .rules-modal button:disabled {
#               background: #aaa;
#               cursor: not-allowed;
#             }
#             </style>

#             <div class="overlay" id="rulesOverlay">
#               <div class="rules-modal">
#                 <h3>📋 Exam Rules & Regulations</h3>
#                 <ul>
#                   <li>Camera must remain <b>ON</b> during viva.</li>
#                   <li>Face must remain <b>clearly visible</b>.</li>
#                   <li>No background noise or external help.</li>
#                   <li>Answer clearly within the <b>time limit</b>.</li>
#                   <li>Once you proceed, viva will begin.</li>
#                 </ul>
#                 <label>
#                   <input type="checkbox" id="agreeCheck"> I agree with the rules
#                 </label>
#                 <button id="proceedBtn" disabled>Proceed</button>
#               </div>
#             </div>

#             <script>
#             const check = document.getElementById("agreeCheck");
#             const btn = document.getElementById("proceedBtn");

#             check.addEventListener("change", () => {
#               btn.disabled = !check.checked;
#             });

#             btn.addEventListener("click", () => {
#               // Trigger Streamlit hidden button
#               window.parent.postMessage({ isRulesAccepted: true, type: "rules-event" }, "*");
#             });
#             </script>
#             """,
#             height=500,
#         )

#         # Hidden button → catches JS postMessage
#         if st.query_params.get("rulesAccepted") == "true":
#            st.session_state.rules_done = True
#            try:
#              st.query_params.clear()
#            except Exception:
#              pass
#            st.rerun()

#     # ✅ After rules accepted
#     st.success("✅ Rules accepted. You may now begin the viva.")

#     if st.button("Start Test", key="start_btn", type="primary"):
#         with st.spinner("Playing welcome message..."):
#             speak("Welcome to this Examination. Please listen carefully and answer within the time limit.")
#         ensure_camera_started()
#         st.session_state.interview_started = True
#         st.rerun()






# ---------- interview running ----------
candidate_dir = os.path.join("interviews", st.session_state.candidate_id)
os.makedirs(candidate_dir, exist_ok=True)

q_idx = st.session_state.current_q
if q_idx < len(questions) and not st.session_state.terminate_clicked:
    question = questions[q_idx]
    st.subheader(f"Question {q_idx + 1}: {question}")

    # Timer box placeholder always below the question
    st.session_state.timer_container = st.empty()


    # show monitor every render (no forced rerun here)
    render_face_monitor()

    if not st.session_state.is_recording:
        q_key = f"auto_started_q{q_idx}"
        if not st.session_state.get(q_key, False):
            st.session_state[q_key] = True
        show_countdown("Question will play start in", secs=3)
        play_beep()
        speak(question)   # blocking
        play_beep()

        time.sleep(2) 
        
        # show_countdown(" Get ready to answer in", secs=3)

        st.session_state.is_recording = True
        st.session_state.recording_complete = False
        st.session_state.timer_start_time = time.time()

        audio_fname = os.path.join(candidate_dir, f"q{q_idx + 1}_answer.wav")
        threading.Thread(
           target=threaded_record_audio,
           args=(audio_fname, RECORDING_DURATION),
           daemon=True
        ).start()
        st.rerun()




    # 2) While recording: update timer smoothly, finish when done
    if st.session_state.is_recording:
        elapsed = time.time() - st.session_state.timer_start_time
        remaining = max(0, int(RECORDING_DURATION - elapsed))
        
        render_timer_box(remaining)

        if remaining <= 0 or st.session_state.get("recording_complete", False):
            play_beep()  # end signal
            time.sleep(0.2)  # small gap for file flush

            st.session_state.timer_container.markdown("### ⏰ **Oops! Time's up!**")
            time.sleep(1)

            audio_fname = os.path.join(candidate_dir, f"q{q_idx + 1}_answer.wav")
            transcript = transcribe_audio(audio_fname).strip()
            st.session_state.responses.append({
                "question_number": q_idx + 1,
                "question": question,
                "audio_file": audio_fname,
                "transcript": transcript
            })

            st.session_state.is_recording = False
            st.session_state.recording_complete = False
            st.session_state.current_q += 1
            st.rerun()
        else:
            # gentle refresh ONLY while recording
            time.sleep(0.5)
            st.rerun()

# ---------- termination controls ----------
if not st.session_state.terminate_clicked:
    if st.session_state.current_q >= len(questions):
        st.warning("🎉 You've answered all questions. Click below to view your summary.")
        if st.button("🟢 View My Responses", key="terminate_btn_final"):
            st.session_state.terminate_clicked = True
            st.rerun()

    elif st.session_state.responses:
        if st.button("🔴 Quit Interview", key="terminate_btn"):
            st.session_state.terminate_clicked = True
            st.rerun()


# ---------- summary page ----------
if st.session_state.terminate_clicked:
    # stop camera
    cap = st.session_state.get("video_capture")
    if cap is not None:
        try: cap.release()
        except Exception: pass
        st.session_state.video_capture = None

    st.success("✅ Interview Summary")
    for res in st.session_state.responses:
        st.markdown(f"**Q{res['question_number']}:** {res['question']}")
        st.audio(res['audio_file'])
        st.markdown(f"**A:** {res['transcript']}")

    if st.button("Submit and Show Results"):
        # persist latest responses (overwrite every time)
        with open(os.path.join(candidate_dir, "responses.json"), "w") as f:
            json.dump(st.session_state.responses, f, indent=4)

        with st.spinner("Analyzing your responses..."):
            score_all_responses(st.session_state.candidate_id)
            generate_analysis_responses(st.session_state.candidate_id)

        st.switch_page("pages/thank_you.py")

# ---------- keep camera alive between questions WITHOUT hammering reruns ----------
if st.session_state.interview_started and not st.session_state.terminate_clicked and not st.session_state.is_recording:
    render_face_monitor()
    # mild refresh so preview updates (~2 fps) but UI stays responsive
    time.sleep(0.5)
    st.rerun()























