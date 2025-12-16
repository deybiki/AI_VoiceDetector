









# import streamlit as st
# import json
# import os
# from datetime import datetime
# import requests
# from sentence_transformers import SentenceTransformer, util
# import threading



# # model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
# if "embedding_model" not in st.session_state:
#     st.session_state.embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# # --- INITIAL CONFIGURATION ---
# st.set_page_config(page_title="Result Analysis", layout="wide")
# st.markdown("""<style>[data-testid="stSidebar"], [data-testid="collapsedControl"] {display: none !important;}</style>""", unsafe_allow_html=True)

# # --- GET IDS FROM SESSION ---
# candidate_id = st.session_state.get("candidate_id", "default_student")
# # candidate_dir = os.path.join("interviews", candidate_id)
# candidate_dir = st.session_state.get("attempt_dir")

# # breakdown_path = os.path.join(candidate_dir, "scored_responses.json")
# responses_path = os.path.join(candidate_dir, "responses.json")


# # reference_answers = st.session_state.get("reference_answers", [])



# if not candidate_dir:
#     st.error("❌ Attempt data not found. Please restart viva.")
#     st.stop()

# breakdown_path = os.path.join(candidate_dir, "scored_responses.json")





# # --- State Initialization ---
# if 'view' not in st.session_state:
    
#     st.session_state.view = 'results'





# if "results_processed" not in st.session_state:
#     with st.spinner("Submitting responses and preparing results..."):
#         try:
#             if not os.path.exists(breakdown_path):
#                 st.error("❌ No scored responses found. Please contact admin.")
#                 st.stop()

#             with open(breakdown_path, "r") as f:
#                 breakdown_json = json.load(f)

#             # Load QA pairs for backend submission
#             QA_pair = []
#             if os.path.exists(responses_path):
#                 with open(responses_path, "r") as f:
#                     responses = json.load(f)
#                 QA_pair = [{"question": r["question"], "answer": r.get("transcript", "")} for r in responses]

#             # --- Cosine similarity with reference answers ---
#             reference_answers = st.session_state.get("reference_answers", [])
#             similarities = []
#             for i, qa in enumerate(QA_pair):
#                 user_ans = qa["answer"].strip()
#                 ref_ans = reference_answers[i].strip() if i < len(reference_answers) else ""

#                 if user_ans and ref_ans:
#                     emb_user = st.session_state.embedding_model.encode(user_ans, convert_to_tensor=True)
#                     emb_ref = st.session_state.embedding_model.encode(ref_ans, convert_to_tensor=True)
#                     raw_score = float(util.cos_sim(emb_user, emb_ref).item())

#     # Clamp negatives & scale to 0–10
#                     scaled_score = max(raw_score, 0.0) * 10
#                 else:
#                     raw_score = -1.0
#                     scaled_score = -1.0

# # Save both into QA_pair
#                 qa["cosine_similarity_raw"] = raw_score
#                 qa["cosine_similarity_scaled"] = scaled_score

# # Collect only scaled version for summaries
#                 similarities.append(scaled_score)

#                 # print(f"[DEBUG] Q{i+1}: Raw CS = {raw_score:.4f}, Scaled (0-10) = {scaled_score:.2f}")

#             # Compute per-question averages
#             question_averages = [r.get("average_score", -1) for r in breakdown_json if r.get("average_score", -1) >= 0]

#             # Compute final score (avg of averages)
#             final_score = round(sum(question_averages) / len(question_averages), 2) if question_averages else -1

#             st.session_state["scoring_results"] = breakdown_json

#             # --- Send to backend (MongoDB insertion happens there) ---
#             data_to_submit = {
#                 "testId": st.session_state.get("test_id", ""),
#                 "candidateId": candidate_id,
#                 "vivaDate": str(datetime.now()),
#                 "questionAnswerPairs": QA_pair,   # now includes cosine_similarity
#                 "totalScore": final_score,
#                 "questionAverages": question_averages,
#                 "detailedBreakdown": breakdown_json,
#                 "cosineSimilarities": similarities  # summary list
#             }

#             try:
#                 response = requests.post("http://localhost:5000/api/submit-viva", json=data_to_submit)
#                 if response.status_code == 200:
#                     print("✅ Results submitted successfully")
#                 else:
#                     print(f"⚠️ Backend submission failed: {response.status_code}")
#             except Exception as e:
#                 print(f"⚠️ Could not reach backend: {e}")

#         except Exception as e:
#             st.error(f"An error occurred while preparing results: {e}")
#     st.session_state["results_processed"] = True




# # --- VIEW 1: RESULTS REPORT CARD ---
# if st.session_state.view == 'results':
#     st.markdown("<h2 style='color: green;'>Interview Report Card</h2>", unsafe_allow_html=True)

#     if "scoring_results" in st.session_state and st.session_state["scoring_results"]:
#         for result in st.session_state["scoring_results"]:
#             # Show question + scores
#             st.markdown(f"**Q: {result['question']}**")
#             col1, col2, col3, col4 = st.columns(4)
    
#             col2.metric("Gemini Score", f"{result.get('gemini_score', 'N/A')}/10")
#             col1.metric("Kimi K2 Score", f"{result.get('kimi_score', 'N/A')}/10")
#             col3.metric("Llama Score", f"{result.get('llama_3.3_score', 'N/A')}/10")
#             col4.metric("Average", f"{result.get('average_score', 'N/A')}/10")
#             st.markdown("---")

#             # Feedback
#             with st.expander(f"Feedback for: **{result['question']}**"):
                
#                 st.markdown(f"**Gemini Feedback:** {result.get('gemini_feedback', 'N/A')}")
#                 st.markdown(f"**Kimi K2 Feedback:** {result.get('kimi_feedback', 'N/A')}")
#                 st.markdown(f"**Llama Feedback:** {result.get('llama_feedback', 'N/A')}")

#     else:
#         st.error("No scoring results to display.")

#     if st.button("Proceed to Exit"):
#         st.session_state.view = 'feedback'
#         st.rerun()

# # --- VIEW 2: PLATFORM FEEDBACK ---





# # --- VIEW 2: PLATFORM FEEDBACK ---
# elif st.session_state.view == 'feedback':
#     st.subheader("Please Give Platform Feedback")

#     rating = st.radio(
#         "How would you rate your experience with this platform?",
#         options=('⭐', '⭐⭐', '⭐⭐⭐', '⭐⭐⭐⭐', '⭐⭐⭐⭐⭐'),
#         horizontal=True,
#         index=4
#     )

#     recommendation = st.text_area(
#         "Any recommendations to improve your experience?",
#         placeholder="The platform was smooth, but..."
#     )

#     if st.button("Submit Feedback"):
#         # Prepare payload for backend
#         payload = {
#             "candidateId": candidate_id,
#             "rating": len(rating),  # convert '⭐⭐⭐' -> 3
#             "recommendation": recommendation,
#             "timestamp": str(datetime.now()),
#         }

#         BACKEND_URL = "http://localhost:5000/api/feedback/platform"

#         # 🚀 Send only to backend (no local save)
#         r = requests.post(BACKEND_URL, json=payload, timeout=8)

#         if r.status_code in (200, 201):
#             st.success("✅ Feedback saved to database.")
#         else:
#             st.error(f"❌ Failed to save feedback. Server responded {r.status_code}: {r.text}")
#             st.stop()

#         # Transition to final view
#         st.session_state.view = 'final_thank_you'
#         st.rerun()

# # --- VIEW 3: FINAL THANK YOU ---
# # elif st.session_state.view == 'final_thank_you':
# #     st.success("**Thank you for completing the viva and providing your valuable feedback!**")
# #     st.balloons()
# #     st.session_state.clear()
# #     st.stop()

# elif st.session_state.view == 'final_thank_you':
#     # exit fullscreen cleanly
    

#     st.success("**Thank you for completing the viva and providing your valuable feedback!**")
#     st.balloons()
#     st.session_state.clear()
#     st.stop()




















import streamlit as st
import json
import os
from datetime import datetime
import requests
import threading
import streamlit.components.v1 as components



# --- INITIAL CONFIGURATION ---
st.set_page_config(page_title="Result Analysis", layout="wide")
st.markdown("""<style>[data-testid="stSidebar"], [data-testid="collapsedControl"] {display: none !important;}</style>""", unsafe_allow_html=True)

st.markdown(
    """
    <style>
    /* Primary action buttons */
    div.stButton > button {
        background-color: #4285F4 !important;
        color: white !important;
        font-weight: 600;
        font-size: 16px;
        border-radius: 8px;
        padding: 10px 24px;
        border: none;
        width: 100%;
        transition: background-color 0.2s ease;
    }

    div.stButton > button:hover {
        background-color: #2b6fe3 !important;
        color: white !important;
    }

    div.stButton > button:active {
        transform: scale(0.98);
    }
    </style>
    """,
    unsafe_allow_html=True
)



# --- GET IDS FROM SESSION ---
candidate_id = st.session_state.get("candidate_id", "default_student")
# candidate_dir = os.path.join("interviews", candidate_id)
candidate_dir = st.session_state.get("attempt_dir")

# breakdown_path = os.path.join(candidate_dir, "scored_responses.json")
responses_path = os.path.join(candidate_dir, "responses.json")





if not candidate_dir:
    st.error("❌ Attempt data not found. Please restart viva.")
    st.stop()

breakdown_path = os.path.join(candidate_dir, "scored_responses.json")





# --- State Initialization ---
# if 'view' not in st.session_state:
    
#     st.session_state.view = 'results'


if 'view' not in st.session_state:
    st.session_state.view = 'summary'






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





            similarities = []

            for qa in QA_pair:
                qa["cosine_similarity_raw"] = None
                qa["cosine_similarity_scaled"] = None
                similarities.append(None)




                # print(f"[DEBUG] Q{i+1}: Raw CS = {raw_score:.4f}, Scaled (0-10) = {scaled_score:.2f}")

            # Compute per-question averages
            question_averages = [r.get("average_score", -1) for r in breakdown_json if r.get("average_score", -1) >= 0]
            st.session_state["question_averages"] = question_averages

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

question_averages = st.session_state.get("question_averages", [])



total_questions = len(question_averages)
total_marks = total_questions * 10
obtained_marks = sum(question_averages)

percentage = round((obtained_marks / total_marks) * 100, 2) if total_marks > 0 else 0

def get_grade_and_message(percent):
    if percent >= 80:
        return "A+", "Outstanding performance! You clearly know your fundamentals."
    elif percent >= 70:
        return "A", "Excellent work. Your understanding is strong and well-demonstrated."
    elif percent >= 60:
        return "B+", "Very good effort. A little refinement can take you to excellence."
    else:
        return "B", "Good attempt. Strengthen core concepts for better results."





# import streamlit.components.v1 as components

if st.session_state.view == "summary":

    grade, message = get_grade_and_message(percentage)

    # Push content slightly down
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Title
    # st.markdown(
    #     "<h1 style='text-align:center;'>Final Result</h1>",
    #     unsafe_allow_html=True
    # )
    st.markdown(
         "<h2 style='margin-top:-60px;'>Final Result</h2>",
          unsafe_allow_html=True
)


    st.markdown("<br>", unsafe_allow_html=True)

    # BIG SCORE CIRCLE (HTML only for this part)
    st.markdown(
        f"""
        <div style="
            display:flex;
            justify-content:center;
            align-items:center;
            width:100%;
            margin:40px 0;
        ">
            <div style="
                width:260px;
                height:260px;
                border-radius:50%;
                border:14px solid #dc2626;
                display:flex;
                align-items:center;
                justify-content:center;
                font-size:64px;
                font-weight:900;
                color:#dc2626;
            ">
                {int(obtained_marks)} / {int(total_marks)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Percentage
    st.markdown(
        f"<p style='text-align:center; font-size:24px;'>Percentage: <b>{percentage}%</b></p>",
        unsafe_allow_html=True
    )

    # Grade
    st.markdown(
        f"<p style='text-align:center; font-size:32px; font-weight:800;'>Grade: {grade}</p>",
        unsafe_allow_html=True
    )

    # Message
    st.markdown(
        f"<p style='text-align:center; font-size:20px; color:#374151;'>{message}</p>",
        unsafe_allow_html=True
    )

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Disclaimer
    st.markdown(
        """
        <p style="
            text-align:center;
            font-size:16px;
            color:#6b7280;
            font-style:italic;
        ">
            Disclaimer: Your score has been evaluated by an AI system.<br>
            No human examiner was involved — so yes, blame LLM.
        </p>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Action button — wide, centered
    left, center, right = st.columns([1, 2, 1])
    with center:
        if st.button("Check Detailed Score & Feedback", use_container_width=True):
           st.session_state.view = "results"
           st.rerun()




# --- VIEW 1: RESULTS REPORT CARD ---
elif st.session_state.view == 'results':
    st.markdown("<h2 style='color: green;'>Interview Report Card</h2>", unsafe_allow_html=True)

    if "scoring_results" in st.session_state and st.session_state["scoring_results"]:
        for result in st.session_state["scoring_results"]:
            # Show question + scores
            st.markdown(f"**Q: {result['question']}**")
            col1, col2, col3, col4 = st.columns(4)
    
            col2.metric("Gemini Score", f"{result.get('gemini_score', 'N/A')}/10")
            col1.metric("Kimi K2 Score", f"{result.get('kimi_score', 'N/A')}/10")
            col3.metric("Llama Score", f"{result.get('llama_3.3_score', 'N/A')}/10")
            col4.metric("Average", f"{result.get('average_score', 'N/A')}/10")
            st.markdown("---")

            # Feedback
            with st.expander(f"Feedback for: **{result['question']}**"):
                
                st.markdown(f"**Gemini Feedback:** {result.get('gemini_feedback', 'N/A')}")
                st.markdown(f"**Kimi K2 Feedback:** {result.get('kimi_feedback', 'N/A')}")
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
























