
import streamlit as st
import time, json, os, subprocess, asyncio, tempfile, threading
from datetime import datetime
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
from face_monitor import render_face_monitor, ensure_camera_started,camera_check_ui
from llm_scoring import score_all_responses ,score_single_response
# from full_screen import start_tab_monitor, stop_tab_monitor

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

st.session_state["test_id"] = test_id
# print("✅ Final test_id stored in session:", test_id)

student_id = str(query_params.get("studentId", "")).strip()
if not test_id or not student_id: st.error("❌ Missing IDs"); st.stop()
test_data = tests_collection.find_one({"sharedLinkId": test_id})
if not test_data: st.error("❌ Invalid Test ID"); st.stop()

test_description = test_data.get("description", "No description available")
st.session_state["test_description"] = test_description

# print(f"[DEBUG] Test description fetched: {test_description}")


# qids = test_data.get("questions", [])
# questions = [q.get("questionText","Error") for q in db.get_collection("questions")
#              .find({"_id": {"$in": [ObjectId(x) for x in qids]}})]
# if not questions: st.error("❌ No questions resolved"); st.stop()

  # debug in terminal
qids = test_data.get("questions", [])

# Fetch all answers for this test
answers_data = list(db.get_collection("testanswers").find({"testId": ObjectId(test_data["_id"])}))

questions, reference_answers = [], []

# Maintain same order as qids
for q in db.get_collection("questions").find({"_id": {"$in": [ObjectId(x) for x in qids]}}):
    questions.append(q.get("questionText", "Error"))

# Just align answers in insertion order (since no questionId is present)
reference_answers = [a.get("answerText", "") for a in answers_data]

if not questions:
    st.error("❌ No questions resolved")
    st.stop()

st.session_state.reference_answers = reference_answers
# print("✅ Loaded reference answers:", reference_answers)






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


    attempt_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state.attempt_dir = os.path.join(
        "interviews",
        f"{st.session_state.candidate_id}_{attempt_id}"
    )
    os.makedirs(st.session_state.attempt_dir, exist_ok=True)

def show_countdown(message, secs=3):
    ph = st.empty()
    for remaining in range(secs, 0, -1):
        # render_face_monitor()
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







RECORDING_DURATION = 25
st.title("AI-powered Viva-Voice System")

# ---------- confirm ID ----------
if not st.session_state.id_confirmed:
    try:
        r = requests.get(f"http://localhost:5000/api/student/student/{student_id}", timeout=3)
        if r.status_code == 200 and r.json().get("photo"):
            st.image(r.json()["photo"], caption="Candidate Photo", width=180)
    except Exception:
        pass

    # cand_in = st.text_input("Enter your Candidate ID to begin:", value=student_id)
    # if st.button("Confirm ID"):
    #     if cand_in == student_id:
    #         st.session_state.id_confirmed = True
    #         st.rerun()
    #     else:
    #         st.error("❌ Entered ID does not match.")
    # st.stop()

# ---------- start interview: welcome is BLOCKING, then start camera ----------

#



# ---------- rules popup (before showing Start button) ----------



if "rules_accepted" not in st.session_state:
    st.session_state.rules_accepted = False
if "interview_started" not in st.session_state:
    st.session_state.interview_started = False

# -------------------
if "camera_checked" not in st.session_state:
    st.session_state.camera_checked = False




# ---------- confirm ID ----------
if not st.session_state.id_confirmed:
    cand_in = st.text_input("Enter your Candidate ID to begin:", value=student_id)
    if st.button("Confirm ID"):
        if cand_in == student_id:
            st.session_state.id_confirmed = True

            # Show banner here only once
            st.success(f"ID '{student_id}' registered successfully.")
            st.rerun()
        else:
            st.error("❌ Entered ID does not match.")
    st.stop()

# ---------- Rules Page ----------
# if not st.session_state.rules_accepted:
#     st.header("Viva Rules & Regulations")
#     st.markdown(
#         """
#         - Camera must remain **ON** during viva.  
#         - Face must remain **clearly visible**.  
#         - No background noise or external help.  
#         - Answer clearly within the **time limit**.  
#         - Once you proceed, viva will begin.  
#         """
#     )

if not st.session_state.rules_accepted:
    st.header("Viva Rules & Regulations")
    st.markdown(
        """
        - Throughout the exam, you will be under **camera monitoring** and your behavior will be logged.  
        - Any **undesirable behavior** may lead to **disqualification**.  
        - Ensure you have a **high-speed internet connection**, a **quiet environment**, and a room with **proper lighting**.  
        - **Do not switch tabs** or leave the viva window; such actions will be monitored and logged.  
        - Answer **within the time limit** for each question. You will have **45 seconds per question**. 
        - After the beep sound, you may start answering, and continue until the timer ends and the beep sounds again.  
        - Speak **clearly and loudly** so your answers can be accurately recorded and assessed. 
        - Once you click **Start Exam**, the viva will begin. After submitting your responses, **please wait** for results and feedback.  

        **Thank you! Wishing you the best viva experience.**
        """
    )



    agree = st.checkbox(" I have read and agree to the rules")
    proceed_btn = st.button("Proceed", disabled=not agree)

    st.markdown(
        """
        <style>
        div.stButton > button {
            background-color: #4285F4 !important;
            color: white !important;
            font-weight: bold;
            border-radius: 8px;
            height: 3em;
        }
        div.stButton > button:disabled {
            background-color: #a0c4ff !important;
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if proceed_btn and agree:
        st.session_state.rules_accepted = True
        st.rerun()
    st.stop()

# ---------- Camera Check Page ----------
if st.session_state.rules_accepted and not st.session_state.camera_checked:
    st.header("Camera Check")
    st.markdown("Please adjust your camera so that only your face is visible.")

    ensure_camera_started()
    ready = camera_check_ui()

    if ready:
        st.session_state.camera_checked = True
        st.rerun()
    st.stop()




# ---------- Start Test Page ----------


if st.session_state.camera_checked and not st.session_state.interview_started: 
# if not st.session_state.interview_started:
    st.success(" Click Start Test to begin the viva.")

    if st.button("Start Test", key="start_test_btn"):
        with st.spinner("Playing welcome message..."):
            speak("Welcome to this Examination. Please listen carefully and answer within the time limit.")
        ensure_camera_started()
        
        st.session_state.interview_started = True
        # start_tab_monitor(test_id, student_id, backend_url="http://localhost:5000/api")
        # start_tab_monitor()

        st.rerun()
    st.stop()





# ---------- interview running ----------
# candidate_dir = os.path.join("interviews", st.session_state.candidate_id)
candidate_dir = st.session_state.attempt_dir

os.makedirs(candidate_dir, exist_ok=True)

q_idx = st.session_state.current_q
if q_idx < len(questions) and not st.session_state.terminate_clicked:
    question = questions[q_idx]
    st.subheader(f"Question {q_idx + 1}: {question}")

    # Timer box placeholder always below the question
    st.session_state.timer_container = st.empty()


    # show monitor every render (no forced rerun here)
    # render_face_monitor()
    # render_face_monitor(throttle_secs=10, save_dir=candidate_dir)
    render_face_monitor(save_dir=candidate_dir, randomized=True)
    # render_face_monitor(save_dir="logs", randomized=True, show_alerts=False)



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


            score_single_response(st.session_state.candidate_id, question, transcript)


            st.session_state.is_recording = False
            st.session_state.recording_complete = False
            st.session_state.current_q += 1
            st.rerun()
        else:
            # gentle refresh ONLY while recording
            time.sleep(0.5)
            st.rerun()

# ---------- termination controls ----------

if not st.session_state.terminate_clicked and st.session_state.current_q >= len(questions):
    st.success("🎉 You've answered all questions. Please submit to view your results.")

    if st.button("Submit and Show Results", key="terminate_btn_final"):
        #  mark terminated so camera stops
        # stop_tab_monitor()

        st.session_state.terminate_clicked = True  

        #  stop camera explicitly
        cap = st.session_state.get("video_capture")
        if cap is not None:
            try:
                cap.release()
            except Exception:
                pass
            st.session_state.video_capture = None

        # candidate_dir = os.path.join("interviews", st.session_state.candidate_id)
        candidate_dir = st.session_state.attempt_dir
        os.makedirs(candidate_dir, exist_ok=True)

        # Save responses
        with open(os.path.join(candidate_dir, "responses.json"), "w") as f:
            json.dump(st.session_state.responses, f, indent=4)

        


        with st.spinner("Preparing your results..."):
            candidate_dir = st.session_state.attempt_dir
            scored_file = os.path.join(candidate_dir, "scored_responses.json")
            if not os.path.exists(scored_file):
        # fallback if something went wrong
               score_all_responses(st.session_state.candidate_id)



        st.switch_page("pages/thank_you.py")




# ---------- keep camera alive between questions WITHOUT hammering reruns ----------
if st.session_state.interview_started and not st.session_state.terminate_clicked and not st.session_state.is_recording:
    # render_face_monitor()
    render_face_monitor(save_dir=candidate_dir, randomized=True)
    # render_face_monitor(save_dir="logs", randomized=True, show_alerts=False)

    # mild refresh so preview updates (~2 fps) but UI stays responsive
    time.sleep(0.5)
    st.rerun()






























