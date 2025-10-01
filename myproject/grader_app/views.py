from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status

# This class handles the file upload logic.
# The name must be exactly "GradeView".
class GradeView(APIView):
    # This parser allows the view to handle file uploads
    parser_classes = (MultiPartParser,)

    # This method is called when a POST request is sent to this URL
    def post(self, request, *args, **kwargs):
        solution_key_file = request.data.get('solutionKey')
        student_sheet_file = request.data.get('studentSheet')

        # Check if both files were providedfrom rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status

# This class handles the file upload and processing logic.
class GradeView(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request, *args, **kwargs):
        solution_key_file = request.data.get('solutionKey')
        student_sheet_file = request.data.get('studentSheet')

        if not solution_key_file or not student_sheet_file:
            return Response(
                {"error": "Both solutionKey and studentSheet files are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # --- NEW LOGIC STARTS HERE ---

            # Read the binary content of the files
            solution_bytes = solution_key_file.read()
            student_bytes = student_sheet_file.read()

            # Decode the bytes into a UTF-8 string. This converts the file content into readable text.
            solution_text = solution_bytes.decode('utf-8')
            student_text = student_bytes.decode('utf-8')

            # Print the extracted text to the Django terminal for verification
            print("--- SOLUTION KEY CONTENT ---")
            print(solution_text)
            print("---------------------------\n")

            print("--- STUDENT SHEET CONTENT ---")
            print(student_text)
            print("----------------------------\n")

            # --- NEW LOGIC ENDS HERE ---
            
            # Send a success message back to the frontend
            return Response(
                {"message": "Files received and text content extracted successfully."},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            # Handle potential errors during file reading or decoding
            print(f"An error occurred: {e}")
            return Response(
                {"error": "Failed to read or process the uploaded files."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


        if not solution_key_file or not student_sheet_file:
            return Response(
                {"error": "Both solutionKey and studentSheet files are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # At this stage, we just confirm the files were received.
        # The actual AI processing logic will be added here later.
        print(f"Received solution key: {solution_key_file.name}")
        print(f"Received student sheet: {student_sheet_file.name}")
        
        # Send a success message back to the frontend
        return Response(
            {"message": "Files received successfully by the Django backend."},
            status=status.HTTP_200_OK
        )

