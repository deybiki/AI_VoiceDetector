





import streamlit as st
import time, json, os, subprocess, asyncio, tempfile, threading
from datetime import datetime
import edge_tts, speech_recognition as sr, sounddevice as sd
from scipy.io.wavfile import write
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId
import streamlit.components.v1 as components
import base64
from mutagen.mp3 import MP3



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
# def speak(text):
#     try:
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:  # synthesize
#             fname = tmp.name
#         asyncio.run(edge_tts.Communicate(text, "en-IN-PrabhatNeural").save(fname))
#         subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", fname],
#                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#     finally:
#         try: os.remove(fname)
#         except Exception: pass

# def play_beep():
#     p = os.path.abspath("beep-05.wav")
#     if os.path.exists(p):
#         subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", p],
#                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def play_mp3_client_and_wait(mp3_path):
    if not os.path.exists(mp3_path):
        print("Missing mp3:", mp3_path)
        return
    with open(mp3_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    components.html(
        f'<audio autoplay>'
        f'<source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>',
        height=0,
        
    )
    try:
        duration = MP3(mp3_path).info.length
    except Exception:
        duration = 2.0
    time.sleep(duration + 0.15)



def play_beep_client():
    p = os.path.abspath("beep-05.wav")
    if not os.path.exists(p):
        return
    with open(p, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    components.html(f'<audio autoplay><source src="data:audio/wav;base64,{b64}" type="audio/wav"></audio>', height=0)


# def play_beep_client():
#     p = os.path.abspath("beep-05.wav")
#     if not os.path.exists(p):
#         return
#     with open(p, "rb") as f:
#         b64 = base64.b64encode(f.read()).decode()
#     components.html(
#         f"""
#         <audio autoplay>
#             <source src="data:audio/wav;base64,{b64}" type="audio/wav">
#         </audio>
#         """,
#         height=0,
#         key=f"beep_{time.time()}",  # 👈 force reload every call
#     )







def pre_synthesize_questions(questions, out_dir, voice="en-IN-PrabhatNeural"):
    os.makedirs(out_dir, exist_ok=True)
    for i, q in enumerate(questions, start=1):
        fname = os.path.join(out_dir, f"q{i}.mp3")
        if os.path.exists(fname):
            # print(f"[TTS] Skipping existing {fname}")
            continue
        try:
            # print(f"[TTS] Synthesizing q{i} ...")
            asyncio.run(edge_tts.Communicate(q, voice).save(fname))
        except Exception as e:
            print(f"[TTS] Error for q{i}: {e}")
            # optionally retry once
            try:
                asyncio.run(edge_tts.Communicate(q, voice).save(fname))
            except Exception as e2:
                print(f"[TTS] Retry failed: {e2}")


# def threaded_record_audio(filename, duration, fs=44100):
#     try:
#         audio = sd.rec(int(duration*fs), samplerate=fs, channels=1, dtype='int16')
#         sd.wait()
#         write(filename, fs, audio)
#     finally:
#         st.session_state['recording_complete'] = True


def threaded_record_audio(filename, duration, fs=44100):
    """Record in a background thread, write WAV and wait until file is visible & non-empty."""
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        write(filename, fs, audio)

        # Wait up to N seconds for file to appear and have a size > header size
        timeout = 5.0
        start = time.time()
        while True:
            if os.path.exists(filename) and os.path.getsize(filename) > 44:
                # file looks valid
                break
            if time.time() - start > timeout:
                print(f"[recording] timeout waiting for audio file: {filename}")
                break
            time.sleep(0.05)

    except Exception as e:
        print(f"[recording] error writing {filename}: {e}")
    finally:
        # Mark recording complete (consistent signal to main thread)
        st.session_state['recording_complete'] = True




# def transcribe_audio(filename):
#     if not filename or not os.path.exists(filename): return "No audio file."
#     r = sr.Recognizer()
#     with sr.AudioFile(filename) as src:
#         audio = r.record(src)
#     try:
#         return r.recognize_google(audio)
#     except sr.UnknownValueError:
#         return "Could not understand audio."
#     except sr.RequestError as e:
#         return f"API error: {e}"




def transcribe_audio(filename, wait_timeout=5.0):
    """
    Wait for the file to exist & be non-empty, then run speech_recognition.
    Returns a string (transcript) or "No audio file." / error messages.
    """
    if not filename:
        return "No audio file."
    path = os.path.abspath(filename)

    # Wait for file presence + reasonable size
    start = time.time()
    while True:
        if os.path.exists(path):
            try:
                size = os.path.getsize(path)
            except Exception:
                size = 0
            if size > 44:  # WAV header ~44 bytes; protects against zero-length
                break
        if time.time() - start > wait_timeout:
            print(f"[transcribe] file not present/too small after {wait_timeout}s: {path}")
            return "No audio file."
        time.sleep(0.08)

    # Now try transcription
    try:
        r = sr.Recognizer()
        with sr.AudioFile(path) as src:
            audio = r.record(src)
        try:
            text = r.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Could not understand audio."
        except sr.RequestError as e:
            return f"API error: {e}"
    except Exception as e:
        print(f"[transcribe] unexpected error for {path}: {e}")
        return f"Transcription error: {e}"







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



@st.cache_resource
def get_client(uri):
    return MongoClient(uri)

# Create client only once
client = get_client(MONGO_URI)

# Pick the database (example: "test")
db = client["test"]

# Pick the collection
tests_collection = db["tests"]

# Example debug
# st.write("✅ Connected to MongoDB, using DB:", db.name)





# client = MongoClient(MONGO_URI)

# db = client.get_database("test")

# tests_collection = db.get_collection("tests")

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

# pre_synthesize_questions(questions, st.session_state.attempt_dir)






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

# pre_synthesize_questions(questions, st.session_state.attempt_dir)

with st.spinner("⏳ Exam is loading, please wait..."):
    pre_synthesize_questions(questions, st.session_state.attempt_dir)


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







RECORDING_DURATION = 30
st.title("AI-powered Viva-Voce System")

# ---------- confirm ID ----------
if not st.session_state.id_confirmed:
    try:
        r = requests.get(f"http://localhost:5000/api/student/student/{student_id}", timeout=3)
        if r.status_code == 200 and r.json().get("photo"):
            st.image(r.json()["photo"], caption="Candidate Photo", width=180)
    except Exception:
        pass

    

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

if not st.session_state.rules_accepted:
    st.header("Viva Rules & Regulations")
    st.markdown(
        """
        - Throughout the exam, you will be under **camera monitoring** and your behavior will be logged.  
        - Any **undesirable behavior** may lead to **disqualification**.  
        - Ensure you have a **high-speed internet connection**, a **quiet environment**, and a room with **proper lighting**.  
        - **Do not switch tabs** or leave the viva window; such actions will be monitored and logged.  
        - Answer **within the time limit** for each question. You will have **30 seconds per question**. 
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




# Pre-synthesize all questions at once (optional)







# ---------- Start Test Page ----------


if st.session_state.camera_checked and not st.session_state.interview_started: 
# if not st.session_state.interview_started:
    st.success(" Click Start Test to begin the viva.")

    if st.button("Start Test", key="start_test_btn"):
        with st.spinner("Playing welcome message..."):
            # speak("Welcome to this Examination. Please listen carefully and answer within the time limit.")
              welcome_path = os.path.join(st.session_state.attempt_dir, "welcome.mp3")
              if not os.path.exists(welcome_path):
                 asyncio.run(edge_tts.Communicate(
                      "Welcome to this Examination. Please listen carefully and answer within the time limit.",
                      "en-IN-PrabhatNeural"
            ).save(welcome_path))

        play_mp3_client_and_wait(welcome_path)


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

        # play_beep()
        # speak(question)   # blocking
        # play_beep()

        # play_beep_client()  # browser plays beep
        mp3_path = os.path.join(st.session_state.attempt_dir, f"q{q_idx + 1}.mp3")
        play_mp3_client_and_wait(mp3_path)  # browser plays synthesized question
        # play_beep_client()

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
            # play_beep()
            play_beep_client()  # end signal
            time.sleep(0.2)  # small gap for file flush

            st.session_state.timer_container.markdown("### ⏰ **Oops! Time's up!**")
            time.sleep(1)

            # audio_fname = os.path.join(candidate_dir, f"q{q_idx + 1}_answer.wav")
            audio_fname = os.path.abspath(os.path.join(candidate_dir, f"q{q_idx + 1}_answer.wav"))
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






































































































































































































































































































# import streamlit as st
# import time, json, os, subprocess, asyncio, tempfile
# from datetime import datetime
# import edge_tts, requests
# from pymongo import MongoClient
# from dotenv import load_dotenv
# from bson import ObjectId
# import streamlit.components.v1 as components
# import base64
# from mutagen.mp3 import MP3

# # --- COMPONENT IMPORTS ---
# from face_monitor import render_face_monitor, ensure_camera_started, camera_check_ui
# from llm_scoring import score_all_responses, score_single_response

# st.set_page_config(page_title="AI Viva System", layout="wide", initial_sidebar_state="collapsed")
# st.markdown("""<style>[data-testid="stSidebar"], [data-testid="collapsedControl"]{display:none!important}</style>""", unsafe_allow_html=True)

# st.markdown("""
# <style>
# @keyframes pulse { 
#   0% { transform: scale(1); } 
#   50% { transform: scale(1.06); } 
#   100% { transform: scale(1); } 
# }
# </style>
# """, unsafe_allow_html=True)

# # ---------- CONFIGURATION ----------
# RECORDING_DURATION = 30  # seconds

# # ---------- HELPER FUNCTIONS ----------

# def play_mp3_client_and_wait(mp3_path):
#     """Play MP3 in browser and wait for duration"""
#     if not os.path.exists(mp3_path):
#         print("Missing mp3:", mp3_path)
#         return
#     with open(mp3_path, "rb") as f:
#         b64 = base64.b64encode(f.read()).decode()
#     components.html(
#         f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>',
#         height=0,
#     )
#     try:
#         duration = MP3(mp3_path).info.length
#     except Exception:
#         duration = 2.0
#     time.sleep(duration + 0.15)


# def play_beep_client():
#     """Play beep sound in browser"""
#     p = os.path.abspath("beep-05.wav")
#     if not os.path.exists(p):
#         return
#     with open(p, "rb") as f:
#         b64 = base64.b64encode(f.read()).decode()
#     components.html(
#         f'<audio autoplay><source src="data:audio/wav;base64,{b64}" type="audio/wav"></audio>', 
#         height=0
#     )


# def pre_synthesize_questions(questions, out_dir, voice="en-IN-PrabhatNeural"):
#     """Pre-generate TTS for all questions"""
#     os.makedirs(out_dir, exist_ok=True)
#     for i, q in enumerate(questions, start=1):
#         fname = os.path.join(out_dir, f"q{i}.mp3")
#         if os.path.exists(fname):
#             continue
#         try:
#             asyncio.run(edge_tts.Communicate(q, voice).save(fname))
#         except Exception as e:
#             print(f"[TTS] Error for q{i}: {e}")


# def browser_audio_recorder(duration_sec, question_num):
#     """Browser-based audio recorder - simplified for reliability"""
    
#     recorder_html = f"""
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <style>
#             body {{ margin: 0; padding: 20px; font-family: system-ui; }}
#             #timer {{
#                 display: flex; flex-direction: column; align-items: center;
#                 padding: 28px 45px; border-radius: 16px;
#                 background: #fff; border: 2px solid #e5e7eb;
#                 box-shadow: 0 8px 20px rgba(0,0,0,0.1);
#                 text-align: center; min-width: 240px; margin: 20px auto;
#             }}
#             .time {{ color: #2563eb; font-size: 48px; font-weight: 800; }}
#             .label {{ color: #111827; font-size: 18px; font-weight: 600; margin-top: 12px; }}
#             .recording {{ color: #dc3545; margin-top: 12px; font-weight: bold; animation: blink 1.5s infinite; }}
#             @keyframes blink {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.4; }} }}
#         </style>
#     </head>
#     <body>
#         <div id="timer">
#             <div class="time" id="timeDisplay">{duration_sec}s</div>
#             <div class="label">Speak loudly & clearly</div>
#             <div class="recording" id="status">🔴 Recording...</div>
#         </div>

#         <script>
#             let mediaRecorder, audioChunks = [], startTime;
#             const duration = {duration_sec};

#             async function startRecording() {{
#                 try {{
#                     const stream = await navigator.mediaDevices.getUserMedia({{
#                         audio: {{ echoCancellation: true, noiseSuppression: true }}
#                     }});
                    
#                     let mimeType = 'audio/webm';
#                     if (!MediaRecorder.isTypeSupported(mimeType)) {{
#                         mimeType = 'audio/mp4';
#                     }}
                    
#                     mediaRecorder = new MediaRecorder(stream, {{ mimeType: mimeType }});
                    
#                     mediaRecorder.ondataavailable = (e) => {{
#                         if (e.data.size > 0) audioChunks.push(e.data);
#                     }};
                    
#                     mediaRecorder.onstop = () => {{
#                         const blob = new Blob(audioChunks, {{ type: mimeType }});
#                         console.log('✅ Recording complete:', blob.size, 'bytes');
#                         stream.getTracks().forEach(t => t.stop());
#                         document.getElementById('status').textContent = '✅ Saved!';
#                         document.getElementById('status').style.color = '#10b981';
#                         document.getElementById('status').style.animation = 'none';
#                     }};

#                     mediaRecorder.start(100);
#                     startTime = Date.now();
                    
#                     const timer = setInterval(() => {{
#                         const elapsed = Math.floor((Date.now() - startTime) / 1000);
#                         const remaining = Math.max(0, duration - elapsed);
#                         document.getElementById('timeDisplay').textContent = remaining + 's';
#                         if (remaining === 0) clearInterval(timer);
#                     }}, 100);
                    
#                     setTimeout(() => {{
#                         if (mediaRecorder && mediaRecorder.state === 'recording') {{
#                             mediaRecorder.stop();
#                         }}
#                     }}, duration * 1000);

#                 }} catch (err) {{
#                     console.error('Mic error:', err);
#                     document.getElementById('status').textContent = '❌ Mic denied';
#                     document.getElementById('status').style.color = '#ef4444';
#                 }}
#             }}

#             startRecording();
#         </script>
#     </body>
#     </html>
#     """
    
#     components.html(recorder_html, height=200, scrolling=False)


# def show_countdown(message, secs=3):
#     """Display countdown timer"""
#     ph = st.empty()
#     for remaining in range(secs, 0, -1):
#         ph.markdown(
#             f"""
#             <div style="display: flex; justify-content: center; margin: 20px 0;">
#                 <div style="padding: 20px 40px; border-radius: 12px; background: #f9f9f9;
#                             border: 1px solid #e5e7eb; text-align: center; 
#                             box-shadow: 0 4px 10px rgba(0,0,0,.08);">
#                     {message}<br/>
#                     <span style="color:#2563eb; font-size:34px;">{remaining}</span>
#                 </div>
#             </div>
#             """,
#             unsafe_allow_html=True
#         )
#         time.sleep(1)
#     ph.empty()


# # ---------- STATE INITIALIZATION ----------
# if 'current_q' not in st.session_state: 
#     st.session_state.current_q = 0
# if 'responses' not in st.session_state: 
#     st.session_state.responses = []
# if 'candidate_id' not in st.session_state: 
#     st.session_state.candidate_id = ""
# if 'timer_start_time' not in st.session_state:
#     st.session_state.timer_start_time = 0

# for k in ['interview_started', 'id_confirmed', 'terminate_clicked', 'is_recording', 
#           'recording_complete', 'rules_accepted', 'camera_checked']:
#     st.session_state.setdefault(k, False)

# # ---------- MONGODB SETUP ----------
# load_dotenv("../backend/.env")
# MONGO_URI = os.getenv("MONGO_URI")

# @st.cache_resource
# def get_client(uri):
#     return MongoClient(uri)

# client = get_client(MONGO_URI)
# db = client["test"]
# tests_collection = db["tests"]

# # ---------- GET TEST DATA ----------
# query_params = st.query_params
# test_id = str(query_params.get("testId", "")).strip()
# st.session_state["test_id"] = test_id

# student_id = str(query_params.get("studentId", "")).strip()
# if not test_id or not student_id:
#     st.error("❌ Missing IDs")
#     st.stop()

# test_data = tests_collection.find_one({"sharedLinkId": test_id})
# if not test_data:
#     st.error("❌ Invalid Test ID")
#     st.stop()

# test_description = test_data.get("description", "No description available")
# st.session_state["test_description"] = test_description

# # Load questions and answers
# qids = test_data.get("questions", [])
# answers_data = list(db.get_collection("testanswers").find({"testId": ObjectId(test_data["_id"])}))

# questions, reference_answers = [], []
# for q in db.get_collection("questions").find({"_id": {"$in": [ObjectId(x) for x in qids]}}):
#     questions.append(q.get("questionText", "Error"))

# reference_answers = [a.get("answerText", "") for a in answers_data]

# if not questions:
#     st.error("❌ No questions resolved")
#     st.stop()

# st.session_state.reference_answers = reference_answers

# # ---------- RESET STATE FOR NEW CANDIDATE ----------
# if st.session_state.get("candidate_id") != student_id:
#     st.session_state.candidate_id = student_id
#     st.session_state.responses = []
#     st.session_state.current_q = 0
#     st.session_state.terminate_clicked = False
#     st.session_state.interview_started = False
#     st.session_state.id_confirmed = False
#     st.session_state.is_recording = False
#     st.session_state.recording_complete = False
#     st.session_state.rules_accepted = False
#     st.session_state.camera_checked = False

#     attempt_id = datetime.now().strftime("%Y%m%d_%H%M%S")
#     st.session_state.attempt_dir = os.path.join(
#         "interviews",
#         f"{st.session_state.candidate_id}_{attempt_id}"
#     )
#     os.makedirs(st.session_state.attempt_dir, exist_ok=True)

# # Pre-synthesize questions
# with st.spinner("⏳ Exam is loading, please wait..."):
#     pre_synthesize_questions(questions, st.session_state.attempt_dir)

# st.title("AI-powered Viva-Voce System")

# # ---------- ID CONFIRMATION ----------
# if not st.session_state.id_confirmed:
#     try:
#         r = requests.get(f"http://localhost:5000/api/student/student/{student_id}", timeout=3)
#         if r.status_code == 200 and r.json().get("photo"):
#             st.image(r.json()["photo"], caption="Candidate Photo", width=180)
#     except Exception:
#         pass

#     cand_in = st.text_input("Enter your Candidate ID to begin:", value=student_id)
#     if st.button("Confirm ID"):
#         if cand_in == student_id:
#             st.session_state.id_confirmed = True
#             st.success(f"ID '{student_id}' registered successfully.")
#             st.rerun()
#         else:
#             st.error("❌ Entered ID does not match.")
#     st.stop()

# # ---------- RULES PAGE ----------
# if not st.session_state.rules_accepted:
#     st.header("Viva Rules & Regulations")
#     st.markdown(
#         """
#         - Throughout the exam, you will be under **camera monitoring** and your behavior will be logged.  
#         - Any **undesirable behavior** may lead to **disqualification**.  
#         - Ensure you have a **high-speed internet connection**, a **quiet environment**, and a room with **proper lighting**.  
#         - **Do not switch tabs** or leave the viva window; such actions will be monitored and logged.  
#         - Answer **within the time limit** for each question. You will have **30 seconds per question**. 
#         - After the beep sound, you may start answering, and continue until the timer ends and the beep sounds again.  
#         - Speak **clearly and loudly** so your answers can be accurately recorded and assessed. 
#         - Once you click **Start Exam**, the viva will begin. After submitting your responses, **please wait** for results and feedback.  

#         **Thank you! Wishing you the best viva experience.**
#         """
#     )

#     agree = st.checkbox("✅ I have read and agree to the rules")
#     proceed_btn = st.button("Proceed", disabled=not agree)

#     st.markdown(
#         """
#         <style>
#         div.stButton > button {
#             background-color: #4285F4 !important;
#             color: white !important;
#             font-weight: bold;
#             border-radius: 8px;
#             height: 3em;
#         }
#         div.stButton > button:disabled {
#             background-color: #a0c4ff !important;
#             color: white !important;
#         }
#         </style>
#         """,
#         unsafe_allow_html=True,
#     )

#     if proceed_btn and agree:
#         st.session_state.rules_accepted = True
#         st.rerun()
#     st.stop()

# # ---------- CAMERA CHECK PAGE ----------
# if st.session_state.rules_accepted and not st.session_state.camera_checked:
#     st.header("Camera Check")
#     st.markdown("Please adjust your camera so that only your face is visible.")

#     ensure_camera_started()
#     ready = camera_check_ui()

#     if ready:
#         st.session_state.camera_checked = True
#         st.success("✅ Camera check complete! Proceeding to test...")
#         time.sleep(1)
#         st.rerun()
    
#     st.stop()

# # ---------- START TEST PAGE ----------
# if st.session_state.camera_checked and not st.session_state.interview_started:
#     st.success("✅ Click Start Test to begin the viva.")

#     if st.button("Start Test", key="start_test_btn"):
#         with st.spinner("Playing welcome message..."):
#             welcome_path = os.path.join(st.session_state.attempt_dir, "welcome.mp3")
#             if not os.path.exists(welcome_path):
#                 asyncio.run(edge_tts.Communicate(
#                     "Welcome to this Examination. Please listen carefully and answer within the time limit.",
#                     "en-IN-PrabhatNeural"
#                 ).save(welcome_path))

#         play_mp3_client_and_wait(welcome_path)
#         ensure_camera_started()
#         st.session_state.interview_started = True
#         st.rerun()
#     st.stop()

# # ---------- INTERVIEW RUNNING ----------
# candidate_dir = st.session_state.attempt_dir
# os.makedirs(candidate_dir, exist_ok=True)

# q_idx = st.session_state.current_q

# if q_idx < len(questions) and not st.session_state.terminate_clicked:
#     question = questions[q_idx]
#     st.subheader(f"Question {q_idx + 1} of {len(questions)}: {question}")

#     # Show camera monitor
#     render_face_monitor(save_dir=candidate_dir, randomized=True)

#     # STEP 1: Play question
#     if not st.session_state.is_recording:
#         q_key = f"auto_started_q{q_idx}"
#         if not st.session_state.get(q_key, False):
#             st.session_state[q_key] = True
            
#         show_countdown("Question will start in", secs=3)

#         mp3_path = os.path.join(st.session_state.attempt_dir, f"q{q_idx + 1}.mp3")
#         play_mp3_client_and_wait(mp3_path)
#         time.sleep(1)

#         st.session_state.is_recording = True
#         st.session_state.recording_complete = False
#         st.session_state.timer_start_time = time.time()
#         st.rerun()

#     # STEP 2: Recording - AUTO ADVANCE
#     if st.session_state.is_recording and not st.session_state.recording_complete:
#         browser_audio_recorder(RECORDING_DURATION, q_idx + 1)
        
#         elapsed = time.time() - st.session_state.timer_start_time
#         remaining = max(0, int(RECORDING_DURATION - elapsed))
        
#         if remaining > 0:
#             st.info(f"⏱️ Time remaining: {remaining} seconds")
        
#         # AUTO ADVANCE after duration + buffer
#         if elapsed >= (RECORDING_DURATION + 2):
#             st.session_state.recording_complete = True
#             st.rerun()
#         else:
#             time.sleep(1)
#             st.rerun()

#     # STEP 3: Process and move to next
#     if st.session_state.recording_complete:
#         play_beep_client()
#         st.success("✅ Recording complete!")
#         time.sleep(1)
        
#         # Save marker file
#         audio_marker = os.path.join(candidate_dir, f"q{q_idx + 1}_recorded.txt")
#         with open(audio_marker, "w") as f:
#             f.write(f"Audio recorded at {datetime.now().isoformat()}")
        
#         transcript = f"[Audio answer recorded for question {q_idx + 1}]"
        
#         st.session_state.responses.append({
#             "question_number": q_idx + 1,
#             "question": question,
#             "audio_file": audio_marker,
#             "transcript": transcript
#         })

#         # Score response
#         try:
#             score_single_response(st.session_state.candidate_id, question, transcript)
#         except Exception as e:
#             print(f"Scoring error: {e}")

#         # Move to next question
#         st.session_state.is_recording = False
#         st.session_state.recording_complete = False
#         st.session_state.current_q += 1
        
#         st.success(f"✅ Question {q_idx + 1} completed! Moving to next...")
#         time.sleep(1.5)
#         st.rerun()

# # ---------- SUBMISSION ----------
# if not st.session_state.terminate_clicked and st.session_state.current_q >= len(questions):
#     st.balloons()
#     st.success("🎉 You've answered all questions! Please submit to view your results.")

#     if st.button("Submit and Show Results", key="terminate_btn_final", type="primary"):
#         st.session_state.terminate_clicked = True

#         # Save responses
#         with open(os.path.join(candidate_dir, "responses.json"), "w") as f:
#             json.dump(st.session_state.responses, f, indent=4)

#         with st.spinner("Preparing your results..."):
#             scored_file = os.path.join(candidate_dir, "scored_responses.json")
#             if not os.path.exists(scored_file):
#                 score_all_responses(st.session_state.candidate_id)

#         st.switch_page("pages/thank_you.py")

# # ---------- KEEP CAMERA ALIVE ----------
# if st.session_state.interview_started and not st.session_state.terminate_clicked and not st.session_state.is_recording:
#     render_face_monitor(save_dir=candidate_dir, randomized=True)
#     time.sleep(0.5)
#     st.rerun()























































































































# import streamlit as st
# import time, json, os, asyncio
# from datetime import datetime
# import edge_tts, requests
# from pymongo import MongoClient
# from dotenv import load_dotenv
# from bson import ObjectId
# import streamlit.components.v1 as components
# import base64
# from mutagen.mp3 import MP3

# # --- COMPONENT IMPORTS ---
# from face_monitor import render_face_monitor, ensure_camera_started, camera_check_ui
# from llm_scoring import score_all_responses, score_single_response

# st.set_page_config(page_title="AI Viva System", layout="wide", initial_sidebar_state="collapsed")
# st.markdown("""<style>[data-testid="stSidebar"], [data-testid="collapsedControl"]{display:none!important}</style>""", unsafe_allow_html=True)

# RECORDING_DURATION = 30

# def play_mp3_client_and_wait(mp3_path):
#     if not os.path.exists(mp3_path):
#         return
#     with open(mp3_path, "rb") as f:
#         b64 = base64.b64encode(f.read()).decode()
#     components.html(f'<audio autoplay><source src="data:audio/mp3;base64,{b64}"></audio>', height=0)
#     try:
#         duration = MP3(mp3_path).info.length
#     except:
#         duration = 2.0
#     time.sleep(duration + 0.15)

# def play_beep_client():
#     p = os.path.abspath("beep-05.wav")
#     if not os.path.exists(p):
#         return
#     with open(p, "rb") as f:
#         b64 = base64.b64encode(f.read()).decode()
#     components.html(f'<audio autoplay><source src="data:audio/wav;base64,{b64}"></audio>', height=0)

# def pre_synthesize_questions(questions, out_dir, voice="en-IN-PrabhatNeural"):
#     os.makedirs(out_dir, exist_ok=True)
#     for i, q in enumerate(questions, start=1):
#         fname = os.path.join(out_dir, f"q{i}.mp3")
#         if os.path.exists(fname):
#             continue
#         try:
#             asyncio.run(edge_tts.Communicate(q, voice).save(fname))
#         except Exception as e:
#             print(f"[TTS] Error: {e}")

# def browser_recorder_with_speech_recognition(duration_sec, question_num):
#     """
#     Records audio AND transcribes in real-time using Web Speech API.
#     NO file upload needed - transcript sent directly to Python!
#     """
    
#     recorder_html = f"""
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <style>
#             body {{ margin: 0; padding: 20px; font-family: system-ui; }}
#             #container {{ display: flex; flex-direction: column; align-items: center; }}
#             #timer {{
#                 display: flex; flex-direction: column; align-items: center;
#                 padding: 28px 45px; border-radius: 16px;
#                 background: #fff; border: 2px solid #e5e7eb;
#                 box-shadow: 0 8px 20px rgba(0,0,0,0.1);
#                 min-width: 280px; margin: 20px auto;
#             }}
#             .time {{ color: #2563eb; font-size: 48px; font-weight: 800; }}
#             .label {{ color: #111827; font-size: 18px; font-weight: 600; margin-top: 12px; }}
#             .recording {{ color: #dc3545; margin-top: 12px; font-weight: bold; animation: blink 1.5s infinite; }}
#             @keyframes blink {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.4; }} }}
#             #transcript {{
#                 margin-top: 20px; padding: 15px; background: #f0f9ff;
#                 border-radius: 8px; min-height: 80px; max-width: 600px;
#                 border-left: 4px solid #3b82f6; font-size: 15px;
#                 color: #1e40af; line-height: 1.6;
#             }}
#             .transcript-label {{ font-weight: 600; color: #1e3a8a; margin-bottom: 8px; }}
#         </style>
#     </head>
#     <body>
#         <div id="container">
#             <div id="timer">
#                 <div class="time" id="timeDisplay">{duration_sec}s</div>
#                 <div class="label">Speak loudly & clearly</div>
#                 <div class="recording" id="status">🔴 Recording...</div>
#             </div>
            
#             <div id="transcript">
#                 <div class="transcript-label">📝 Live Transcript:</div>
#                 <div id="transcriptText">Listening...</div>
#             </div>
#         </div>

#         <script>
#             let mediaRecorder, audioChunks = [], startTime;
#             let recognition;
#             let finalTranscript = '';
#             let interimTranscript = '';
#             const duration = {duration_sec};
#             const questionNum = {question_num};

#             // Web Speech API Setup
#             const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            
#             if (!SpeechRecognition) {{
#                 document.getElementById('status').textContent = '❌ Speech recognition not supported';
#                 document.getElementById('transcriptText').textContent = 'Please use Chrome, Edge, or Safari';
#             }} else {{
#                 recognition = new SpeechRecognition();
#                 recognition.continuous = true;
#                 recognition.interimResults = true;
#                 recognition.lang = 'en-US';

#                 recognition.onresult = (event) => {{
#                     interimTranscript = '';
                    
#                     for (let i = event.resultIndex; i < event.results.length; i++) {{
#                         const transcript = event.results[i][0].transcript;
#                         if (event.results[i].isFinal) {{
#                             finalTranscript += transcript + ' ';
#                         }} else {{
#                             interimTranscript += transcript;
#                         }}
#                     }}
                    
#                     // Update display
#                     const display = finalTranscript + interimTranscript;
#                     document.getElementById('transcriptText').textContent = display || 'Listening...';
#                 }};

#                 recognition.onerror = (event) => {{
#                     console.error('Speech recognition error:', event.error);
#                 }};
#             }}

#             async function startRecording() {{
#                 try {{
#                     // Start audio recording (for backup)
#                     const stream = await navigator.mediaDevices.getUserMedia({{
#                         audio: {{ echoCancellation: true, noiseSuppression: true }}
#                     }});
                    
#                     mediaRecorder = new MediaRecorder(stream);
#                     mediaRecorder.ondataavailable = e => {{ if (e.data.size > 0) audioChunks.push(e.data); }};
                    
#                     mediaRecorder.onstop = () => {{
#                         const blob = new Blob(audioChunks, {{ type: 'audio/webm' }});
#                         console.log('Audio recorded:', blob.size, 'bytes');
                        
#                         // Save transcript to sessionStorage
#                         sessionStorage.setItem('transcript_q' + questionNum, finalTranscript.trim());
#                         sessionStorage.setItem('transcript_q' + questionNum + '_ready', 'true');
                        
#                         document.getElementById('status').textContent = '✅ Complete!';
#                         document.getElementById('status').style.color = '#10b981';
#                         document.getElementById('status').style.animation = 'none';
                        
#                         stream.getTracks().forEach(t => t.stop());
#                     }};

#                     // Start both recording and recognition
#                     mediaRecorder.start(100);
#                     if (recognition) {{
#                         recognition.start();
#                     }}
                    
#                     startTime = Date.now();
                    
#                     // Update timer
#                     const timerInterval = setInterval(() => {{
#                         const elapsed = Math.floor((Date.now() - startTime) / 1000);
#                         const remaining = Math.max(0, duration - elapsed);
#                         document.getElementById('timeDisplay').textContent = remaining + 's';
                        
#                         if (remaining === 0) {{
#                             clearInterval(timerInterval);
#                         }}
#                     }}, 100);
                    
#                     // Auto-stop after duration
#                     setTimeout(() => {{
#                         if (mediaRecorder && mediaRecorder.state === 'recording') {{
#                             mediaRecorder.stop();
#                         }}
#                         if (recognition) {{
#                             recognition.stop();
#                         }}
#                     }}, duration * 1000);

#                 }} catch (err) {{
#                     console.error('Mic error:', err);
#                     document.getElementById('status').textContent = '❌ Mic denied';
#                     document.getElementById('status').style.color = '#ef4444';
#                 }}
#             }}

#             startRecording();
#         </script>
#     </body>
#     </html>
#     """
    
#     components.html(recorder_html, height=400, scrolling=False)

# def get_transcript_from_browser(question_num):
#     """Retrieve transcript from browser's sessionStorage"""
    
#     retrieval_script = f"""
#     <script>
#         const questionNum = {question_num};
#         const transcript = sessionStorage.getItem('transcript_q' + questionNum);
#         const isReady = sessionStorage.getItem('transcript_q' + questionNum + '_ready');
        
#         if (isReady === 'true' && transcript) {{
#             // Create a hidden element with the transcript
#             const div = document.createElement('div');
#             div.id = 'transcript_data';
#             div.setAttribute('data-transcript', transcript);
#             div.style.display = 'none';
#             document.body.appendChild(div);
            
#             // Also log it
#             console.log('Transcript ready:', transcript);
            
#             // Clean up
#             sessionStorage.removeItem('transcript_q' + questionNum);
#             sessionStorage.removeItem('transcript_q' + questionNum + '_ready');
#         }}
#     </script>
#     """
    
#     components.html(retrieval_script, height=0)

# def show_countdown(message, secs=3):
#     ph = st.empty()
#     for remaining in range(secs, 0, -1):
#         ph.markdown(f"""
#             <div style="display: flex; justify-content: center; margin: 20px 0;">
#                 <div style="padding: 20px 40px; border-radius: 12px; background: #f9f9f9;
#                             border: 1px solid #e5e7eb; text-align: center;">
#                     {message}<br/><span style="color:#2563eb; font-size:34px;">{remaining}</span>
#                 </div>
#             </div>
#             """, unsafe_allow_html=True)
#         time.sleep(1)
#     ph.empty()

# # ---------- STATE INITIALIZATION ----------
# if 'current_q' not in st.session_state: st.session_state.current_q = 0
# if 'responses' not in st.session_state: st.session_state.responses = []
# if 'candidate_id' not in st.session_state: st.session_state.candidate_id = ""
# if 'timer_start_time' not in st.session_state: st.session_state.timer_start_time = 0
# if 'current_transcript' not in st.session_state: st.session_state.current_transcript = ""

# for k in ['interview_started', 'id_confirmed', 'terminate_clicked', 'is_recording', 
#           'recording_complete', 'rules_accepted', 'camera_checked']:
#     st.session_state.setdefault(k, False)

# # ---------- MONGODB SETUP ----------
# load_dotenv("../backend/.env")
# MONGO_URI = os.getenv("MONGO_URI")

# @st.cache_resource
# def get_client(uri):
#     return MongoClient(uri)

# client = get_client(MONGO_URI)
# db = client["test"]
# tests_collection = db["tests"]

# # ---------- GET TEST DATA ----------
# query_params = st.query_params
# test_id = str(query_params.get("testId", "")).strip()
# student_id = str(query_params.get("studentId", "")).strip()

# if not test_id or not student_id:
#     st.error("❌ Missing IDs")
#     st.stop()

# test_data = tests_collection.find_one({"sharedLinkId": test_id})
# if not test_data:
#     st.error("❌ Invalid Test ID")
#     st.stop()

# qids = test_data.get("questions", [])
# answers_data = list(db.get_collection("testanswers").find({"testId": ObjectId(test_data["_id"])}))

# questions, reference_answers = [], []
# for q in db.get_collection("questions").find({"_id": {"$in": [ObjectId(x) for x in qids]}}):
#     questions.append(q.get("questionText", "Error"))
# reference_answers = [a.get("answerText", "") for a in answers_data]

# if not questions:
#     st.error("❌ No questions")
#     st.stop()

# st.session_state.reference_answers = reference_answers

# # ---------- RESET STATE ----------
# if st.session_state.get("candidate_id") != student_id:
#     st.session_state.candidate_id = student_id
#     st.session_state.responses = []
#     st.session_state.current_q = 0
#     st.session_state.terminate_clicked = False
#     st.session_state.interview_started = False
#     st.session_state.id_confirmed = False
#     st.session_state.is_recording = False
#     st.session_state.recording_complete = False
#     st.session_state.rules_accepted = False
#     st.session_state.camera_checked = False
#     st.session_state.current_transcript = ""

#     attempt_id = datetime.now().strftime("%Y%m%d_%H%M%S")
#     st.session_state.attempt_dir = os.path.join("interviews", f"{student_id}_{attempt_id}")
#     os.makedirs(st.session_state.attempt_dir, exist_ok=True)

# with st.spinner("⏳ Loading..."):
#     pre_synthesize_questions(questions, st.session_state.attempt_dir)

# st.title("AI-powered Viva-Voce System")

# # ---------- ID CONFIRMATION ----------
# if not st.session_state.id_confirmed:
#     try:
#         r = requests.get(f"http://localhost:5000/api/student/student/{student_id}", timeout=3)
#         if r.status_code == 200 and r.json().get("photo"):
#             st.image(r.json()["photo"], caption="Candidate Photo", width=180)
#     except:
#         pass

#     cand_in = st.text_input("Enter ID:", value=student_id)
#     if st.button("Confirm"):
#         if cand_in == student_id:
#             st.session_state.id_confirmed = True
#             st.success("Registered!")
#             st.rerun()
#         else:
#             st.error("❌ Mismatch")
#     st.stop()

# # ---------- RULES ----------
# if not st.session_state.rules_accepted:
#     st.header("Rules")
#     st.markdown("""
#         - Camera monitoring active
#         - 30 seconds per question
#         - Speak clearly
#         - No tab switching
#         """)
#     if st.button("I Agree"):
#         st.session_state.rules_accepted = True
#         st.rerun()
#     st.stop()

# # ---------- CAMERA CHECK ----------
# if not st.session_state.camera_checked:
#     st.header("Camera Check")
#     ensure_camera_started()
#     if camera_check_ui():
#         st.session_state.camera_checked = True
#         st.rerun()
#     st.stop()

# # ---------- START TEST ----------
# if not st.session_state.interview_started:
#     if st.button("Start Test"):
#         welcome_path = os.path.join(st.session_state.attempt_dir, "welcome.mp3")
#         if not os.path.exists(welcome_path):
#             asyncio.run(edge_tts.Communicate(
#                 "Welcome to this Examination. Please listen carefully and answer within the time limit.",
#                 "en-IN-PrabhatNeural"
#             ).save(welcome_path))
#         play_mp3_client_and_wait(welcome_path)
#         st.session_state.interview_started = True
#         st.rerun()
#     st.stop()

# # ---------- INTERVIEW ----------
# candidate_dir = st.session_state.attempt_dir
# q_idx = st.session_state.current_q

# if q_idx < len(questions) and not st.session_state.terminate_clicked:
#     question = questions[q_idx]
#     st.subheader(f"Q{q_idx + 1}/{len(questions)}: {question}")
    
#     render_face_monitor(save_dir=candidate_dir, randomized=True)

#     if not st.session_state.is_recording:
#         show_countdown("Starting in", secs=3)
#         mp3_path = os.path.join(st.session_state.attempt_dir, f"q{q_idx + 1}.mp3")
#         play_mp3_client_and_wait(mp3_path)
        
#         st.session_state.is_recording = True
#         st.session_state.recording_complete = False
#         st.session_state.timer_start_time = time.time()
#         st.session_state.current_transcript = ""
#         st.rerun()

#     if st.session_state.is_recording and not st.session_state.recording_complete:
#         browser_recorder_with_speech_recognition(RECORDING_DURATION, q_idx + 1)
#         get_transcript_from_browser(q_idx + 1)
        
#         elapsed = time.time() - st.session_state.timer_start_time
#         remaining = max(0, int(RECORDING_DURATION - elapsed))
        
#         if remaining > 0:
#             st.info(f"⏱️ {remaining}s remaining")
        
#         # Auto-advance after recording
#         if elapsed >= (RECORDING_DURATION + 2):
#             st.session_state.recording_complete = True
#             st.rerun()
#         else:
#             time.sleep(1)
#             st.rerun()

#     if st.session_state.recording_complete:
#         play_beep_client()
        
#         # Use a text input as workaround to get transcript
#         st.markdown("### 📝 Your Answer:")
#         transcript_input = st.text_area(
#             "Verify your transcript (auto-generated):",
#             value=st.session_state.current_transcript,
#             height=100,
#             key=f"transcript_q{q_idx + 1}",
#             help="This was automatically transcribed. You can edit if needed."
#         )
        
#         if st.button("✅ Confirm & Continue", type="primary"):
#             transcript = transcript_input if transcript_input.strip() else "[Speech not detected]"
            
#             # Save audio marker
#             audio_marker = os.path.join(candidate_dir, f"q{q_idx + 1}_recorded.txt")
#             with open(audio_marker, "w") as f:
#                 f.write(f"Transcript: {transcript}\nRecorded at: {datetime.now().isoformat()}")
            
#             st.session_state.responses.append({
#                 "question_number": q_idx + 1,
#                 "question": question,
#                 "audio_file": audio_marker,
#                 "transcript": transcript
#             })

#             try:
#                 score_single_response(st.session_state.candidate_id, question, transcript)
#             except Exception as e:
#                 print(f"Scoring error: {e}")

#             st.session_state.is_recording = False
#             st.session_state.recording_complete = False
#             st.session_state.current_q += 1
#             st.session_state.current_transcript = ""
            
#             st.success(f"✅ Q{q_idx + 1} complete!")
#             time.sleep(1)
#             st.rerun()

# # ---------- SUBMISSION ----------
# if not st.session_state.terminate_clicked and st.session_state.current_q >= len(questions):
#     st.balloons()
#     st.success("🎉 All questions complete!")
    
#     if st.button("Submit Results", type="primary"):
#         st.session_state.terminate_clicked = True
        
#         with open(os.path.join(candidate_dir, "responses.json"), "w") as f:
#             json.dump(st.session_state.responses, f, indent=4)
        
#         scored_file = os.path.join(candidate_dir, "scored_responses.json")
#         if not os.path.exists(scored_file):
#             score_all_responses(st.session_state.candidate_id)
        
#         st.switch_page("pages/thank_you.py")

# if st.session_state.interview_started and not st.session_state.terminate_clicked and not st.session_state.is_recording:
#     render_face_monitor(save_dir=candidate_dir, randomized=True)
#     time.sleep(0.5)
#     st.rerun()








