import re
import json
import os
import google.generativeai as genai
from django.conf import settings

# Configure the Gemini API
# Safely attempt to get the key from settings or environment variables
api_key = getattr(settings, 'GEMINI_API_KEY', None) or os.environ.get('GEMINI_API_KEY')

if api_key:
    genai.configure(api_key=api_key)
else:
    print("WARNING: GEMINI_API_KEY not found in settings.py or environment variables. AI features will fail.")

def _parse_string_content(text_content):
    """
    Parses the text content of either the solution or answer file.
    Handles numbering with either a parenthesis ')' or a period '.'.
    """
    # FIX 1: STRICTER REGEX
    # Changed \n* (zero or more) to \n (required newline) to prevent splitting 
    # on numbers inside math equations like "(2k + 1)^2".
    # The (?:^|\n) handles both the start of the file OR a newline.
    pattern = r'(?=(?:^|\n)\d+[\.\)])'
    
    parts = [p.strip() for p in re.split(pattern, text_content) if p.strip()]
    parsed_data = {}
    
    for part in parts:
        # Match the number at the start of the chunk
        match = re.match(r'(\d+)[\.\)]', part)
        if match:
            question_number = int(match.group(1))
            content = part[len(match.group(0)):].strip()
            parsed_data[question_number] = content
            
    return parsed_data

def create_structured_data(solution_text, student_text):
    """
    Combines solution key and student answers into a structured list.
    """
    solution_data = _parse_string_content(solution_text)
    student_data = _parse_string_content(student_text)

    structured_data = []

    # Iterate through questions found in the solution key
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

def grade_answers_with_ai(structured_data):
    """
    Sends the structured data to Gemini for grading with specific instructions
    to flag alternative valid methods.
    """
    if not api_key:
        return {"error": "GEMINI_API_KEY is missing. Please add it to settings.py."}, 0
    
    system_instruction = """
    You are an expert academic grader. Your task is to grade student answers based STRICTLY on the provided Solution Key and Marking Scheme.

    **Input Data:**
    You will receive a JSON list of questions. Each item contains:
    - `question_number`: The ID of the question.
    - `solution_text`: The correct answer/solution.
    - `marking_scheme`: The rules for assigning marks (including the total marks available).
    - `student_answer`: The answer written by the student.

    **Grading Rules:**
    1. **Analyze:** Compare the `student_answer` against the `solution_text` and `marking_scheme`.
    2. **Score:** Assign a score based on how many points from the marking scheme were satisfied.
    3. **Justify:** Provide a brief explanation for the score awarded.
    
    **CRITICAL - HANDLING DIFFERENT METHODS:**
    - If a student uses a valid academic method that is DIFFERENT from the one in the solution key (e.g., using "Proof by Contradiction" when the key uses "Contrapositive", or a different valid formula), you must **NOT** assign a score.
    - In this specific case, set `score_awarded` to `null` (or None).
    - In the `justification`, you MUST write: "The student used a different valid method ([Method Name]). Manual review recommended."

    **Output Format:**
    Return PURE JSON. Do not include markdown formatting (like ```json).
    The structure must be:
    {
        "total_score": <sum of all scores (treat null as 0 for sum)>,
        "graded_questions": [
            {
                "question_number": <int>,
                "score_awarded": <float or null>,
                "max_score": <int (extracted from marking scheme)>, 
                "justification": "<string>",
                "student_answer": "<string>",
                "solution_text": "<string>",
                "marking_scheme": "<string>"
            },
            ...
        ]
    }
    """

    # FIX 2: UPDATED MODEL NAME
    # Switched to 'gemini-1.5-flash-latest' to resolve the 404 error.
    # If this still fails, try 'gemini-pro'.
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash", 
        system_instruction=system_instruction
    )

    try:
        response = model.generate_content(json.dumps(structured_data))
        response_text = response.text

        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        result_json = json.loads(response_text.strip())
        
        total_score = 0
        for q in result_json.get("graded_questions", []):
            if q.get("score_awarded") is not None:
                total_score += q["score_awarded"]
        
        result_json["total_score"] = total_score

        return result_json["graded_questions"], total_score

    except Exception as e:
        print(f"Error calling AI: {e}")
        return {"error": str(e)}, 0