# AI Exam Corrector

An AI-powered automated grading system that uses Google's Gemini API to evaluate student answer sheets against a solution key. It supports both text-based and image-based (handwritten) submissions.

## Features

- **Multimodal Grading:** Grades both text files (.txt) and handwritten images/PDFs.
- **Context-Aware Evaluation:** Uses Gemini 2.5 Flash to understand logic and semantics, not just keyword matching.
- **Partial Scoring:** Awards partial marks for correct steps based on the provided marking scheme.
- **Batch Processing:** Can process multiple student answer sheets in a single batch.
- **Detailed Feedback:** Provides justification for every score awarded.

## Prerequisites

- Python 3.8+
- A Google Gemini API Key

## Installation & Setup

1.  **Navigate to the project directory:**

    ```bash
    cd /path/to/AI_exam_corrector
    ```

2.  **Activate the Virtual Environment:**

    ```bash
    source venv/bin/activate
    ```

    _(If you don't have one, create it: `python3 -m venv venv` and install dependencies)_

3.  **Install Dependencies:**
    The project requires the following packages:

    ```bash
    pip install django djangorestframework django-cors-headers google-generativeai python-dotenv
    ```

4.  **Set up Environment Variables:**

    - Create a `.env` file in `myproject/` or set the variable in your shell.
    - You must have `GEMINI_API_KEY` set.

    ```bash
    export GEMINI_API_KEY="your_api_key_here"
    ```

5.  **Run the Backend Server:**
    ```bash
    cd myproject
    python manage.py runserver
    ```
    The server will start at `http://127.0.0.1:8000/`.

## Usage

1.  **Open the Frontend:**

    - Locate `ai_grader.html` in the root directory.
    - Open it in any modern web browser (Chrome, Safari, etc.).

2.  **Upload Files:**

    - **Solution Key:** Upload your `solution_key.txt` or `.png`/`.pdf`.
    - **Student Sheets:** Upload one or more student answer files (`.txt`, `.png`, `.jpg`, `.pdf`).

3.  **Start Grading:**
    - Click the "Grade Exams" button.
    - The results will appear in the table below, showing scores and a detailed breakdown.

## Test Data

Sample test data is available in the `test_data` directory:

- `test_data/test_data_text/`: Contains text-based test cases.
- `test_data/test_data_image/`: Contains image-based test cases (handwritten samples).

You can use these files to test the system's functionality.
