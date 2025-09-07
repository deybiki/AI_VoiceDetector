





import streamlit as st
import json
import os
from datetime import datetime
import requests
from sentence_transformers import SentenceTransformer, util
import threading



# model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
if "embedding_model" not in st.session_state:
    st.session_state.embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# --- INITIAL CONFIGURATION ---
st.set_page_config(page_title="Result Analysis", layout="wide")
st.markdown("""<style>[data-testid="stSidebar"], [data-testid="collapsedControl"] {display: none !important;}</style>""", unsafe_allow_html=True)

# --- GET IDS FROM SESSION ---
candidate_id = st.session_state.get("candidate_id", "default_student")
# candidate_dir = os.path.join("interviews", candidate_id)
candidate_dir = st.session_state.get("attempt_dir")

# breakdown_path = os.path.join(candidate_dir, "scored_responses.json")
responses_path = os.path.join(candidate_dir, "responses.json")


# reference_answers = st.session_state.get("reference_answers", [])



if not candidate_dir:
    st.error("❌ Attempt data not found. Please restart viva.")
    st.stop()

breakdown_path = os.path.join(candidate_dir, "scored_responses.json")





# --- State Initialization ---
if 'view' not in st.session_state:
    
    st.session_state.view = 'results'





if "results_processed" not in st.session_state:
    with st.spinner("Submitting responses and preparing results..."):
        try:
            if not os.path.exists(breakdown_path):
                st.error("❌ No scored responses found. Please contact admin.")
                st.stop()

            with open(breakdown_path, "r") as f:
                breakdown_json = json.load(f)

            # Load QA pairs for backend submission
            QA_pair = []
            if os.path.exists(responses_path):
                with open(responses_path, "r") as f:
                    responses = json.load(f)
                QA_pair = [{"question": r["question"], "answer": r.get("transcript", "")} for r in responses]

            # --- Cosine similarity with reference answers ---
            reference_answers = st.session_state.get("reference_answers", [])
            similarities = []
            for i, qa in enumerate(QA_pair):
                user_ans = qa["answer"].strip()
                ref_ans = reference_answers[i].strip() if i < len(reference_answers) else ""

                if user_ans and ref_ans:
                    emb_user = st.session_state.embedding_model.encode(user_ans, convert_to_tensor=True)
                    emb_ref = st.session_state.embedding_model.encode(ref_ans, convert_to_tensor=True)
                    raw_score = float(util.cos_sim(emb_user, emb_ref).item())

    # Clamp negatives & scale to 0–10
                    scaled_score = max(raw_score, 0.0) * 10
                else:
                    raw_score = -1.0
                    scaled_score = -1.0

# Save both into QA_pair
                qa["cosine_similarity_raw"] = raw_score
                qa["cosine_similarity_scaled"] = scaled_score

# Collect only scaled version for summaries
                similarities.append(scaled_score)

                # print(f"[DEBUG] Q{i+1}: Raw CS = {raw_score:.4f}, Scaled (0-10) = {scaled_score:.2f}")

            # Compute per-question averages
            question_averages = [r.get("average_score", -1) for r in breakdown_json if r.get("average_score", -1) >= 0]

            # Compute final score (avg of averages)
            final_score = round(sum(question_averages) / len(question_averages), 2) if question_averages else -1

            st.session_state["scoring_results"] = breakdown_json

            # --- Send to backend (MongoDB insertion happens there) ---
            data_to_submit = {
                "testId": st.session_state.get("test_id", ""),
                "candidateId": candidate_id,
                "vivaDate": str(datetime.now()),
                "questionAnswerPairs": QA_pair,   # now includes cosine_similarity
                "totalScore": final_score,
                "questionAverages": question_averages,
                "detailedBreakdown": breakdown_json,
                "cosineSimilarities": similarities  # summary list
            }

            try:
                response = requests.post("http://localhost:5000/api/submit-viva", json=data_to_submit)
                if response.status_code == 200:
                    print("✅ Results submitted successfully")
                else:
                    print(f"⚠️ Backend submission failed: {response.status_code}")
            except Exception as e:
                print(f"⚠️ Could not reach backend: {e}")

        except Exception as e:
            st.error(f"An error occurred while preparing results: {e}")
    st.session_state["results_processed"] = True




# --- VIEW 1: RESULTS REPORT CARD ---
if st.session_state.view == 'results':
    st.markdown("<h2 style='color: green;'>Interview Report Card</h2>", unsafe_allow_html=True)

    if "scoring_results" in st.session_state and st.session_state["scoring_results"]:
        for result in st.session_state["scoring_results"]:
            # Show question + scores
            st.markdown(f"**Q: {result['question']}**")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Kimi K2  Score", f"{result.get('gpt_4_score', 'N/A')}/10")
            col2.metric("Google DeepMind Score", f"{result.get('opus_4_score', 'N/A')}/10")
            col3.metric("Llama Score", f"{result.get('llama_3.3_score', 'N/A')}/10")
            col4.metric("Average", f"{result.get('average_score', 'N/A')}/10")
            st.markdown("---")

            # Feedback
            with st.expander(f"Feedback for: **{result['question']}**"):
                st.markdown(f"**Kimi K2 Feedback:** {result.get('gpt_feedback', 'N/A')}")
                st.markdown(f"**Google DeepMind Feedback:** {result.get('claude_feedback', 'N/A')}")
                st.markdown(f"**Llama Feedback:** {result.get('llama_feedback', 'N/A')}")

    else:
        st.error("No scoring results to display.")

    if st.button("Proceed to Exit"):
        st.session_state.view = 'feedback'
        st.rerun()

# --- VIEW 2: PLATFORM FEEDBACK ---





# --- VIEW 2: PLATFORM FEEDBACK ---
elif st.session_state.view == 'feedback':
    st.subheader("Please Give Platform Feedback")

    rating = st.radio(
        "How would you rate your experience with this platform?",
        options=('⭐', '⭐⭐', '⭐⭐⭐', '⭐⭐⭐⭐', '⭐⭐⭐⭐⭐'),
        horizontal=True,
        index=4
    )

    recommendation = st.text_area(
        "Any recommendations to improve your experience?",
        placeholder="The platform was smooth, but..."
    )

    if st.button("Submit Feedback"):
        # Prepare payload for backend
        payload = {
            "candidateId": candidate_id,
            "rating": len(rating),  # convert '⭐⭐⭐' -> 3
            "recommendation": recommendation,
            "timestamp": str(datetime.now()),
        }

        BACKEND_URL = "http://localhost:5000/api/feedback/platform"

        # 🚀 Send only to backend (no local save)
        r = requests.post(BACKEND_URL, json=payload, timeout=8)

        if r.status_code in (200, 201):
            st.success("✅ Feedback saved to database.")
        else:
            st.error(f"❌ Failed to save feedback. Server responded {r.status_code}: {r.text}")
            st.stop()

        # Transition to final view
        st.session_state.view = 'final_thank_you'
        st.rerun()

# --- VIEW 3: FINAL THANK YOU ---
# elif st.session_state.view == 'final_thank_you':
#     st.success("**Thank you for completing the viva and providing your valuable feedback!**")
#     st.balloons()
#     st.session_state.clear()
#     st.stop()

elif st.session_state.view == 'final_thank_you':
    # exit fullscreen cleanly
    

    st.success("**Thank you for completing the viva and providing your valuable feedback!**")
    st.balloons()
    st.session_state.clear()
    st.stop()










