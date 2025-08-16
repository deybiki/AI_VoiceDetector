
import os
import re
import json
import subprocess
# from typing import List, Dict
from typing import List, Dict, Tuple

from retry import retry
from openai import OpenAI 
from dotenv import load_dotenv  # Used for OpenRouter integration

# ------------------- API Key Configuration ------------------- #




# load_dotenv()
load_dotenv(override=True)

LLAMA_API_KEY = os.getenv("LLAMA_API_KEY")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")


if not OPENAI_API_KEY:
    print("[ERROR] OPENAI_API_KEY not found in environment or hardcoded.")
else:
    client_openai = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENAI_API_KEY,
    )

if not GEMINI_API_KEY:
    print("[ERROR] GEMINI_API_KEY not found in environment or hardcoded.")
else:
    client_gemini = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=GEMINI_API_KEY,
    )

if not CLAUDE_API_KEY:
    print("[ERROR] CLAUDE_API_KEY not found.")
else:
    client_claude = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=CLAUDE_API_KEY,
    )

if not LLAMA_API_KEY:
    print("[ERROR] LLAMA_API_KEY not found.")
else:
    client_llama = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=LLAMA_API_KEY,
    )


# ------------------- Utility ------------------- #

def extract_numeric_score(text: str) -> float:
    match = re.search(r"\b(10(?:\.0)?|[0-9](?:\.[0-9])?)\b", text)
    return float(match.group()) if match else -1.0


# ------------------- Scoring Engines ------------------- #

@retry(tries=3, delay=1)
def gpt_score_response(question: str, answer: str) -> float:
    try:
        prompt = f"""
You are evaluating a student's answer in a viva exam ,ingore typo.

Question: {question}
Answer: {answer}

Please provide a numeric score between 0 and 10 (inclusive). Return only the number.
"""
        response = client_openai.chat.completions.create(
            model="openai/gpt-4.1-nano",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2,
            temperature=0.2
        )
        return extract_numeric_score(response.choices[0].message.content.strip())
    except Exception as e:
        print(f"[OpenRouter GPT Error] {e}")
        return -1.0


@retry(tries=3, delay=1)
def gemini_score_response(question: str, answer: str) -> float:
    try:
        prompt = f"""
You are evaluating a student's answer in a viva exam ,ingore typo.

Question: {question}
Answer: {answer}

Provide only a numeric score from 0 to 10.
"""
        response = client_gemini.chat.completions.create(
            model="google/gemini-2.0-flash-exp:free",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2,
            temperature=0.2
        )
        return extract_numeric_score(response.choices[0].message.content.strip())
    except Exception as e:
        print(f"[Gemini via OpenRouter Error] {e}")
        return -1.0


@retry(tries=3, delay=1)
def llama_score_response(question: str, answer: str) -> float:
    try:
        prompt = f"""
You are evaluating a student's answer in a viva exam ,ingore typo.

Question: {question}
Answer: {answer}

Provide only a numeric score from 0 to 10.
"""
        response = client_llama.chat.completions.create(
            model="meta-llama/llama-3.2-3b-instruct:free",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2,
            temperature=0.2
        )
        return extract_numeric_score(response.choices[0].message.content.strip())
    except Exception as e:
        print(f"[Meta/llama via OpenRouter Error] {e}")
        return -1.0


@retry(tries=3, delay=1)
def opus_score_response(question: str, answer: str) -> float:
    try:
        prompt = f"""
You are evaluating a student's answer in a viva exam ,ingore typo.

Question: {question}
Answer: {answer}

Give a numeric score from 0 to 10. Just return the number.
"""
        response = client_claude.chat.completions.create(
            model="anthropic/claude-3-haiku",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2,
            temperature=0.2
        )
        return extract_numeric_score(response.choices[0].message.content.strip())
    except Exception as e:
        print(f"[Claude/Opus Error] {e}")
        return -1.0


# ------------------- Scoring Orchestrator ------------------- #

# llm_scoring.py

# ... (all your other code, like API keys and scoring functions, remains the same) ...


# --- THIS IS THE CORRECTED FUNCTION ---
def score_all_responses(candidate_id: str) -> Tuple[List[Dict], float, List[Dict]]:
    """
    Scores all responses and returns three distinct values:
    1. A simple list of question-answer pairs for the backend.
    2. The final average score for the entire viva.
    3. A detailed JSON-style list with all individual scores for the report card.
    """
    filepath = os.path.join("interviews", candidate_id, "responses.json")
    if not os.path.exists(filepath):
        print(f"[ERROR] responses.json not found for candidate: {candidate_id}")
        return [], -1.0, []

    with open(filepath, "r") as f:
        responses = json.load(f)

    results_breakdown = []
    QA_pair = []  
    all_avg_scores = []

    for res in responses:
        question = res.get("question", "").strip()
        answer = res.get("transcript", "").strip()
        if not answer:
            continue

        # Using placeholder scores for demonstration. Replace with your actual calls.
        # gpt_score, gemini_score, opus_score, llama_score = 9.0, 8.5, 8.0, 8.8

        # llm_scoring.py

        # --- FIX: Use the actual scoring functions ---
        gpt_score = gpt_score_response(question, answer)
        gemini_score = gemini_score_response(question, answer)
        opus_score = opus_score_response(question, answer)
        llama_score = llama_score_response(question, answer)
        # --- END FIX ---



        valid_scores = [s for s in [gpt_score, gemini_score, opus_score, llama_score] if s >= 0]
        average = round(sum(valid_scores) / len(valid_scores), 2) if valid_scores else -1.0
        if average >= 0:
            all_avg_scores.append(average)

        # This is for the detailed report card display
        results_breakdown.append({
            "question": question,
            "answer": answer,
            "gpt_4_score": gpt_score,
            "gemini_1.5_score": gemini_score,
            "opus_4_score": opus_score,
            "llama_3.3_score": llama_score,
            "average_score": average
        })

        # This is the simplified format your backend Answer.js schema expects
        QA_pair.append({  # <--- RENAMED
            "question": question,
            "answer": answer
        })

    scored_filepath = os.path.join("interviews", candidate_id, "scored_responses.json")
    with open(scored_filepath, "w") as f:
        json.dump(results_breakdown, f, indent=4)

    final_score = round(sum(all_avg_scores) / len(all_avg_scores), 2) if all_avg_scores else -1.0

    return QA_pair, final_score, results_breakdown # <--- RENAMED

# ... (the rest of your llm_scoring.py file remains the same) ...







def generate_analysis_responses(candidate_id: str) -> List[Dict]:
    print(f"[DEBUG] generate_analysis_responses triggered for candidate: {candidate_id}")

    filepath = os.path.join("interviews", candidate_id, "responses.json")
    scored_filepath = os.path.join("interviews", candidate_id, "scored_responses.json")
    output_filepath = os.path.join("interviews", candidate_id, "breakdown_results.json")

    if not os.path.exists(filepath):
        print(f"[ERROR] responses.json not found for candidate: {candidate_id}")
        return []

    if not os.path.exists(scored_filepath):
        print(f"[ERROR] scored_responses.json not found. Please score the responses first.")
        return []

    with open(filepath, "r") as f:
        responses = json.load(f)
    with open(scored_filepath, "r") as f:
        scores = json.load(f)

    detailed_feedback = []

    for res, score_obj in zip(responses, scores):
        question = res.get("question", "").strip()
        answer = res.get("transcript", "").strip()
        if not answer:
            continue

        prompt = f"""
You are evaluating a student's answer in a viva exam. Ignore typos.

Question: "{question}"
Answer: "{answer}"

In one short line, provide brief feedback on the quality of the answer.

Respond in this JSON format only:
{{"feedback": "..."}}.
        """.strip()

        result = {
            "gpt_feedback": "N/A",
            "claude_feedback": "N/A",
            "gemini_feedback": "N/A",
            "llama_feedback": "N/A",
            "question": question,
            "answer": answer
        }

        # GPT Feedback
        try:
            gpt_resp = client_openai.chat.completions.create(
                model="openai/gpt-4-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=40,
                temperature=0.4
            )
            raw = gpt_resp.choices[0].message.content.strip().replace("```json", "").replace("```", "")
            parsed = json.loads(raw)
            result["gpt_feedback"] = parsed.get("feedback", "N/A")
        except Exception as e:
            print(f"[GPT Error] {e}")

        # Claude Feedback
        try:
            claude_resp = client_claude.chat.completions.create(
                model="anthropic/claude-sonnet-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=40,
                temperature=0.4
            )
            raw = claude_resp.choices[0].message.content.strip().replace("```json", "").replace("```", "")
            parsed = json.loads(raw)
            result["claude_feedback"] = parsed.get("feedback", "N/A")
        except Exception as e:
            print(f"[Claude Error] {e}")

        # Gemini Feedback
        try:
            gemini_resp = client_gemini.chat.completions.create(
                model="google/gemini-pro-1.5",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=40,
                temperature=0.4
            )
            raw = gemini_resp.choices[0].message.content.strip().replace("```json", "").replace("```", "")
            parsed = json.loads(raw)
            result["gemini_feedback"] = parsed.get("feedback", "N/A")
        except Exception as e:
            print(f"[Gemini Error] {e}")

        # LLaMA Feedback
        try:
            llama_resp = client_llama.chat.completions.create(
                model="meta-llama/llama-3.3-70b-instruct:free",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=40,
                temperature=0.4
            )
            raw = llama_resp.choices[0].message.content.strip().replace("```json", "").replace("```", "")
            parsed = json.loads(raw)
            result["llama_feedback"] = parsed.get("feedback", "N/A")
        except Exception as e:
            print(f"[LLaMA Error] {e}")

        # Now append after all feedback is collected
        detailed_feedback.append({
            **score_obj,
            **result
        })

    with open(output_filepath, "w") as f:
        json.dump(detailed_feedback, f, indent=4)

    print(f"[INFO] Breakdown + feedback saved to {output_filepath}")
    return detailed_feedback



















