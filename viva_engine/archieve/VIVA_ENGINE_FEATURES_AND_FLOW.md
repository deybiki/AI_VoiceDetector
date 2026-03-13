# Viva Engine: Features, Execution Flow, and Integrations

This document describes the `viva_engine` module in detail:
- each feature and its behavior
- exact execution order at runtime
- connection points with frontend, backend, and database
- files generated during an interview
- scoring and proctoring internals
- known integration risks

## 1. Scope and Core Files

Primary files:
- `viva_engine/streamlit_app.py` (main viva runtime)
- `viva_engine/face_monitor.py` (camera and face monitoring)
- `viva_engine/llm_scoring.py` (AI scoring pipeline)
- `viva_engine/pages/thank_you.py` (result summary, backend submission, feedback)
- `viva_engine/requirements.txt` (Python dependencies)
- `viva_engine/Dockerfile` (container build/run setup)

Related integration files:
- `frontend/src/landing_page/stud_dash/Footer.jsx` (launches Streamlit and fetches student results)
- `backend/server.js` (mounts APIs)
- `backend/routes/testResults.js` (stores viva results)
- `backend/platformFeedback.js` (stores platform feedback)
- `backend/routes/student.js`, `backend/controllers/studentController.js` (join/start/upcoming/student lookup)
- `backend/routes/evaluator.js`, `backend/controllers/evaluatorController.js` (read/evaluate viva results)
- `backend/models/Test.js`, `backend/models/VivaResult.js`, `backend/models/Student.js`

## 2. Functional Overview

`viva_engine` is a Streamlit-based interview runtime that:
1. receives `testId` and `studentId` from URL
2. validates test and candidate context using MongoDB
3. enforces exam entry gates (ID confirm, rules, camera check)
4. runs timed voice-based Q/A loop
5. performs camera snapshot monitoring throughout the interview
6. transcribes answers to text
7. scores each answer using multiple LLM providers
8. stores local artifacts (`responses.json`, `scored_responses.json`, snapshots, logs)
9. submits final result to backend API
10. collects platform feedback and posts it to backend API

## 3. Runtime Execution Order (Exact Flow)

This is the runtime sequence in practical order.

### Phase A: App boot and state initialization
1. Streamlit app starts, page config and custom CSS are loaded.
2. Session state keys are initialized if absent:
   - `current_q`, `responses`, `timer_start_time`, `candidate_id`
   - `interview_started`, `id_confirmed`, `terminate_clicked`
   - `is_recording`, `recording_complete`, `force_stop`
   - later gates: `rules_accepted`, `camera_checked`

### Phase B: DB connectivity and test context resolution
1. `load_dotenv("../backend/.env")` loads backend DB URI.
2. Mongo client is created via cached function (`@st.cache_resource`).
3. App reads URL query params:
   - `testId` from `st.query_params`
   - `studentId` from `st.query_params`
4. If either is missing, app stops with error.
5. Test is fetched by `sharedLinkId == testId`.
6. Questions are fetched from `questions` collection.
7. Reference answers are fetched from `testanswers` collection by `testId = ObjectId(test._id)`.
8. If candidate changes, attempt state resets and a new attempt directory is created:
   - `interviews/<candidateId>_<YYYYMMDD_HHMMSS>/`

### Phase C: Audio pre-generation
1. App pre-synthesizes all question audios (`q1.mp3`, `q2.mp3`, ...).
2. Uses `edge-tts` voice `en-IN-NeerjaNeural`.
3. Retries each question up to 3 times with delay.
4. This happens before interview begins to reduce runtime TTS lag.

### Phase D: Candidate gating screens
1. Candidate ID confirmation screen:
   - user must enter the same `studentId` as query param.
2. Rules acceptance screen:
   - checkbox is mandatory before proceed.
3. Camera check screen:
   - initializes camera (`ensure_camera_started`)
   - verifies exactly one face (`camera_check_ui`)
   - only then allows moving forward.

### Phase E: Start Test transition
1. Start button is displayed after camera check.
2. Welcome audio (`welcome.mp3`) is generated (if absent) and played.
3. Camera is ensured active.
4. `interview_started` set true and app reruns into interview mode.

### Phase F: Per-question execution loop
For each question index `q_idx`:
1. Render question text.
2. Run `render_face_monitor(...)` to keep silent proctoring active.
3. If recording not started:
   - countdown (`Question will play start in 3..2..1`)
   - play pre-generated question audio (`q{n}.mp3`)
   - small delay
   - start background audio recording thread for 30 seconds
4. While recording:
   - show countdown timer box
   - allow `Done & Next` to force stop early
5. Recording ends when:
   - timer reaches 0, or
   - recording thread signals complete, or
   - user presses force stop
6. End beep is played.
7. Audio file is transcribed via SpeechRecognition.
8. Response object is appended to session `responses`.
9. `score_single_response(...)` is called immediately (per question).
10. Move to next question and rerun.

### Phase G: Interview submission
1. After last question, show `Submit and Show Results`.
2. On click:
   - stop camera capture
   - write `responses.json` in attempt directory
   - if `scored_responses.json` missing, fallback to `score_all_responses(...)`
   - switch page to `pages/thank_you.py`

### Phase H: Result/feedback flow (`thank_you.py`)
1. Loads attempt artifacts (`responses.json`, `scored_responses.json`).
2. Computes:
   - per-question averages
   - obtained marks and percentage
   - grade/message
3. Posts full viva result to backend `POST /api/submit-viva`.
4. Displays:
   - summary score view
   - detailed per-question LLM score/feedback view
5. Collects platform feedback and posts to `POST /api/feedback/platform`.
6. Final thank-you view clears session.

## 4. Feature-by-Feature Detail

### 4.1 Test context loader
Purpose:
- bind Streamlit session to a specific backend test and candidate.

Key inputs:
- URL `testId` (actually backend `Test.sharedLinkId`)
- URL `studentId` (scholar ID string)

Key outputs:
- `questions` list
- `reference_answers` list in session
- `attempt_dir` path for artifacts

### 4.2 Candidate verification gate
Purpose:
- prevent accidental/incorrect candidate entry.

Behavior:
- explicit ID confirmation required before proceeding.

### 4.3 Rules acknowledgement gate
Purpose:
- require user consent to rules before exam start.

Behavior:
- proceed button disabled until checkbox selected.

### 4.4 Camera readiness gate
Purpose:
- verify webcam + single-face visibility before test start.

`face_monitor.py` features used:
- `ensure_camera_started`: tries camera indexes 0..2
- `camera_check_ui`: frame preview + face count status + proceed lock

### 4.5 Silent proctoring monitor
Purpose:
- passive exam surveillance with minimal UI distraction.

Behavior:
- snapshots saved at randomized intervals (8-15s)
- each snapshot gets a status:
  - `ok` (single face)
  - `no_face`
  - `multi_face`
- logs appended into `face_log.json`
- candidate sees only "Camera Active" badge

### 4.6 TTS question playback
Purpose:
- play each question clearly and consistently.

Implementation:
- pre-synthesis using `edge_tts`
- playback from browser via base64-injected `<audio>` component
- duration estimated with `mutagen.mp3` and waited before next action

### 4.7 Audio recording engine
Purpose:
- capture candidate answer for each question.

Implementation:
- background thread (`threaded_record_audio`)
- `sounddevice` recording + `scipy.io.wavfile.write`
- 30-second limit (configurable constant `RECORDING_DURATION`)
- file visibility/size checks to avoid race conditions

### 4.8 Transcription
Purpose:
- convert WAV answer to text for scoring.

Implementation:
- waits for audio file validity
- uses `speech_recognition` with Google recognizer
- returns fallback messages on unknown speech/API issues

### 4.9 Multi-LLM scoring
Purpose:
- evaluate answer quality using ensemble scoring.

Models/providers used in `llm_scoring.py`:
- Kimi (through Groq/OpenRouter-compatible flow)
- Gemini (native Google Generative AI SDK)
- Llama 3.3 70B (Groq)

Scoring rubric per model:
- Accuracy (0-2)
- Coverage (0-2)
- Reasoning (0-2)
- Clarity (0-2)
- Terminology (0-2)
- total out of 10

Per-answer output:
- each model score + feedback
- average score across valid model outputs

Resilience:
- primary and alternate keys for providers
- parser attempts to recover JSON from imperfect model output

### 4.10 Results and analytics page
Purpose:
- summarize AI performance and submit final record.

Displayed:
- total marks and percentage
- grade band with message
- detailed model scores and feedback per question

### 4.11 Platform feedback capture
Purpose:
- collect user satisfaction after viva completion.

Data posted:
- `candidateId`
- `rating` (1-5 stars mapped from symbol count)
- `recommendation`
- `timestamp`

## 5. Data Artifacts Written by Viva Engine

Per-attempt directory structure:
- `welcome.mp3`
- `q1.mp3`, `q2.mp3`, ...
- `q1_answer.wav`, `q2_answer.wav`, ...
- `responses.json`
- `scored_responses.json`
- `snapshot_<timestamp>.jpg` (multiple)
- `face_log.json`

### `responses.json` shape
Array of objects:
- `question_number`
- `question`
- `audio_file`
- `transcript`

### `scored_responses.json` shape
Array of objects:
- `question`, `answer`
- `kimi_score`, `gemini_score`, `llama_3.3_score`
- `average_score`
- `kimi_feedback`, `gemini_feedback`, `llama_feedback`

### `face_log.json` shape
Array of objects:
- `timestamp`
- `status` (`ok`, `no_face`, `multi_face`, `unknown`)
- `snapshot` (filename)

## 6. Frontend Integration (Detailed)

Main integration point:
- `frontend/src/landing_page/stud_dash/Footer.jsx`

### 6.1 Start test launch flow
1. Fetch student Mongo `_id` from scholar ID:
   - `GET /api/student/:scholarId/fetchId`
2. Load upcoming tests:
   - `GET /api/student/upcoming`
3. Check previous attempts:
   - `GET /api/testAttempt/:studentMongoId/:testId/fetch_test_attempt`
4. On start:
   - `POST /api/testAttempt/:studentMongoId/:testId/submit` (marks attempted)
   - `POST /api/student/join/:testId`
   - `POST /api/student/start/:testId`
5. Open Streamlit:
   - `http://localhost:8501/?testId=<sharedLinkId>&studentId=<scholarId>`

### 6.2 Student result display flow
1. Fetch candidate viva results:
   - `GET /api/evaluator/:candidateId/studresults`
2. For each result `testId` (which is actually `sharedLinkId`), fetch title:
   - `GET /api/test/:sharedLinkId/title`

## 7. Backend Integration (Detailed)

### 7.1 APIs consumed by `viva_engine`

From `streamlit_app.py`:
- `GET /api/student/student/:scholarId`
  - expected usage: candidate photo display

From `thank_you.py`:
- `POST /api/submit-viva`
  - stores viva AI output into `vivaresults`
- `POST /api/feedback/platform`
  - stores platform feedback

### 7.2 Result storage endpoint
Route:
- `backend/routes/testResults.js` -> `POST /api/submit-viva`

Payload fields:
- `testId` (string, set to sharedLinkId in current flow)
- `candidateId`
- `questionAnswerPairs`
- `totalScore`
- `detailedBreakdown`
- `vivaDate`
- `questionAverages`
- `cosineSimilarities`

Model:
- `backend/models/VivaResult.js`
  - `status` defaults to `"Not Evaluated"`
  - later changed to `"Evaluated"` by evaluator workflow

### 7.3 Evaluator pipeline connection
Evaluator APIs use test Mongo `_id`, then internally map to `sharedLinkId`:
- fetch pending results for a test
- fetch all results for a test
- submit evaluator feedback (`/api/evaluator/resultsubmit`)
- fetch evaluator response by candidate
- fetch all candidate results for student dashboard

This mapping is key because `VivaResult.testId` stores sharedLinkId string.

### 7.4 Platform feedback storage
Route:
- `backend/platformFeedback.js`
- mounted at `/api/feedback`
- viva engine hits `POST /api/feedback/platform`

Stored fields:
- `candidateId`
- `rating`
- `recommendation`
- `submittedAt`

## 8. Database Interaction Map

Collections touched by viva flow:

Read path:
- `tests`:
  - find by `sharedLinkId` from query param
- `questions`:
  - fetch question text using IDs from test doc
- `testanswers`:
  - fetch reference answers by test ObjectId
- `students`:
  - fetch candidate photo by `scholarId` (via backend API)

Write path:
- `vivaresults`:
  - final AI-scored result submission
- `platformfeedbacks` (model-defined collection):
  - post-exam feedback

Related but outside Streamlit runtime:
- `testattempts`:
  - updated from frontend/backend before launching Streamlit

## 9. Configuration and Deployment Notes

### 9.1 Dependencies (`requirements.txt`)
Includes:
- streamlit, pymongo, requests
- speech and audio stack (`SpeechRecognition`, `sounddevice`, `scipy`)
- CV stack (`opencv-python`)
- LLM SDKs (`Groq`, `google-generativeai`, `openai`, `cerebras-cloud-sdk`)
- utility libs (`mutagen`, `python-dotenv`, `retry`)

### 9.2 Docker behavior
Current Dockerfile:
- exposes port `8501`
- starts Streamlit with `interview_app.py`

Important:
- actual main file in repo is `streamlit_app.py`
- container command should match actual filename

### 9.3 Docker compose integration
`docker-compose.yml` defines:
- backend on `5000`
- frontend on `3000`
- viva_engine on `8501`
- `viva_engine/interviews` mounted to `/app/interviews` for persistence

## 10. Known Risks and Mismatches

1. Docker entry mismatch:
- Docker CMD points to `interview_app.py`, but repo contains `streamlit_app.py`.

2. Student photo field mismatch:
- backend student schema uses `image`, but route returns `photo`.
- Streamlit expects `photo`.

3. Time field mismatch in student join logic:
- controller checks `startTime/endTime`
- schema defines `start_time/end_time`

4. Attempt status timing:
- frontend marks attempt submitted before viva actually starts.

5. Secrets handling:
- environment files currently contain sensitive keys and credentials.

## 11. End-to-End Data Contract Summary

ID semantics in this system:
- `Test._id`:
  - used in many backend and frontend APIs.
- `Test.sharedLinkId`:
  - used in Streamlit URL as `testId`
  - stored in `VivaResult.testId`
  - used by student dashboard title resolver endpoint.
- `studentId` in Streamlit URL:
  - scholar ID string.

Key payload from viva to backend (`/api/submit-viva`):
- identifies candidate and test context
- includes raw Q/A, per-question detailed model outputs, and aggregate score
- becomes primary input for evaluator workflow and dashboard displays

## 12. Quick Reference: Feature Checklist

- URL param validation (`testId`, `studentId`)
- MongoDB test/question/answer loading
- per-candidate attempt folder creation
- question TTS pre-synthesis
- candidate ID confirmation
- rules acceptance gate
- camera readiness gate
- random-interval face snapshot monitoring
- 30s timed answer recording per question
- transcription
- 3-model scoring with fallback behavior
- per-answer score persistence
- full interview response persistence
- final result submission to backend
- result summary and detailed feedback UI
- platform feedback collection and submission
- session cleanup on completion

---

If you want, a second companion document can be added with:
- sequence diagrams (frontend -> backend -> viva_engine -> DB)
- JSON schema examples for every API payload/response
- troubleshooting playbook by failure point.
