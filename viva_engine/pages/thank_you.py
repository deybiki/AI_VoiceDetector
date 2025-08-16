

# # import streamlit as st
# # import json
# # import os
# # from datetime import datetime
# # import requests
# # from llm_scoring import score_all_responses, generate_analysis_responses

# # # Import the new face monitor component
# # from face_monitor import render_face_monitor


# # st.set_page_config(page_title="Result Analysis", layout="centered")

# # # Candidate ID
# # candidate_id = st.session_state.get("candidate_id", "default")
# # breakdown_path = f"interviews/{candidate_id}/breakdown_results.json"

# # # Perform scoring and backend update only once
# # # if "scoring_results" not in st.session_state:
# # #     try:
# # #         question_answers, final_score, breakdown_json = score_all_responses(candidate_id)
# # #         generate_analysis_responses(candidate_id)
# # #         st.session_state["scoring_results"] = breakdown_json

# # #         # ✅ Send results to backend
# # #         data = {
# # #             "candidateId": candidate_id,
# # #             "vivaDate": str(datetime.now()),
# # #             "questionAnswerPairs": question_answers,
# # #             "totalScore": final_score,
# # #             "detailedBreakdown": breakdown_json,
# # #         }

# # # thank_you.py

# # # Perform scoring and backend update only once
# # if "scoring_results" not in st.session_state:
# #     with st.spinner("Finalizing results..."):
# #         try:
# #             # FIX: Use the new 'QA_pair' variable name
# #             QA_pair, final_score, breakdown_json = score_all_responses(candidate_id)
# #             generate_analysis_responses(candidate_id)
# #             st.session_state["scoring_results"] = breakdown_json

# #             # FIX: Create the payload with the exact field names your backend expects
# #             data = {
# #                 "student": candidate_id,
# #                 "test": st.session_state.get("test_db_id", "Unknown Test ID"), # Assumes you've stored this
# #                 "answers": QA_pair,
# #                 "totalScore": final_score,
# #                 "detailedBreakdown": breakdown_json,
# #             }




# #             response = requests.post("http://localhost:5000/api/submit-viva", json=data)

# #             if response.status_code == 200:
# #                st.success("✅ Viva data successfully submitted to backend.")
# #             else:
# #                st.error(f"❌ Failed to submit viva data. Error: {response.text}")

# #         except Exception as e:
# #            st.error(f"Scoring or backend save failed: {e}")
        



# # # View control toggle
# # if "show_analysis" not in st.session_state:
# #     st.session_state["show_analysis"] = False

# # # Report Card View
# # if not st.session_state["show_analysis"]:
# #     st.markdown("<h2 style='color: green;'>📊 Interview Report Card</h2>", unsafe_allow_html=True)
# #     st.markdown("<hr>", unsafe_allow_html=True)

# #     if "scoring_results" in st.session_state:
# #         for idx, result in enumerate(st.session_state["scoring_results"]):
# #             st.markdown(f"**Q{idx + 1}: {result['question']}**")
# #             st.markdown(f"- GPT Score: `{result['gpt_4_score']}/10`")
# #             st.markdown(f"- Gemini Score: `{result['gemini_1.5_score']}/10`")
# #             st.markdown(f"- Claude Score: `{result['opus_4_score']}/10`")
# #             st.markdown(f"- Meta Score: `{result['llama_3.3_score']}/10`")
# #             st.markdown(f"- **Average Score: `{result['average_score']}/10`**")
# #             st.markdown("---")
# #     else:
# #         st.error("No scoring results found. Please return to the interview page.")

# #     # st.write("**Thank you for your patience.**")
# #     # st.markdown("**Best wishes for your future!**")

# #     if st.button("🔍 View Result Analysis"):
# #         st.session_state["show_analysis"] = True

# # # Detailed Analysis View
# # else:
# #     st.subheader("🔍 Detailed Result Analysis")

# #     if os.path.exists(breakdown_path):
# #         try:
# #             with open(breakdown_path, "r") as f:
# #                 data = json.load(f)
# #                 for d in data:
# #                     st.markdown(f"**Q:** {d['question']}")
# #                     st.markdown(f"**Answer:** {d['answer']}")
# #                     st.markdown(f"**Final Score:** `{d.get('average_score', '-')}/10`")
# #                     st.markdown(f"**GPT Feedback:** {d.get('gpt_feedback', 'N/A')}")
# #                     st.markdown(f"**Gemini Feedback:** {d.get('gemini_feedback', 'N/A')}")
# #                     st.markdown(f"**Meta Feedback:** {d.get('llama_feedback', 'N/A')}")
# #                     st.markdown(f"**Claude Feedback:** {d.get('claude_feedback', 'N/A')}")
# #                     st.markdown("---")
# #         except Exception as e:
# #             st.error(f"Failed to load analysis: {e}")
# #     else:
# #         st.error("⚠️ Analysis not available yet. Please try again later.")

# #     # if st.button("EXIT"):
# #     #     for key in list(st.session_state.keys()):
# #     #         del st.session_state[key]
# #     #     # st.switch_page("streamlit_app.py")
# #     #     st.write("**Thank you for your patience.**")
# #     #     st.markdown("**Best wishes for your future!**")
# #     #     st.balloon("🎈 Thank you for using our AI-powered viva-voce system! 🎈")
# #     # if st.button("EXIT"):
# #     # # ✅ Clear all session state keys
# #     #     st.session_state.clear()

# #     # # ✅ Show final thank-you message
# #     #     st.success("**Thank you for your patience.**")
# #     #     st.markdown("**Best wishes for your future!**")
# #     #     st.markdown("🎈 Thank you for using our AI-powered viva-voce system! 🎈")

# #     # # ✅ Nice visual effect
# #     #     st.balloons()

# #     # # ✅ Stop execution so nothing else runs after exit
# #     #     # st.stop()
# #     if st.button("EXIT"):
# #           st.success("**Thank you for your patience.**")
# #           st.session_state.clear()
# #           st.markdown("**Best wishes for your future!**")
# #           st.markdown("🎈 Thank you for using our AI-powered viva-voce system! 🎈")
# #           st.balloons()
# #           st.stop() # <-- This line is now active




# #  # RENDER THE FACE MONITOR AT THE END OF THE SCRIPT
# # # render_face_monitor()
# # # st.rerun()












































# # thank_you.py

# import streamlit as st
# import json
# import os
# from datetime import datetime
# import requests
# from llm_scoring import score_all_responses, generate_analysis_responses

# # --- INITIAL CONFIGURATION ---
# st.set_page_config(page_title="Result Analysis", layout="wide")
# st.markdown("""<style>[data-testid="stSidebar"], [data-testid="collapsedControl"] {display: none !important;}</style>""", unsafe_allow_html=True)

# # --- GET IDS FROM SESSION ---
# candidate_id = st.session_state.get("candidate_id", "default_student")
# breakdown_path = f"interviews/{candidate_id}/breakdown_results.json"

# # --- SCORING AND BACKEND SUBMISSION (RUNS ONLY ONCE) ---
# if "results_processed" not in st.session_state:
#     with st.spinner("Calculating scores and submitting results..."):
#         try:
#             # 1. Get all the necessary data from the scoring function
#             QA_pair, final_score, breakdown_json = score_all_responses(candidate_id)
#             generate_analysis_responses(candidate_id)
            
#             # Store the data needed for the report card in the session
#             st.session_state["scoring_results"] = breakdown_json

#             # 2. **CRITICAL FIX**: Create the JSON payload with the EXACT field names
#             #    that your database screenshot shows: candidateId, vivaDate, etc.
            # data_to_submit = {
            #     "candidateId": candidate_id,
            #     "vivaDate": str(datetime.now()),
            #     "questionAnswerPairs": QA_pair,
            #     "totalScore": final_score,
            #     "detailedBreakdown": breakdown_json
            # }

            # # 3. Send the correctly formatted data to your backend
            # response = requests.post("http://localhost:5000/api/submit-viva", json=data_to_submit)

            # if response.status_code == 200:
            #     st.success("✅ Viva data successfully submitted to the backend.")
            # else:
            #     st.error(f"❌ Failed to submit data. Server responded with: {response.text}")

#         except Exception as e:
#             st.error(f"An error occurred during scoring or submission: {e}")
            
#     st.session_state["results_processed"] = True

# # --- Main Display Logic ---
# st.markdown("<h2 style='color: green;'>📊 Interview Report Card</h2>", unsafe_allow_html=True)

# if "scoring_results" in st.session_state and st.session_state["scoring_results"]:
#     for result in st.session_state["scoring_results"]:
#         st.markdown(f"**Q: {result['question']}**")
#         col1, col2, col3, col4 = st.columns(4)
#         col1.metric("GPT Score", f"{result.get('gpt_4_score', 'N/A')}/10")
#         col2.metric("Gemini Score", f"{result.get('gemini_1.5_score', 'N/A')}/10")
#         col3.metric("Claude Score", f"{result.get('opus_4_score', 'N/A')}/10")
#         col4.metric("Meta Score", f"{result.get('llama_3.3_score', 'N/A')}/10")
#         st.markdown(f"**Average Score: `{result.get('average_score', 'N/A')}/10`**")
#         st.markdown("---")

    # st.subheader("🔍 Detailed Feedback")
    # if os.path.exists(breakdown_path):
    #     with open(breakdown_path, "r") as f:
    #         data = json.load(f)
    #         for d in data:
    #             with st.expander(f"Analysis for: **{d['question']}**"):
    #                 st.markdown(f"**Your Answer:** {d['answer']}")
    #                 st.markdown("---")
    #                 st.markdown(f"**GPT Feedback:** {d.get('gpt_feedback', 'N/A')}")
    #                 st.markdown(f"**Gemini Feedback:** {d.get('gemini_feedback', 'N/A')}")
    #                 st.markdown(f"**Meta Feedback:** {d.get('llama_feedback', 'N/A')}")
    #                 st.markdown(f"**Claude Feedback:** {d.get('claude_feedback', 'N/A')}")
    # else:
    #     st.warning("Detailed feedback file not found.")

# else:
#     st.error("No scoring results to display.")


# if st.button("Proceed to Exit"):
#         st.session_state.view = 'feedback'
#         st.rerun()


# # --- VIEW 2: PLATFORM FEEDBACK ---
# elif st.session_state.view == 'feedback':
#     st.subheader("Please Give Platform Feedback")
    
#     # Five-star marking options
#     rating = st.radio(
#         "How would you rate your experience with this platform?",
#         options=('⭐', '⭐⭐', '⭐⭐⭐', '⭐⭐⭐⭐', '⭐⭐⭐⭐⭐'),
#         horizontal=True,
#         index=4  # Default to 5 stars
#     )

#     # Recommendation text input
#     recommendation = st.text_area(
#         "Any recommendations to improve your experience?",
#         placeholder="The platform was smooth, but..."
#     )

#     # Submit button
#     if st.button("Submit Feedback"):
#         feedback_data = {
#             "candidateId": candidate_id,
#             "rating": f"{len(rating)}/5",
#             "recommendation": recommendation,
#             "timestamp": str(datetime.now())
#         }

#         # Save feedback to a JSON file
#         feedback_dir = os.path.join("interviews", candidate_id)
#         os.makedirs(feedback_dir, exist_ok=True)
#         with open(os.path.join(feedback_dir, "platform_feedback.json"), "w") as f:
#             json.dump(feedback_data, f, indent=4)

#         # Transition to the final view
#         st.session_state.view = 'final_thank_you'
#         st.rerun()

# # --- VIEW 3: FINAL THANK YOU MESSAGE ---
# elif st.session_state.view == 'final_thank_you':
#     st.success("**Thank you for completing the viva and providing your valuable feedback!**")
#     st.balloons()
#     st.session_state.clear() # Clear the session state to finalize
#     st.stop()

# # if st.button("EXIT"):
# #     st.success("**Thank you for completing the viva!**")
# #     st.balloons()
# #     st.session_state.clear()
# #     st.stop()






# thank_you.py

import streamlit as st
import json
import os
from datetime import datetime
import requests
from llm_scoring import score_all_responses, generate_analysis_responses

# --- INITIAL CONFIGURATION ---
st.set_page_config(page_title="Result Analysis", layout="wide")
st.markdown("""<style>[data-testid="stSidebar"], [data-testid="collapsedControl"] {display: none !important;}</style>""", unsafe_allow_html=True)

# --- GET IDS FROM SESSION ---
candidate_id = st.session_state.get("candidate_id", "default_student")
breakdown_path = f"interviews/{candidate_id}/breakdown_results.json"

# --- State Initialization for this page ---
# This will control which view is shown: 'results', 'feedback', or 'final_thank_you'
if 'view' not in st.session_state:
    st.session_state.view = 'results'

# --- SCORING AND BACKEND SUBMISSION (RUNS ONLY ONCE) ---
if "results_processed" not in st.session_state:
    with st.spinner("Submitting respones and calculating results..."):
        try:
            # Assumes score_all_responses is corrected to return three values
            QA_pair, final_score, breakdown_json = score_all_responses(candidate_id)
            generate_analysis_responses(candidate_id)
            st.session_state["scoring_results"] = breakdown_json


            data_to_submit = {
                "candidateId": candidate_id,
                "vivaDate": str(datetime.now()),
                "questionAnswerPairs": QA_pair,
                "totalScore": final_score,
                "detailedBreakdown": breakdown_json
            }

            # 3. Send the correctly formatted data to your backend
            response = requests.post("http://localhost:5000/api/submit-viva", json=data_to_submit)

            if response.status_code == 200:
                st.success("✅ Viva data successfully submitted to the backend.")
            else:
                st.error(f"❌ Failed to submit data. Server responded with: {response.text}")



        except Exception as e:
            st.error(f"An error occurred during scoring or submission: {e}")
    st.session_state["results_processed"] = True

# --- State Machine: Controls what is shown on the page ---

# --- VIEW 1: RESULTS REPORT CARD ---
if st.session_state.view == 'results':
    st.markdown("<h2 style='color: green;'>📊 Interview Report Card</h2>", unsafe_allow_html=True)

    if "scoring_results" in st.session_state and st.session_state["scoring_results"]:
        for result in st.session_state["scoring_results"]:
            st.markdown(f"**Q: {result['question']}**")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("GPT Score", f"{result.get('gpt_4_score', 'N/A')}/10")
            col2.metric("Gemini Score", f"{result.get('gemini_1.5_score', 'N/A')}/10")
            col3.metric("Claude Score", f"{result.get('opus_4_score', 'N/A')}/10")
            col4.metric("Meta Score", f"{result.get('llama_3.3_score', 'N/A')}/10")
            st.markdown(f"**Average Score: `{result.get('average_score', 'N/A')}/10`**")
            st.markdown("---")

            st.subheader("🔍 Detailed Feedback")
            if os.path.exists(breakdown_path):
                with open(breakdown_path, "r") as f:
                     data = json.load(f)
                     for d in data:
                         with st.expander(f"Analysis for: **{d['question']}**"):
                             st.markdown(f"**Your Answer:** {d['answer']}")
                             st.markdown("---")
                             st.markdown(f"**GPT Feedback:** {d.get('gpt_feedback', 'N/A')}")
                             st.markdown(f"**Gemini Feedback:** {d.get('gemini_feedback', 'N/A')}")
                             st.markdown(f"**Meta Feedback:** {d.get('llama_feedback', 'N/A')}")
                             st.markdown(f"**Claude Feedback:** {d.get('claude_feedback', 'N/A')}")
            else:
               st.warning("Detailed feedback file not found.")
    else:
        st.error("No scoring results to display.")

    # This button now transitions to the feedback view
    if st.button("Proceed to Exit"):
        st.session_state.view = 'feedback'
        st.rerun()

# --- VIEW 2: PLATFORM FEEDBACK ---
elif st.session_state.view == 'feedback':
    st.subheader("Please Give Platform Feedback")
    
    # Five-star marking options
    rating = st.radio(
        "How would you rate your experience with this platform?",
        options=('⭐', '⭐⭐', '⭐⭐⭐', '⭐⭐⭐⭐', '⭐⭐⭐⭐⭐'),
        horizontal=True,
        index=4  # Default to 5 stars
    )

    # Recommendation text input
    recommendation = st.text_area(
        "Any recommendations to improve your experience?",
        placeholder="The platform was smooth, but..."
    )

    # Submit button
    if st.button("Submit Feedback"):
        feedback_data = {
            "candidateId": candidate_id,
            "rating": f"{len(rating)}/5",
            "recommendation": recommendation,
            "timestamp": str(datetime.now())
        }

        # Save feedback to a JSON file
        feedback_dir = os.path.join("interviews", candidate_id)
        os.makedirs(feedback_dir, exist_ok=True)
        with open(os.path.join(feedback_dir, "platform_feedback.json"), "w") as f:
            json.dump(feedback_data, f, indent=4)

        # Transition to the final view
        st.session_state.view = 'final_thank_you'
        st.rerun()

# --- VIEW 3: FINAL THANK YOU MESSAGE ---
elif st.session_state.view == 'final_thank_you':
    st.success("**Thank you for completing the viva and providing your valuable feedback!**")
    st.balloons()
    st.session_state.clear() # Clear the session state to finalize
    st.stop()