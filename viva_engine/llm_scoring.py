






import streamlit as st
import os
import re
import json
from typing import List, Dict, Tuple
from retry import retry
from openai import OpenAI
from dotenv import load_dotenv  
from groq import Groq
import google.generativeai as genai
from cerebras.cloud.sdk import Cerebras



# ------------------- API Key Configuration ------------------- #
load_dotenv(override=True)

# LLAMA_API_KEY = os.getenv("LLAMA_API_KEY")
GROQ_LLAMA_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_2_LLMA_API_KEY = os.getenv("GROQ_API_KEY_ALT")



# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_KEY_ALT = os.getenv("GEMINI_API_KEY_ALT")


####################################################################

# GEMMA_2_API_API_KEY = os.getenv("GEMMA_API_KEY_ALT")
# GEMMA_API_KEY = os.getenv("GEMMA_API_KEY")

###################################################################


# GPT_API_KEY = os.getenv("GPT_API_KEY")
# GPT_API_KEY_ALT = os.getenv("GPT_API_KEY_ALT")






Deepseek_API_KEY = os.getenv("DEEPSEEK_API_KEY")

Deepseek_2_API_KEY = os.getenv("DEEPSEEK_2_API_KEY")






def init_groq_client(api_key, name):
    """Initialize Groq-based client"""
    if not api_key:
        print(f"[ERROR] {name} key not found")
        return None
    return Groq(api_key=api_key)


def init_client(api_key, name):
    if not api_key:
        print(f"[ERROR] {name} key not found")
        return None
    return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)







# client_openai = init_client(OPENAI_API_KEY, "OPENAI")
client_groq_2_llama = init_groq_client(GROQ_2_LLMA_API_KEY, "LLAMA2")
client_llama = init_groq_client(GROQ_LLAMA_API_KEY, "LLAMA")








# client_gemma = init_groq_client(GEMMA_API_KEY, "GEMMA")

# client_2_gemma = init_groq_client(GEMMA_2_API_API_KEY, "GEMMA2")



# client_llama  = init_client(LLAMA_API_KEY,  "LLAMA")




###############################################################




client_deepseek = init_groq_client(Deepseek_API_KEY, "DEEPSEEK")

client_2_deepseek = init_groq_client(Deepseek_2_API_KEY, "DEEPSEEK")






# ------------------- Scoring Helper ------------------- #
# def parse_model_response(raw: str) -> Dict:
#     """Ensure JSON parsing with fallback"""
#     try:
#         cleaned = raw.strip().replace("```json", "").replace("```", "")
#         parsed = json.loads(cleaned)
#         return {
#             "score": float(parsed.get("score", -1)),
#             "feedback": parsed.get("feedback", "N/A")
#         }
#     except Exception as e:
#         print(f"[Parse Error] {e} | Raw: {raw}")
#         return {"score": -1, "feedback": "N/A"}


def parse_model_response(raw: str) -> Dict:
    try:
        # --- ADD THIS CHECK ---
        if not raw:
            raise ValueError("No content in API response (None or empty string)")
        # --- END OF CHECK ---
            
        cleaned = raw.strip().replace("```json", "").replace("```", "")
        # Extract first JSON object using regex
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            parsed = json.loads(match.group())
            return {"score": float(parsed.get("score", -1)),
                    "feedback": parsed.get("feedback", "N/A")}
        else:
            raise ValueError("No JSON found in response")
    except Exception as e:
        print(f"[Parse Error] {e} | Raw: {raw}")
        return {"score": -1, "feedback": "N/A"}






# ------------------- Generic Model Caller ------------------- #
def ask_model(client, model: str, question: str, answer: str) -> Dict:
    if not client:
        return {"score": -1, "feedback": "API client missing"}
    try:
        prompt = f"""
Evaluate the student's viva answer (ignore typos).

Context: {st.session_state['test_description']}
Question: {question}
Answer: {answer}

Rubric (0-2 each, sum 0-10):
1. Accuracy - facts correct
2. Coverage - all parts addressed
3. Reasoning - logic/explanation
4. Clarity - clear & structured
5. Terminology - correct terms

Respond strictly:
{{"score": <0-10>, "feedback": "One line feedback"}}
(⚠️ Only final JSON, no breakdown)
"""
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=60,
            temperature=0.3
        )
        raw = resp.choices[0].message.content
        return parse_model_response(raw)
    except Exception as e:
        print(f"[{model} Error] {e}")
        return {"score": -1, "feedback": "N/A"}


# ------------------- Groq Model Caller ------------------- #
def ask_groq_model(client, model: str, question: str, answer: str) -> Dict:
    if not client:
        return {"score": -1, "feedback": "Groq client missing"}
    try:
        prompt = f"""
Evaluate the student's viva answer (ignore typos).

Context: {st.session_state['test_description']}

Question: {question}
Answer: {answer}

Rubric (0-2 each, sum 0-10):
1. Accuracy - facts correct
2. Coverage - all parts addressed
3. Reasoning - logic/explanation
4. Clarity - clear & structured
5. Terminology - correct terms

Respond strictly with JSON only.
Do not include explanations, markdown, <think> tokens, or extra text.
Only output: {{"score": <0-10>, "feedback": "One line feedback"}}
"""
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=100,
            temperature=0.3
        )
        raw = resp.choices[0].message.content
        return parse_model_response(raw)
    except Exception as e:
        print(f"[Groq {model} Error] {e}")
        return {"score": -1, "feedback": "N/A"}



# ... (after your ask_groq_model function) ...

# ------------------- Native Gemini Caller ------------------- #
def ask_gemini_native(client, question: str, answer: str) -> Dict:
    if not client:
        return {"score": -1, "feedback": "Native Gemini client missing"}
    
    prompt = f"""
Evaluate the student's viva answer (ignore typos).

Context: {st.session_state['test_description']}

Question: {question}
Answer: {answer}

Rubric (0-2 each, sum 0-10):
1. Accuracy - facts correct
2. Coverage - all parts addressed
3. Reasoning - logic/explanation
4. Clarity - clear & structured
5. Terminology - correct terms

Respond strictly with JSON only.
Do not include explanations, markdown, <think> tokens, or extra text.
Only output: {{"score": <0-10>, "feedback": "One line feedback"}}
"""
    
    # Configuration to match your 'ask_groq_model' settings
    config = genai.types.GenerationConfig(
        max_output_tokens=100,
        temperature=0.3
    )

    try:
        resp = client.generate_content(
            contents=prompt,
            generation_config=config
        )
        # The native library's response is in 'resp.text'
        return parse_model_response(resp.text)
    except Exception as e:
        print(f"[Native Gemini Error] {e}")
        return {"score": -1, "feedback": "N/A"}





# ------------------- Native Cerebras Caller ------------------- #
# ------------------- Native Cerebras Caller ------------------- #
def ask_cerebras_model(api_key: str, question: str, answer: str) -> Dict:
    if not api_key:
        return {"score": -1, "feedback": "Cerebras API key missing"}

    try:
        # Initialize the client inside the function
        client = Cerebras(api_key=api_key)
        
        # --- PROMPT IS NOW SPLIT INTO ROLES ---
        system_prompt = f"""
Evaluate the student's viva answer (ignore typos).

Context: {st.session_state['test_description']}

Rubric (0-2 each, sum 0-10):
1. Accuracy - facts correct
2. Coverage - all parts addressed
3. Reasoning - logic/explanation
4. Clarity - clear & structured
5. Terminology - correct terms

Respond strictly with JSON only.
Do not include explanations, markdown, <think> tokens, or extra text.
Only output: {{"score": <0-10>, "feedback": "One line feedback"}}
"""
        
        user_prompt = f"""
Question: {question}
Answer: {answer}
"""
        # --- END OF PROMPT SPLIT ---

        resp = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt}, # <--- ADDED SYSTEM ROLE
                {"role": "user", "content": user_prompt}    # <--- USER ROLE IS NOW CLEANER
            ],
            model="qwen-3-235b-a22b-instruct-2507",
            stream=False,
            max_completion_tokens=100,
            temperature=0.3,
            response_format={"type": "json_object"}  # <--- THIS ENFORCES JSON OUTPUT
        )
        
        raw = resp.choices[0].message.content
        return parse_model_response(raw)

    except Exception as e:
        print(f"[Cerebras Error] {e}")
        # Re-raise the exception to be caught by the 'safe_score' wrapper
        raise e




# ------------------- Wrappers ------------------- #



####################################----------------temporary______________############

def safe_deepsk_score(q, a):
    try:
        # Try primary GPT
        # raise Exception("Simulated failure for testing fallback")
        return ask_groq_model(client_deepseek, "moonshotai/kimi-k2-instruct-0905", q, a)
    except Exception as e:
        print(f"[GPT Fallback Triggered] Primary failed: {e}")
        try:
            # Call backup GPT
            res = ask_groq_model(client_2_deepseek, "moonshotai/kimi-k2-instruct-0905", q, a)
            res["fallback_used"] = True
            print("[GPT] Backup model used successfully")
            return res
        except Exception as e2:
            print(f"[GPT Backup Failed] {e2}")
            return {"score": -1, "feedback": "GPT scoring failed", "fallback_used": True}





# # ------------------- Wrappers ------------------- #

# # vvv REPLACE 'safe_deepsk_score' WITH THIS vvv
# def safe_cerebras_score(q, a):
#     """Calls Cerebras gpt-oss-120b with fallback."""
    
#     # --- Try Primary Key ---
#     try:
#         if not GPT_API_KEY:
#             raise Exception("Primary GPT_API_KEY not found")
        
#         # Call the new Cerebras caller function
#         return ask_cerebras_model(GPT_API_KEY, q, a)
    
#     except Exception as e:
#         print(f"[Cerebras Primary Failed] {e}. Trying fallback.")
        
#         # --- Try Fallback Key ---
#         try:
#             if not GPT_API_KEY_ALT:
#                 raise Exception("Fallback CEREBRAS_API_KEY_ALT not found")
            
#             res = ask_cerebras_model(GPT_API_KEY_ALT, q, a)
#             res["fallback_used"] = True
#             print("[Cerebras] Backup key used successfully")
#             return res
        
#         except Exception as e2:
#             print(f"[Cerebras Backup Failed] {e2}")
#             return {"score": -1, "feedback": "Cerebras scoring failed", "fallback_used": True}
# ^^^ END OF REPLACEMENT ^^^

# ... (safe_gemini_score and safe_llama_score functions) ...















# def safe_deepmind_score(q, a):
#     try:
#         # Try primary Claude
#         # raise Exception("Simulated failure for testing fallback")
#         # return ask_groq_model(client_gemma, "gemma2-9b-it", q, a)
#         return ask_groq_model(client_gemma, "openai/gpt-oss-20b", q, a)

#     except Exception as e:
#         print(f"[Claude Fallback Triggered] Primary failed: {e}")
#         try:
#             # Call backup Claude
#             res = ask_groq_model(client_2_gemma, "openai/gpt-oss-20b", q, a)
#             res["fallback_used"] = True
#             print("[Claude] Backup model used successfully")
#             return res
#         except Exception as e2:
#             print(f"[Claude Backup Failed] {e2}")
#             return {"score": -1, "feedback": "Claude scoring failed", "fallback_used": True}




# ------------------- Wrappers ------------------- #

# ... (safe_deepsk_score function) ...

# vvv REPLACE THE OLD safe_gemini_score WITH THIS vvv
def safe_gemini_score(q, a):
    """Calls Gemini 2.5 Flash Lite using the native Google library WITH fallback."""
    
    # --- Try Primary Key ---
    try:
        if not GEMINI_API_KEY:
            raise Exception("Primary GEMINI_API_KEY not found")
        
        # Configure with primary key
        genai.configure(api_key=GEMINI_API_KEY)
        client = genai.GenerativeModel(model_name="gemini-2.5-flash-lite")
        
        # Use the native caller
        return ask_gemini_native(client, q, a)
    
    except Exception as e:
        print(f"[Gemini Primary Failed] {e}. Trying fallback.")
        
        # --- Try Fallback Key ---
        try:
            if not GEMINI_API_KEY_ALT:
                raise Exception("Fallback GEMINI_API_KEY_ALT not found")
            
            # Configure with fallback key
            genai.configure(api_key=GEMINI_API_KEY_ALT)
            client_fallback = genai.GenerativeModel(model_name="gemini-2.5-flash-lite")
            
            res = ask_gemini_native(client_fallback, q, a)
            res["fallback_used"] = True
            print("[Gemini] Backup key used successfully")
            
            # IMPORTANT: Re-configure back to primary key for the next run
            if GEMINI_API_KEY:
                genai.configure(api_key=GEMINI_API_KEY)
            
            return res
        
        except Exception as e2:
            print(f"[Gemini Backup Failed] {e2}")
            # Re-configure back to primary key even if backup fails
            if GEMINI_API_KEY:
                genai.configure(api_key=GEMINI_API_KEY)
            return {"score": -1, "feedback": "Gemini scoring failed", "fallback_used": True}

# ... (safe_llama_score function) ...





def safe_llama_score(q, a):
    try:
        # Try primary Llama
        # raise Exception("Simulated failure for testing fallback")
         return ask_groq_model(client_llama, "llama-3.3-70b-versatile", q, a)
    except Exception as e:
        print(f"[Llama Fallback Triggered] Primary failed: {e}")
        try:
            # Call backup Llama
            res = ask_groq_model(client_groq_2_llama, "llama-3.3-70b-versatile", q, a)
            # Add a flag to indicate fallback was used
            res["fallback_used"] = True
            print("[Llama] Backup model used successfully")
            return res
        except Exception as e2:
            print(f"[Llama Backup Failed] {e2}")
            return {"score": -1, "feedback": "Llama scoring failed", "fallback_used": True}





# ------------------- Single Response Scorer (updated) ------------------- #

def score_single_response(candidate_id: str, question: str, answer: str) -> Dict:
    # gpt_res   = safe_cerebras_score(question, answer)
    kimi_res   = safe_deepsk_score(question, answer)
    

    gemini_res  = safe_gemini_score(question, answer)
    llama_res = safe_llama_score(question, answer)

    valid = [s for s in [kimi_res["score"], gemini_res["score"], llama_res["score"]] if s >= 0]
    avg = round(sum(valid) / len(valid), 2) if valid else -1

    scored = {
        "question": question,
        "answer": answer,
        "kimi_score": kimi_res["score"],
        "gemini_score": gemini_res["score"],
        "llama_3.3_score": llama_res["score"],
        "average_score": avg,
        "kimi_feedback": kimi_res["feedback"],
        "gemini_feedback": gemini_res["feedback"],
        "llama_feedback": llama_res["feedback"],
    }

    # Save into the current attempt directory
    candidate_dir = getattr(st.session_state, "attempt_dir", os.path.join("interviews", candidate_id))
    os.makedirs(candidate_dir, exist_ok=True)

    out = os.path.join(candidate_dir, "scored_responses.json")

    # Append existing or create new
    if os.path.exists(out):
        with open(out, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(scored)

    with open(out, "w") as f:
        json.dump(data, f, indent=4)

    return scored





# ------------------- Orchestrator ------------------- #
def score_all_responses(candidate_id: str) -> Tuple[List[Dict], float, List[Dict]]:
    filepath = os.path.join("interviews", candidate_id, "responses.json")
    if not os.path.exists(filepath):
        print(f"[ERROR] responses.json not found for candidate: {candidate_id}")
        return [], -1.0, []

    with open(filepath, "r") as f:
        responses = json.load(f)

    results_breakdown, QA_pair, all_avg_scores = [], [], []

    for res in responses:
        question = res.get("question", "").strip()
        answer   = res.get("transcript", "").strip()
        if not answer:
            continue

        kimi_res    = safe_deepsk_score(question, answer)
        # gemini_res = gemini_score_response(question, answer)
        gemini_res   = safe_gemini_score(question, answer)
        llama_res  = safe_llama_score(question, answer)


        valid_scores = [s for s in [
            kimi_res["score"], gemini_res["score"], llama_res["score"]
        ] if s >= 0]

        avg = round(sum(valid_scores)/len(valid_scores), 2) if valid_scores else -1
        if avg >= 0:
            all_avg_scores.append(avg)

        results_breakdown.append({
            "question": question,
            "answer": answer,
            "kimi_score": kimi_res["score"],
            # "gemini_1.5_score": gemini_res["score"],
            "gemini_score": gemini_res["score"],
            "llama_3.3_score": llama_res["score"],
            "average_score": avg,
            "kimi_feedback": kimi_res["feedback"],
            # "gemini_feedback": gemini_res["feedback"],
            "gemini_feedback": gemini_res["feedback"],
            "llama_feedback": llama_res["feedback"],
        })

        QA_pair.append({"question": question, "answer": answer})

    # Save breakdown file
    scored_filepath = os.path.join("interviews", candidate_id, "scored_responses.json")
    with open(scored_filepath, "w") as f:
        json.dump(results_breakdown, f, indent=4)

    final_score = round(sum(all_avg_scores)/len(all_avg_scores), 2) if all_avg_scores else -1

    return QA_pair, final_score, results_breakdown

















