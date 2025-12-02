import re
import json
import os
import google.generativeai as genai
from django.conf import settings

# --- CONFIGURATION ---

# Safely attempt to get the key from settings or environment variables
api_key = getattr(settings, 'GEMINI_API_KEY', None) or os.environ.get('GEMINI_API_KEY')

if api_key:
    genai.configure(api_key=api_key)
else:
    print("WARNING: GEMINI_API_KEY not found in settings.py. AI features will fail.")

# --- SHARED PROMPTS & HELPERS ---

def get_grading_prompt():
    """
    Returns the system instruction for the AI.
    Includes logic for scoring, justification, and flagging alternative methods.
    """
    return """
    You are an expert academic grader. Your task is to grade student answers based STRICTLY on the provided Solution Key.

    **CRITICAL - HANDLING DIFFERENT METHODS:**
    - If a student uses a valid academic method that is DIFFERENT from the one in the solution key (e.g., using "Proof by Contradiction" when the key uses "Contrapositive", or a valid alternative algorithm), you must **NOT** assign a score.
    - Set `score_awarded` to `null` (do not use 0).
    - In the `justification`, you MUST write: "The student used a different valid method ([Method Name]). Manual review recommended."

    **Output Format:**
    Return PURE JSON. Do not include markdown formatting.
    Structure:
    {
        "total_score": <sum_of_scores>,
        "graded_questions": [
            {
                "question_number": <int>,
                "score_awarded": <float or null>,
                "max_score": <int (inferred from marking scheme)>, 
                "justification": "<string>",
                "student_answer": "<string (extract text from student doc)>",
                "solution_text": "<string (extract text from solution doc)>",
                "marking_scheme": "<string>"
            }
        ]
    }
    """

def parse_ai_response(response_text):
    """
    Cleans and parses the JSON response from Gemini.
    """
    # Strip markdown code blocks if present
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]

    try:
        result_json = json.loads(response_text.strip())
        
        # Calculate total score safely (treating None/null as 0 for the sum)
        total_score = 0
        for q in result_json.get("graded_questions", []):
            if q.get("score_awarded") is not None:
                total_score += q["score_awarded"]
        
        result_json["total_score"] = total_score
        return result_json["graded_questions"], total_score
    except json.JSONDecodeError:
        return {"error": "Failed to parse AI response"}, 0

# --- TEXT ONLY LOGIC (LEGACY / FAST PATH) ---

def _parse_string_content(text_content):
    """
    Parses text content using regex (for .txt files).
    Robustly handles numbering with either a parenthesis ')' or a period '.'.
    """
    # Strict Regex: Look for a newline (or start of string) followed by digits and a delimiter.
    # This prevents splitting on math like "(2k+1)^2"
    pattern = r'(?=(?:^|\n)\d+[\.\)])'
    
    parts = [p.strip() for p in re.split(pattern, text_content) if p.strip()]
    parsed_data = {}
    
    for part in parts:
        match = re.match(r'(\d+)[\.\)]', part)
        if match:
            question_number = int(match.group(1))
            content = part[len(match.group(0)):].strip()
            parsed_data[question_number] = content
            
    return parsed_data

def create_structured_data(solution_text, student_text):
    solution_data = _parse_string_content(solution_text)
    student_data = _parse_string_content(student_text)
    structured_data = []

    for q_num, sol_content in solution_data.items():
        if "Marking Scheme:" in sol_content:
            sol_text, marking_scheme = sol_content.split("Marking Scheme:", 1)
            marking_scheme = marking_scheme.strip()
        else:
            sol_text = sol_content
            marking_scheme = "No marking scheme provided."

        item = {
            "question_number": q_num,
            "solution_text": sol_text.strip(),
            "marking_scheme": marking_scheme,
            "student_answer": student_data.get(q_num, "No answer provided.")
        }
        structured_data.append(item)

    return structured_data

def grade_text_submission(solution_text, student_text):
    """
    Grades purely text-based submissions using the structured parsing logic.
    """
    structured_data = create_structured_data(solution_text, student_text)
    system_instruction = get_grading_prompt()
    
    # Use specific model version to avoid 404s
    model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=system_instruction)
    
    try:
        response = model.generate_content(json.dumps(structured_data))
        return parse_ai_response(response.text)
    except Exception as e:
        print(f"Error grading text: {e}")
        return {"error": str(e)}, 0

# --- MULTIMODAL LOGIC (PDF/IMAGE SUPPORT) ---

def grade_multimodal_submission(solution_file, student_file):
    """
    Grades submissions where one or both files are PDFs/Images.
    Sends raw file data directly to Gemini.
    """
    if not api_key:
        return {"error": "GEMINI_API_KEY is missing."}, 0

    system_instruction = get_grading_prompt()
    model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=system_instruction)
    
    # Prepare the prompt parts with raw file data
    # Django UploadedFile objects can be read directly
    prompt_parts = [
        "Here are the documents to grade.",
        "DOCUMENT 1: SOLUTION KEY",
        {
            "mime_type": solution_file.content_type,
            "data": solution_file.read()
        },
        "DOCUMENT 2: STUDENT ANSWER SHEET",
        {
            "mime_type": student_file.content_type,
            "data": student_file.read()
        },
        "Please extract the questions, match them, and grade them according to the rules."
    ]

    try:
        response = model.generate_content(prompt_parts)
        return parse_ai_response(response.text)
    except Exception as e:
        print(f"Error grading multimodal: {e}")
        return {"error": str(e)}, 0

# --- MAIN ENTRY POINT ---

def perform_grading(solution_file, student_file):
    """
    Main dispatcher. Checks file types and routes to appropriate logic.
    """
    # Check extensions to decide strategy
    is_text_sol = solution_file.name.lower().endswith('.txt')
    is_text_stud = student_file.name.lower().endswith('.txt')

    if is_text_sol and is_text_stud:
        try:
            # Decode bytes to string for text processing
            sol_text = solution_file.read().decode('utf-8')
            stud_text = student_file.read().decode('utf-8')
            return grade_text_submission(sol_text, stud_text)
        except UnicodeDecodeError:
            # If decoding fails, fallback to multimodal (might be binary disguise)
            solution_file.seek(0)
            student_file.seek(0)
            return grade_multimodal_submission(solution_file, student_file)
    else:
        # If any file is PDF or Image, use Multimodal
        return grade_multimodal_submission(solution_file, student_file)