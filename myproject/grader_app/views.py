import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status

# Import the parsing function from your utility file
from .grading_utils import create_structured_data
from .grading_utils import grade_answers_with_ai

# This class handles the file upload and processing logic
class GradeView(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request, *args, **kwargs):
        solution_key_file = request.data.get('solutionKey')
        student_sheet_file = request.data.get('studentSheet')

        # 1. Validate that both files were provided
        if not solution_key_file or not student_sheet_file:
            return Response(
                {"error": "Both solutionKey and studentSheet files are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 2. Read the content of the uploaded files and decode them into text
            solution_text = solution_key_file.read().decode('utf-8')
            student_text = student_sheet_file.read().decode('utf-8')

            # 3. Call the utility function to parse the text into structured data
            structured_data = create_structured_data(solution_text, student_text)

            # 4. Print the final structured data to the terminal for debugging
            print("--- PARSED AND STRUCTURED DATA ---")
            print(json.dumps(structured_data, indent=2)) # Using json.dumps for pretty printing
            print("----------------------------------")
            
            graded_data, total_score = grade_answers_with_ai(structured_data)
            
            # If there was an error during AI processing, it will be in the graded_data
            if "error" in graded_data:
                return Response(graded_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Step 3: Prepare the final response payload
            final_response = {
                "total_score": total_score,
                "graded_questions": graded_data
            }
            
            # Print the final result to the terminal for verification
            print("--- FINAL GRADED RESPONSE ---")
            print(json.dumps(final_response, indent=2))
            print("-----------------------------")

            return Response(final_response, status=status.HTTP_200_OK)
            # 5. Return the parsed data in the API response

        except Exception as e:
            # Handle any potential errors during file reading or parsing
            print(f"An error occurred: {e}") # This logs the actual error to your terminal
            return Response(
                {"error": "Failed to read or process the uploaded files."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )