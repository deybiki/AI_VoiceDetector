import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import axios from "axios";
import "./VivaExam.css";

const VIVA_API = process.env.REACT_APP_VIVA_ENGINE_URI || "http://localhost:8501";
const TIMEOUT_BEEP_URL = `${process.env.PUBLIC_URL || ""}/beep-05.wav`;
const PRE_SUBMIT_PHASES = new Set(["loading", "interview", "submit"]);
const POST_SUBMIT_PHASES = new Set(["summary", "detailed", "feedback", "done"]);

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function encodeWavFromAudioBuffer(audioBuffer) {
  const channels = audioBuffer.numberOfChannels;
  const sampleRate = audioBuffer.sampleRate;
  const samples = audioBuffer.length;
  const bytesPerSample = 2;
  const blockAlign = channels * bytesPerSample;
  const buffer = new ArrayBuffer(44 + samples * blockAlign);
  const view = new DataView(buffer);

  function writeString(offset, str) {
    for (let i = 0; i < str.length; i += 1) view.setUint8(offset + i, str.charCodeAt(i));
  }

  writeString(0, "RIFF");
  view.setUint32(4, 36 + samples * blockAlign, true);
  writeString(8, "WAVE");
  writeString(12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, channels, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * blockAlign, true);
  view.setUint16(32, blockAlign, true);
  view.setUint16(34, 16, true);
  writeString(36, "data");
  view.setUint32(40, samples * blockAlign, true);

  const channelData = [];
  for (let c = 0; c < channels; c += 1) channelData.push(audioBuffer.getChannelData(c));
  let offset = 44;
  for (let i = 0; i < samples; i += 1) {
    for (let c = 0; c < channels; c += 1) {
      const sample = Math.max(-1, Math.min(1, channelData[c][i]));
      view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7fff, true);
      offset += 2;
    }
  }
  return new Blob([view], { type: "audio/wav" });
}

async function convertBlobToWav(blob) {
  const arrayBuffer = await blob.arrayBuffer();
  const ctx = new (window.AudioContext || window.webkitAudioContext)();
  const decoded = await ctx.decodeAudioData(arrayBuffer.slice(0));
  const wav = encodeWavFromAudioBuffer(decoded);
  await ctx.close();
  return wav;
}

function blobToBase64(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      const result = String(reader.result || "");
      const base64 = result.includes(",") ? result.split(",")[1] : result;
      resolve(base64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

function VivaExam() {
  const [searchParams] = useSearchParams();
  const testId = searchParams.get("testId") || "";
  const studentId = searchParams.get("studentId") || "";

  const [sessionId, setSessionId] = useState("");
  const [phase, setPhase] = useState("loading");
  const [candidateInput, setCandidateInput] = useState(studentId);
  const [rulesChecked, setRulesChecked] = useState(false);
  const [cameraReady, setCameraReady] = useState(false);
  const [cameraStatus, setCameraStatus] = useState("No Face Detected");
  const [loadingMessage, setLoadingMessage] = useState("Loading exam...");
  const [questionData, setQuestionData] = useState(null);
  const [countdown, setCountdown] = useState(0);
  const [recordingLeft, setRecordingLeft] = useState(30);
  const [isRecording, setIsRecording] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [results, setResults] = useState(null);
  const [expandedDetailIndex, setExpandedDetailIndex] = useState(0);
  const [feedbackRating, setFeedbackRating] = useState(5);
  const [feedbackText, setFeedbackText] = useState("");
  const [error, setError] = useState("");
  const [cameraLive, setCameraLive] = useState(false);
  const [examProtectionActive, setExamProtectionActive] = useState(false);
  const [warningModal, setWarningModal] = useState({ show: false, title: "", message: "" });

  const videoRef = useRef(null);
  const cameraStreamRef = useRef(null);
  const recorderStreamRef = useRef(null);
  const recorderRef = useRef(null);
  const chunksRef = useRef([]);
  const recordTimerRef = useRef(null);
  const randomSnapshotRef = useRef(null);
  const incidentThrottleRef = useRef({});
  const timeoutBeepRef = useRef(null);
  const startFlowLockRef = useRef(false);

  const api = useMemo(() => axios.create({ baseURL: VIVA_API }), []);
  const attemptStorageKey = useMemo(() => `viva_attempt_${testId}_${studentId}`, [testId, studentId]);

  const captureFrameBlob = async () => {
    const video = videoRef.current;
    if (!video || !video.videoWidth || !video.videoHeight) return null;
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    return new Promise((resolve) => canvas.toBlob(resolve, "image/jpeg", 0.85));
  };

  const sendSnapshot = useCallback(async (mode = "monitor") => {
    if (!sessionId) return;
    const frame = await captureFrameBlob();
    if (!frame) return;
    const imageBase64 = await blobToBase64(frame);
    const res = await api.post(`/api/viva/session/${sessionId}/proctor-snapshot`, {
      image_base64: imageBase64,
      mode,
    });
    if (mode === "check") {
      const s = res.data.status;
      if (s === "ok") setCameraStatus("Face detected - You are ready");
      if (s === "no_face") setCameraStatus("No Face Detected");
      if (s === "multi_face") setCameraStatus("Multiple faces detected");
      setCameraReady(Boolean(res.data.ready));
      return;
    }
    if (mode === "monitor") {
      if (res.data.status === "no_face") setCameraStatus("Face is not detected");
      else setCameraStatus("");
    }
  }, [api, sessionId]);

  const stopCamera = () => {
    if (cameraStreamRef.current) {
      cameraStreamRef.current.getTracks().forEach((t) => t.stop());
      cameraStreamRef.current = null;
    }
    setCameraLive(false);
  };

  const stopRecorderStream = () => {
    if (recorderStreamRef.current) {
      recorderStreamRef.current.getTracks().forEach((t) => t.stop());
      recorderStreamRef.current = null;
    }
  };

  const attachStreamToVideo = useCallback(async (stream) => {
    const video = videoRef.current;
    if (!video || !stream) return false;
    if (video.srcObject !== stream) video.srcObject = stream;
    video.muted = true;
    video.autoplay = true;
    video.playsInline = true;
    try {
      await video.play();
      setCameraLive(true);
      return true;
    } catch (_) {
      setCameraLive(false);
      return false;
    }
  }, []);

  const startCamera = useCallback(async () => {
    if (!cameraStreamRef.current) {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: "user",
        },
        audio: false,
      });
      cameraStreamRef.current = stream;
    }
    await attachStreamToVideo(cameraStreamRef.current);
  }, [attachStreamToVideo]);

  const playAudio = async (relativeUrl) => {
    const audio = new Audio(`${VIVA_API}${relativeUrl}`);
    await audio.play();
    await new Promise((resolve) => {
      audio.onended = resolve;
      audio.onerror = resolve;
    });
  };

  const playTimeoutBeep = useCallback(() => {
    try {
      if (timeoutBeepRef.current) {
        timeoutBeepRef.current.currentTime = 0;
        timeoutBeepRef.current.play().catch(() => {});
        return;
      }
    } catch (_) {
      // fallback below
    }

    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sine";
      osc.frequency.value = 880;
      gain.gain.setValueAtTime(0.0001, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.18, ctx.currentTime + 0.01);
      gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.22);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.24);
      osc.onended = () => {
        ctx.close().catch(() => {});
      };
    } catch (_) {
      // no-op: keep exam flow unaffected
    }
  }, []);

  const runInterviewQuestion = async (q) => {
    setQuestionData(q);
    setPhase("interview");
    setCountdown(3);
    for (let i = 3; i > 0; i -= 1) {
      setCountdown(i);
      await wait(1000);
    }
    setCountdown(0);
    await playAudio(q.audio_url);
    await wait(2000);
    await startRecording(q.recording_duration || 30);
  };

  const submitRecordedAnswer = async () => {
    setIsSubmitting(true);
    setIsRecording(false);
    if (recordTimerRef.current) clearInterval(recordTimerRef.current);
    stopRecorderStream();

    const blob = new Blob(chunksRef.current, { type: "audio/webm" });
    const wav = await convertBlobToWav(blob);
    const audioBase64 = await blobToBase64(wav);
    const res = await api.post(`/api/viva/session/${sessionId}/answer`, { audio_base64: audioBase64 });
    const nextQ = res.data.question;
    setIsSubmitting(false);
    if (nextQ.done) {
      setPhase("submit");
    } else {
      await runInterviewQuestion(nextQ);
    }
  };

  const stopRecording = async () => {
    if (!recorderRef.current || recorderRef.current.state !== "recording") return;
    recorderRef.current.stop();
  };

  const startRecording = async (durationSec) => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
    recorderStreamRef.current = stream;
    chunksRef.current = [];
    const recorder = new MediaRecorder(stream);
    recorderRef.current = recorder;
    recorder.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) chunksRef.current.push(event.data);
    };
    recorder.onstop = submitRecordedAnswer;
    recorder.start(250);

    setRecordingLeft(durationSec);
    setIsRecording(true);
    recordTimerRef.current = setInterval(() => {
      setRecordingLeft((prev) => {
        if (prev <= 1) {
          clearInterval(recordTimerRef.current);
          playTimeoutBeep();
          stopRecording();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const scheduleRandomMonitor = useCallback(() => {
    if (!sessionId) return;
    const delay = (Math.floor(Math.random() * 8) + 8) * 1000;
    randomSnapshotRef.current = setTimeout(async () => {
      if (phase === "interview" || phase === "submit") {
        try {
          await sendSnapshot("monitor");
        } catch (e) {
          // no-op
        }
      }
      scheduleRandomMonitor();
    }, delay);
  }, [phase, sendSnapshot, sessionId]);

  const showWarning = useCallback((title, message) => {
    setWarningModal({ show: true, title, message });
  }, []);

  const requestFullscreen = useCallback(async () => {
    const element = document.documentElement;
    try {
      if (document.fullscreenElement) return true;
      if (element.requestFullscreen) {
        await element.requestFullscreen();
        return true;
      }
      if (element.webkitRequestFullscreen) {
        element.webkitRequestFullscreen();
        return true;
      }
      return false;
    } catch (_) {
      return false;
    }
  }, []);

  const logIncident = useCallback(
    async (incidentType, details = {}, throttleMs = 1000) => {
      if (!sessionId) return;
      const now = Date.now();
      const last = incidentThrottleRef.current[incidentType] || 0;
      if (now - last < throttleMs) return;
      incidentThrottleRef.current[incidentType] = now;
      try {
        await api.post(`/api/viva/session/${sessionId}/incident`, {
          incident_type: incidentType,
          details,
          phase,
          timestamp: new Date().toISOString(),
        });
      } catch (_) {
        // keep exam flow unaffected on logging failure
      }
    },
    [api, phase, sessionId]
  );

  const showSideCamera = phase === "camera" || phase === "start" || phase === "interview" || phase === "submit";

  const saveAttemptState = useCallback(
    (extra = {}) => {
      if (!attemptStorageKey) return;
      const payload = {
        sessionId,
        phase,
        questionData,
        results,
        examProtectionActive,
        updatedAt: Date.now(),
        ...extra,
      };
      try {
        sessionStorage.setItem(attemptStorageKey, JSON.stringify(payload));
      } catch (_) {
        // no-op
      }
    },
    [attemptStorageKey, examProtectionActive, phase, questionData, results, sessionId]
  );

  const markRefreshTermination = useCallback(() => {
    saveAttemptState({ refreshTerminated: true, refreshTerminatedAt: Date.now() });
  }, [saveAttemptState]);

  const sendIncidentBeacon = useCallback(
    (incidentType, details = {}) => {
      if (!sessionId || !navigator.sendBeacon) return;
      try {
        const payload = {
          incident_type: incidentType,
          details,
          phase,
          timestamp: new Date().toISOString(),
        };
        const blob = new Blob([JSON.stringify(payload)], { type: "application/json" });
        navigator.sendBeacon(`${VIVA_API}/api/viva/session/${sessionId}/incident`, blob);
      } catch (_) {
        // no-op
      }
    },
    [phase, sessionId]
  );

  useEffect(() => {
    let mounted = true;
    timeoutBeepRef.current = new Audio(TIMEOUT_BEEP_URL);
    timeoutBeepRef.current.preload = "auto";

    const readSavedAttempt = () => {
      try {
        const raw = sessionStorage.getItem(attemptStorageKey);
        return raw ? JSON.parse(raw) : null;
      } catch (_) {
        return null;
      }
    };

    const init = async () => {
      if (!testId || !studentId) {
        setError("Missing testId or studentId");
        setPhase("error");
        return;
      }
      try {
        setLoadingMessage("Initializing test session...");
        const saved = readSavedAttempt();
        const res = await api.post("/api/viva/session/init", { testId, studentId });
        if (!mounted) return;
        const sid = res.data.session_id;
        setSessionId(sid);

        const stateRes = await api.get(`/api/viva/session/${sid}/state`);
        if (!mounted) return;
        const state = stateRes.data || {};

        if (state.terminated) {
          if (saved?.sessionId === sid && saved?.results && POST_SUBMIT_PHASES.has(saved.phase)) {
            setResults(saved.results);
            setPhase(saved.phase);
          } else {
            setError("Exam ended because the session was interrupted before submission.");
            setPhase("error");
          }
          return;
        }

        if (state.interview_started) {
          startFlowLockRef.current = true;
          setError("This exam session was already started. Refresh is not allowed before final submission.");
          setPhase("error");
          return;
        }

        if (!state.id_confirmed) {
          setPhase("confirm");
          return;
        }
        if (!state.rules_accepted) {
          setPhase("rules");
          return;
        }
        if (!state.camera_checked) {
          setPhase("camera");
          return;
        }
        setPhase("start");
      } catch (e) {
        setError(e?.response?.data?.detail || "Could not initialize viva");
        setPhase("error");
      }
    };
    init();
    return () => {
      mounted = false;
      if (timeoutBeepRef.current) {
        timeoutBeepRef.current.pause();
        timeoutBeepRef.current = null;
      }
      stopCamera();
      stopRecorderStream();
      if (recordTimerRef.current) clearInterval(recordTimerRef.current);
      if (randomSnapshotRef.current) clearTimeout(randomSnapshotRef.current);
    };
  }, [api, attemptStorageKey, studentId, testId]);

  useEffect(() => {
    if (!sessionId) return;
    saveAttemptState();
  }, [examProtectionActive, phase, questionData, results, saveAttemptState, sessionId]);

  useEffect(() => {
    if (!sessionId) return undefined;
    if (!startFlowLockRef.current || !PRE_SUBMIT_PHASES.has(phase)) return undefined;

    const onBeforeUnload = (event) => {
      markRefreshTermination();
      sendIncidentBeacon("page_refresh_attempt", { reason: "beforeunload" });
      sendIncidentBeacon("page_unload", { reason: "beforeunload" });
      event.preventDefault();
      event.returnValue = "";
    };

    window.addEventListener("beforeunload", onBeforeUnload);
    return () => window.removeEventListener("beforeunload", onBeforeUnload);
  }, [markRefreshTermination, phase, sendIncidentBeacon, sessionId]);

  useEffect(() => {
    if (!sessionId) return;
    if (showSideCamera) {
      startCamera().catch(() => {
        setCameraStatus("Camera not accessible");
        setCameraLive(false);
      });
    }
  }, [showSideCamera, phase, sendSnapshot, sessionId, startCamera]);

  useEffect(() => {
    if (!showSideCamera) return undefined;
    const timer = setInterval(async () => {
      const stream = cameraStreamRef.current;
      const video = videoRef.current;
      if (!stream || !video) {
        setCameraLive(false);
        return;
      }
      const tracks = stream.getVideoTracks();
      const active = tracks.length > 0 && tracks.some((t) => t.readyState === "live");
      const hasFrame = Number(video.videoWidth) > 0 && Number(video.videoHeight) > 0;
      if (!active) {
        setCameraLive(false);
        return;
      }
      if (video.srcObject !== stream || !hasFrame || video.paused) {
        await attachStreamToVideo(stream);
        return;
      }
      setCameraLive(true);
    }, 800);
    return () => clearInterval(timer);
  }, [showSideCamera, attachStreamToVideo]);

  useEffect(() => {
    if (!examProtectionActive) return undefined;

    const onFullscreenChange = () => {
      if (!document.fullscreenElement) {
        logIncident("fullscreen_exit");
        showWarning("Fullscreen Exited", "Please return to fullscreen to continue the exam.");
      }
    };

    const onVisibilityChange = () => {
      if (document.hidden) {
        logIncident("tab_hidden");
        showWarning("Tab Switch Detected", "Please stay on the exam screen in fullscreen mode.");
      }
    };

    const onWindowBlur = () => {
      logIncident("window_blur");
      showWarning("Window Focus Lost", "Please return to the exam window.");
    };

    const onWindowFocus = () => {
      logIncident("focus_returned");
    };

    document.addEventListener("fullscreenchange", onFullscreenChange);
    document.addEventListener("visibilitychange", onVisibilityChange);
    window.addEventListener("blur", onWindowBlur);
    window.addEventListener("focus", onWindowFocus);

    return () => {
      document.removeEventListener("fullscreenchange", onFullscreenChange);
      document.removeEventListener("visibilitychange", onVisibilityChange);
      window.removeEventListener("blur", onWindowBlur);
      window.removeEventListener("focus", onWindowFocus);
    };
  }, [examProtectionActive, logIncident, showWarning]);

  useEffect(() => {
    if (!sessionId || phase !== "camera") return undefined;
    const timer = setInterval(() => {
      sendSnapshot("check").catch(() => setCameraStatus("Camera check failed"));
    }, 1300);
    return () => clearInterval(timer);
  }, [phase, sendSnapshot, sessionId]);

  useEffect(() => {
    if (!sessionId || (phase !== "interview" && phase !== "submit")) return;
    scheduleRandomMonitor();
    return () => {
      if (randomSnapshotRef.current) clearTimeout(randomSnapshotRef.current);
    };
  }, [phase, scheduleRandomMonitor, sessionId]);

  const handleConfirmId = async () => {
    const res = await api.post(`/api/viva/session/${sessionId}/confirm-id`, { candidateId: candidateInput });
    if (!res.data.ok) {
      setError("Entered ID does not match.");
      return;
    }
    setError("");
    setPhase("rules");
  };

  const handleAcceptRules = async () => {
    await api.post(`/api/viva/session/${sessionId}/accept-rules`);
    setPhase("camera");
  };

  const handleStartTest = async () => {
    startFlowLockRef.current = true;
    setExamProtectionActive(true);
    saveAttemptState({ phase: "loading" });
    const fsOk = await requestFullscreen();
    if (!fsOk) {
      logIncident("fullscreen_request_denied");
      showWarning("Fullscreen Required", "Please allow fullscreen mode to continue the exam.");
    }

    setLoadingMessage("Get ready for the exam...");
    setPhase("loading");
    const res = await api.post(`/api/viva/session/${sessionId}/start-test`);
    await playAudio(res.data.welcome_audio_url);
    await runInterviewQuestion(res.data.question);
  };

  const handleSubmitInterview = async () => {
    setIsSubmitting(true);
    setExamProtectionActive(false);
    startFlowLockRef.current = false;
    if (document.fullscreenElement && document.exitFullscreen) {
      try {
        await document.exitFullscreen();
      } catch (_) {
        // ignore
      }
    }
    const res = await api.post(`/api/viva/session/${sessionId}/submit`);
    setResults(res.data);
    setIsSubmitting(false);
    setPhase("summary");
    saveAttemptState({ results: res.data, phase: "summary" });
  };

  const submitFeedback = async () => {
    await api.post(`/api/viva/session/${sessionId}/feedback`, {
      rating: feedbackRating,
      recommendation: feedbackText,
    });
    setPhase("done");
    saveAttemptState({ phase: "done" });
    stopCamera();
  };

  const summary = results?.summary || null;
  const scorePercent = summary?.percentage || 0;

  return (
    <div className="viva-shell">
      <div className="viva-topbar">
        <div className="container d-flex justify-content-between align-items-center">
          <div className="topbar-left">
            <span className="topbar-icon">🎓</span>
            <span>
              Viva Session: <strong>{studentId || "Candidate"}</strong>
            </span>
          </div>
          <div className="topbar-right">VivaPro by VivaNext</div>
        </div>
      </div>

      <div className="container py-4">
        <div className="viva-header mb-4">
          <h1>AI Viva Examination</h1>
          <p>Secure, timed and proctored interview workflow</p>
        </div>

        <div className={`viva-layout ${showSideCamera ? "" : "single-col"}`}>
          <div className="viva-main">
            {phase === "loading" && (
              <div className="card viva-card stage-card stage-card-centered p-4 text-center loading-card">
                <div className="loading-card-inner">
                  <div className="spinner-border text-primary mb-3" />
                  <div>{loadingMessage}</div>
                </div>
              </div>
            )}

            {phase === "error" && <div className="alert alert-danger">{error}</div>}

            {phase === "confirm" && (
              <div className="card viva-card stage-card stage-card-centered p-4">
                <h4>Candidate Verification</h4>
                <label className="form-label mt-3">Enter your Candidate ID to begin</label>
                <input className="form-control" value={candidateInput} onChange={(e) => setCandidateInput(e.target.value)} />
                {error && <div className="text-danger mt-2">{error}</div>}
                <button className="btn btn-primary mt-3" onClick={handleConfirmId}>
                  Confirm ID
                </button>
              </div>
            )}

            {phase === "rules" && (
              <div className="card viva-card stage-card stage-card-centered p-4">
                <h4>Viva Rules & Regulations</h4>
                <ul className="mt-3">
                  <li>Please ensure you are in a noise free environment with proper lighting and a stable internet connection.</li>
                  <li>Listen to each question first. Start speaking only when the timer starts.</li>
                  <li>You have a maximum of 30 seconds for each answer. Speak clearly and finish before the timer ends.</li>
                  <li>Keep your face clearly visible throughout the exam. Only one face should be in the camera frame.</li>
                  <li>Stay on the exam screen in fullscreen throughout the viva. Do not switch tabs or windows.</li>
                  <li>Proctoring stays active for the full exam. Your activities are logged.</li>
                  <li>If suspicious activity is detected after review your exam may be disqualified and not considered for evaluation.</li>
                </ul>
                <div className="form-check mt-3">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    id="rulesAgree"
                    checked={rulesChecked}
                    onChange={(e) => setRulesChecked(e.target.checked)}
                  />
                  <label className="form-check-label" htmlFor="rulesAgree">
                    I have read and agree to the rules
                  </label>
                </div>
                <button className="btn btn-primary mt-3" disabled={!rulesChecked} onClick={handleAcceptRules}>
                  Proceed
                </button>
              </div>
            )}

            {phase === "camera" && (
              <div className="card viva-card stage-card p-4">
                <h4>Camera Check</h4>
                <p>Please adjust your camera so that only your face is visible.</p>
                <button className="btn btn-primary" disabled={!cameraReady} onClick={() => setPhase("start")}>
                  Continue
                </button>
              </div>
            )}

            {phase === "start" && (
              <div className="card viva-card stage-card p-4">
                <h4>Ready to Begin</h4>
                <p>Click Start Test to begin the viva .</p>
                <button className="btn btn-primary" onClick={handleStartTest}>
                  Start Test
                </button>
              </div>
            )}

            {phase === "interview" && questionData && (
              <div className="card viva-card stage-card p-4">
                <div className="question-meta">
                  <span>
                    Question {questionData.number} / {questionData.total}
                  </span>
                  <span className="badge bg-primary-subtle text-primary">30s timed answer</span>
                </div>
                <p className="question-text mt-2">{questionData.question}</p>
                {countdown > 0 && <div className="big-counter">Question audio starts in {countdown}</div>}
                {isRecording && (
                  <div className="timer-wrap mt-3">
                    <div className="timer-box">{recordingLeft}s</div>
                    <div className="text-muted">Speak loudly & clearly</div>
                  </div>
                )}
                <div className="mt-3">
                  <button
                    className="btn btn-primary"
                    onClick={stopRecording}
                    disabled={!isRecording || isSubmitting || warningModal.show}
                  >
                    Done & Next
                  </button>
                </div>
              </div>
            )}

            {phase === "submit" && (
              <div className="card viva-card stage-card stage-card-centered p-4">
                <h4>All questions answered</h4>
                <p>Please submit to generate your final score and feedback.</p>
                <button className="btn btn-success" onClick={handleSubmitInterview} disabled={isSubmitting || warningModal.show}>
                  {isSubmitting ? "Preparing results..." : "Submit and Show Results"}
                </button>
              </div>
            )}

            {phase === "summary" && results && summary && (
              <div className="card viva-card stage-card stage-card-wide stage-card-centered p-4 text-center">
                <h3>Final Result</h3>
                <div className="score-circle mt-3" style={{ "--score": scorePercent }}>
                  <div className="score-inner">
                    {Math.round(summary.obtained_marks)} / {Math.round(summary.total_marks)}
                  </div>
                </div>
                <div className="summary-grid mt-4">
                  <div className="summary-box">
                    <div className="summary-label">Percentage</div>
                    <div className="summary-value">{summary.percentage}%</div>
                  </div>
                  <div className="summary-box">
                    <div className="summary-label">Grade</div>
                    <div className="summary-value">{summary.grade}</div>
                  </div>
                </div>
                <p className="mt-3 summary-message">{summary.message}</p>
                <button className="btn btn-primary mt-2" onClick={() => setPhase("detailed")}>
                  Check Detailed Score & Feedback
                </button>
              </div>
            )}

            {phase === "detailed" && results && (
              <div className="card viva-card stage-card stage-card-wide stage-card-centered p-4">
                <div className="report-head">
                  <div>
                    <h3 className="mb-1">Interview Report Card</h3>
                    <p className="report-subtitle mb-0">
                      {results.detailed.length} question{results.detailed.length === 1 ? "" : "s"} evaluated
                    </p>
                  </div>
                  <div className="report-mini-stat">
                    <span>Overall</span>
                    <strong>{summary?.percentage ?? 0}%</strong>
                  </div>
                </div>
                {results.detailed.map((item, idx) => {
                  const avgPercent = Math.max(0, Math.min(100, ((item.average_score || 0) / 10) * 100));
                  const isOpen = expandedDetailIndex === idx;
                  return (
                    <div key={`${idx}_${item.question}`} className="detail-item">
                      <button
                        type="button"
                        className="detail-toggle"
                        onClick={() => setExpandedDetailIndex(isOpen ? -1 : idx)}
                        aria-expanded={isOpen}
                        title={isOpen ? "Hide feedback" : "View feedback"}
                      >
                        <div className="detail-toggle-main">
                          <p className="mb-1 detail-question">
                            <strong>Q{idx + 1}:</strong> {item.question}
                          </p>
                          <div className="detail-avg-inline">AI Score {item.average_score}/10</div>
                        </div>
                        <div className="detail-toggle-actions">
                          <span className="feedback-hint">{isOpen ? "Hide Feedback" : "View Feedback"}</span>
                          <span className={`detail-chevron ${isOpen ? "open" : ""}`}>▾</span>
                        </div>
                      </button>
                      <div className="progress mb-2 mt-2" role="progressbar" aria-valuenow={avgPercent} aria-valuemin="0" aria-valuemax="100">
                        <div className="progress-bar" style={{ width: `${avgPercent}%` }}>{avgPercent.toFixed(0)}%</div>
                      </div>
                      <div className={`detail-expand ${isOpen ? "open" : ""}`}>
                        <div className="row g-2 mb-2">
                          <div className="col-md-3"><span className="score-tag">Kimi {item.kimi_score}/10</span></div>
                          <div className="col-md-3"><span className="score-tag">Gemini {item.gemini_score}/10</span></div>
                          <div className="col-md-3"><span className="score-tag">Llama {item["llama_3.3_score"]}/10</span></div>
                          <div className="col-md-3"><span className="score-tag score-tag-avg">Average {item.average_score}/10</span></div>
                        </div>
                        <div className="feedback-box">
                          <div><strong>Gemini:</strong> {item.gemini_feedback}</div>
                          <div><strong>Kimi:</strong> {item.kimi_feedback}</div>
                          <div><strong>Llama:</strong> {item.llama_feedback}</div>
                        </div>
                      </div>
                    </div>
                  );
                })}
                <button className="btn btn-primary mt-3" onClick={() => setPhase("feedback")}>
                  Proceed to Exit
                </button>
              </div>
            )}

            {phase === "feedback" && (
              <div className="card viva-card stage-card stage-card-wide stage-card-centered p-4">
                <h4>Platform Feedback</h4>
                <label className="form-label mt-3">Rating</label>
                <div className="rating-row">
                  {[1, 2, 3, 4, 5].map((n) => (
                    <button
                      key={n}
                      type="button"
                      className={`rating-btn ${feedbackRating === n ? "active" : ""}`}
                      onClick={() => setFeedbackRating(n)}
                    >
                      {n}
                    </button>
                  ))}
                </div>
                <label className="form-label mt-3">Recommendations</label>
                <textarea className="form-control" rows={4} value={feedbackText} onChange={(e) => setFeedbackText(e.target.value)} />
                <button className="btn btn-primary mt-3" onClick={submitFeedback}>
                  Submit Feedback
                </button>
              </div>
            )}

            {phase === "done" && (
              <div className="card viva-card stage-card stage-card-wide stage-card-centered p-4 completion-card text-center">
                <div className="completion-icon">✓</div>
                <h4 className="mb-2">Viva Completed Successfully</h4>
                <p className="mb-0">Thank you for completing the viva and sharing your feedback.</p>
              </div>
            )}
          </div>

          {showSideCamera && (
            <div className="viva-side">
              <div className="camera-panel">
                <video ref={videoRef} muted playsInline />
                {!cameraLive && (
                  <div className="camera-overlay">
                    <div className="camera-overlay-title">Connecting camera...</div>
                    <div className="camera-overlay-sub">Please keep this tab active</div>
                  </div>
                )}
                {phase === "camera" && <div className={`camera-status ${cameraReady ? "ok" : "bad"}`}>{cameraStatus}</div>}
                <div className="camera-hint">Keep your face centered and room well-lit</div>
              </div>
            </div>
          )}
        </div>
      </div>

      {warningModal.show && (
        <div className="exam-warning-backdrop">
          <div className="exam-warning-card">
            <h5 className="exam-warning-title">{warningModal.title}</h5>
            <p>{warningModal.message}</p>
            <p className="exam-warning-note">Warning: All your activity is being recorded.</p>
            <div className="d-flex gap-2 justify-content-center">
              <button
                type="button"
                className="btn btn-primary"
                onClick={async () => {
                  const ok = await requestFullscreen();
                  if (ok) {
                    setWarningModal({ show: false, title: "", message: "" });
                    logIncident("fullscreen_reentered");
                  } else {
                    logIncident("fullscreen_reenter_failed");
                  }
                }}
              >
                Return to Fullscreen
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default VivaExam;
