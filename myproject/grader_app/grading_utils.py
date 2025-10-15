# your_app/grading_utils.py

import re
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- (Keep your existing _parse_string_content and create_structured_data functions here) ---

def _parse_string_content(text_content):
    # ... (your existing code)
    pattern = r'(?=\n*\d+\))'
    parts = [p.strip() for p in re.split(pattern, text_content) if p.strip()]
    parsed_data = {}
    for part in parts:
        match = re.match(r'(\d+)\)', part)
        if match:
            question_number = int(match.group(1))
            content = part[len(match.group(0)):].strip()
            parsed_data[question_number] = content
    return parsed_data

def create_structured_data(solution_text, ans_text):
    # ... (your existing code)
    parsed_solutions = _parse_string_content(solution_text)
    parsed_answers = _parse_string_content(ans_text)
    combined_data = []
    for q_num, solution_content in parsed_solutions.items():
        solution_parts = re.split(r'Marking Scheme:', solution_content, flags=re.IGNORECASE)
        sol_text = solution_parts[0].strip()
        marking_scheme = solution_parts[1].strip() if len(solution_parts) > 1 else "No marking scheme provided."
        student_answer = parsed_answers.get(q_num, "No answer provided for this question.")
        combined_data.append({
            "question_number": q_num,
            "solution_text": sol_text,
            "marking_scheme": marking_scheme,
            "student_answer": student_answer
        })
    return combined_data


# --- NEW AI GRADING FUNCTION ---
def grade_answers_with_ai(structured_data):
    """
    Evaluates student answers using the Gemini AI model.
    """
    try:
        # Configure the AI with your API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        genai.configure(api_key=api_key)
        
        # Initialize the generative model
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        
    except Exception as e:
        # Handle cases where the API key is missing or invalid
        print(f"Error configuring AI model: {e}")
        return {"error": str(e)}, 0

    total_score = 0
    graded_results = []

    # This is the instruction template for the AI
    prompt_template = """
    You are an expert AI exam evaluator. Your task is to grade a student's answer based on the provided solution and marking scheme.
    Be strict and follow the marking scheme precisely.

    ---
    **Official Solution:**
    {solution_text}

    **Marking Scheme:**
    {marking_scheme}

    **Student's Answer:**
    {student_answer}
    ---

    Perform the following actions:
    1.  **Analysis:** Compare the student's answer against the solution and marking scheme.
    2.  **Score Calculation:** Award a score based on the marking scheme.
    3.  **Output:** Provide your response ONLY in a valid JSON format with two keys: "score_awarded" (an integer or float) and "justification" (a brief string explaining your reasoning). Do not add any other text outside the JSON structure.
    """

    for question in structured_data:
        # Create a specific prompt for this question
        prompt = prompt_template.format(
            solution_text=question["solution_text"],
            marking_scheme=question["marking_scheme"],
            student_answer=question["student_answer"]
        )

        try:
            # Send the prompt to the AI
            response = model.generate_content(prompt)
            
            # Clean up the response to ensure it's valid JSON
            # Sometimes the model might wrap the JSON in ```json ... ```
            cleaned_response_text = response.text.strip().replace('```json', '').replace('```', '').strip()
            
            # Parse the AI's JSON response
            ai_feedback = json.loads(cleaned_response_text)
            
            # Update the question dictionary with AI feedback
            question['score_awarded'] = ai_feedback.get('score_awarded', 0)
            question['justification'] = ai_feedback.get('justification', 'No justification provided.')
            
            total_score += question['score_awarded']
            
        except (json.JSONDecodeError, AttributeError, Exception) as e:
            # Handle cases where the AI response is not valid JSON or another error occurs
            print(f"Error processing AI response for Q{question['question_number']}: {e}")
            question['score_awarded'] = 0
            question['justification'] = f"Error: Failed to get a valid grade from the AI. ({e})"

        graded_results.append(question)

    return graded_results, total_score