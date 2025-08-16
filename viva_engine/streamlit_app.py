

# streamlit_app.py

import streamlit as st
import time
import json
import os
import subprocess
import asyncio
import edge_tts
import tempfile
import threading
import speech_recognition as sr
import sounddevice as sd
from scipy.io.wavfile import write
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId

# --- COMPONENT IMPORTS ---
from face_monitor import render_face_monitor
from llm_scoring import score_all_responses, generate_analysis_responses

# --- INITIAL CONFIGURATION ---
st.set_page_config(page_title="AI Viva System", layout="wide", initial_sidebar_state="collapsed")

# --- HELPER FUNCTIONS ---
def speak(text):
    """Generates and plays audio. THIS IS A BLOCKING CALL and must be threaded."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            filename = tmp_file.name
        # The async call must be run in a new event loop for threads
        asyncio.run(edge_tts.Communicate(text, "en-IN-PrabhatNeural").save(filename))
        subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", filename],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(filename): os.remove(filename)
    except Exception as e:
        print(f"TTS Error: {e}")

def play_beep():
    """Plays a beep sound. THIS IS A BLOCKING CALL and must be threaded."""
    beep_path = os.path.abspath("beep-05.wav")
    if not os.path.exists(beep_path): return
    try:
        subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", beep_path],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Beep Error: {e}")

def threaded_task(target_func, *args):
    """General-purpose wrapper to run any function in a background thread."""
    thread = threading.Thread(target=target_func, args=args)
    thread.start()

def threaded_record_audio(filename, duration, fs=44100):
    """Runs audio recording in the background and signals completion."""
    try:
        audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        write(filename, fs, audio_data)
    except Exception as e:
        print(f"Audio recording error: {e}")
    finally:
        st.session_state['recording_complete'] = True

def transcribe_audio(filename):
    """Transcribes an audio file to text."""
    if not filename or not os.path.exists(filename): return "No audio file."
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
        try: return recognizer.recognize_google(audio)
        except sr.UnknownValueError: return "Could not understand audio."
        except sr.RequestError as e: return f"API error: {e}"

# --- MAIN APP LOGIC ---
st.markdown("""<style>[data-testid="stSidebar"], [data-testid="collapsedControl"] {display: none !important;}</style>""", unsafe_allow_html=True)

# --- State Initialization ---
if 'current_q' not in st.session_state: st.session_state.current_q = 0
if 'responses' not in st.session_state: st.session_state.responses = []
if 'timer_start_time' not in st.session_state: st.session_state.timer_start_time = 0
if 'candidate_id' not in st.session_state: st.session_state.candidate_id = ""
for key in ['interview_started', 'id_confirmed', 'terminate_clicked', 'is_recording', 'recording_complete', 'start_record']:
    if key not in st.session_state: st.session_state[key] = False

# --- Database & Query Params (PRESERVED) ---
load_dotenv("../backend/.env")
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.get_database("test")
tests_collection = db.get_collection("tests")
query_params = st.query_params
test_id = query_params.get("testId", "")
student_id = query_params.get("studentId", "")
test_id = str(test_id).strip()
student_id = str(student_id).strip()
if not test_id or not student_id:
    st.error("❌ Test ID and/or Student ID are missing from the URL."); st.stop()
test_data = tests_collection.find_one({"sharedLinkId": test_id})
if not test_data:
    st.error("❌ Invalid Test ID or test not found."); st.stop()
question_ids = test_data.get("questions", [])
questions_collection = db.get_collection("questions")
question_object_ids = [ObjectId(qid) for qid in question_ids]
fetched_questions = list(questions_collection.find({"_id": {"$in": question_object_ids}}))
questions = [q.get("questionText", "Error") for q in fetched_questions]
if not questions:
    st.error("❌ Could not resolve any question texts."); st.stop()

RECORDING_DURATION = 15

st.title("AI-powered Viva-Voce System")

if not st.session_state.id_confirmed:
    photo_url = None
    try:
        res = requests.get(f"http://localhost:5000/api/student/student/{student_id}")
        if res.status_code == 200: photo_url = res.json().get("photo")
    except Exception: pass
    if photo_url: st.image(photo_url, caption="Candidate Photo", width=180)
    
    candidate_id_input = st.text_input("Enter your Candidate ID to begin:", value=student_id)

    # if st.button("Confirm ID"):
    #     if candidate_id_input == student_id:
    #         st.session_state.candidate_id = candidate_id_input
    #         st.session_state.id_confirmed = True
    #         st.rerun()
    #     else: st.error("❌ Entered ID does not match.")
     # --- This is the corrected code ---
    if st.button("Confirm ID"):
        if candidate_id_input == student_id:
        # SET THE ID FOR THE NEW SESSION
            st.session_state.candidate_id = candidate_id_input
            st.session_state.id_confirmed = True
         
        # RESET THE STATE for a clean start
            st.session_state.responses = []
            st.session_state.current_q = 0
            st.session_state.terminate_clicked = False
            st.session_state.interview_started = False
        
            st.rerun()
        else: st.error("❌ Entered ID does not match.") 

    st.stop()

if not st.session_state.interview_started:
    st.success(f"ID '{st.session_state.candidate_id}' registered. You may start the interview.")
    st.session_state.camera_index = st.number_input("Select Camera Index (0 for built-in, 1+ for external)", 0, 5, 0)
    if st.button("Start Interview"):
        st.session_state.interview_started = True
        # FIX: Run the blocking welcome message in a thread to prevent stalling
        threaded_task(speak, "Welcome to the interview. Please listen carefully and answer within the time limit.")
        st.rerun()
    st.stop()

candidate_dir = os.path.join("interviews", st.session_state.candidate_id)
os.makedirs(candidate_dir, exist_ok=True)
q_idx = st.session_state.current_q

if q_idx < len(questions) and not st.session_state.terminate_clicked:
    question = questions[q_idx]
    st.subheader(f"Question {q_idx + 1}: {question}")
    timer_placeholder = st.empty()

    # If we are not currently in a recording cycle
    if not st.session_state.is_recording:
        if st.button("▶️ Play Question & Start Answering", key=f"play_q_{q_idx}"):
            # FIX: Run all blocking audio prompts in a background thread
            def question_audio_sequence(text):
                play_beep()
                speak(text)
                play_beep()
            threaded_task(question_audio_sequence, question)
            
            # Immediately set the app to recording mode and start the recording thread
            st.session_state.is_recording = True
            st.session_state.recording_complete = False
            st.session_state.timer_start_time = time.time()
            audio_filename = os.path.join(candidate_dir, f"q{q_idx + 1}_answer.wav")
            threaded_task(threaded_record_audio, audio_filename, RECORDING_DURATION)
            st.rerun()

    # If we are in a recording cycle, just show the timer
    if st.session_state.is_recording:
        elapsed_time = time.time() - st.session_state.timer_start_time
        remaining_time = max(0, RECORDING_DURATION - elapsed_time)
        timer_placeholder.markdown(f"⏳ **Time left: {int(remaining_time)} seconds**")

        # Check if the recording is finished
        if remaining_time == 0 or st.session_state.get('recording_complete', False):
            threaded_task(play_beep)
            timer_placeholder.info("Time's up! Processing your answer...")
            
            # Wait a moment for the background thread to finish writing the file
            time.sleep(1.5) 
            
            audio_filename = os.path.join(candidate_dir, f"q{q_idx + 1}_answer.wav")
            transcript = transcribe_audio(audio_filename)
            st.session_state.responses.append({
                "question_number": q_idx + 1, "question": question,
                "audio_file": audio_filename, "transcript": transcript.strip()
            })
            
            # Reset for the next question
            st.session_state.is_recording = False
            st.session_state.recording_complete = False
            st.session_state.current_q += 1
            st.rerun()

# --- Interview Termination and Submission ---
if not st.session_state.terminate_clicked:
    if st.session_state.current_q >= len(questions):
        st.warning("🎉 You've answered all questions. Click below to view your summary.")
        if st.button("🟢 View My Responses", key="terminate_btn_final"):
            st.session_state.terminate_clicked = True
            st.rerun()
    elif len(st.session_state.responses) > 0:
        if st.button("🔴 Quit Interview", key="terminate_btn"):
            st.session_state.terminate_clicked = True
            st.rerun()

if st.session_state.terminate_clicked:
    # FIX: Stop the camera by releasing the capture object
    if 'video_capture' in st.session_state:
        st.session_state.video_capture.release()
        del st.session_state.video_capture
        
    st.success("✅ Interview Summary")
    for res in st.session_state.responses:
        st.markdown(f"**Q{res['question_number']}:** {res['question']}")
        st.audio(res['audio_file'])
        st.markdown(f"**A:** {res['transcript']}")

    # if st.button("Submit and Show Results"):
    #     if 'video_capture' in st.session_state:
    #         st.session_state.video_capture.release()
    #         del st.session_state.video_capture
            
    #     with st.spinner("Analyzing your responses..."):
    #         with open(os.path.join(candidate_dir, "responses.json"), "w") as f:
    #             json.dump(st.session_state.responses, f, indent=4)
        
    #     st.session_state.scoring_results = score_all_responses(st.session_state.candidate_id)
    #     generate_analysis_responses(st.session_state.candidate_id)
    #     st.switch_page("thank_you")

      # streamlit_app.py

    if st.button("Submit and Show Results"):
        # Stop the camera by releasing the capture object
        if 'video_capture' in st.session_state:
            st.session_state.video_capture.release()
            del st.session_state.video_capture

        with st.spinner("Analyzing your responses..."):
            with open(os.path.join(candidate_dir, "responses.json"), "w") as f:
                json.dump(st.session_state.responses, f, indent=4)
            
            # FIX: Call the scoring and analysis functions
            # This ensures the result files are created before switching pages
            score_all_responses(st.session_state.candidate_id)
            generate_analysis_responses(st.session_state.candidate_id)
        
        # FIX: The correct way to switch pages in recent Streamlit versions
        st.switch_page("pages/thank_you.py")

# --- RENDER FACE MONITOR AND REFRESH LOOP ---
if st.session_state.get('interview_started', False) and not st.session_state.get('terminate_clicked', False):
    render_face_monitor()
    time.sleep(0.1)
    st.rerun()


