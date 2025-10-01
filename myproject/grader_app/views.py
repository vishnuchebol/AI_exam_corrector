from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status

# This class will handle the file upload logic
# Make sure the class name is spelled exactly "GradeView"
class GradeView(APIView):
    # Use MultiPartParser to handle file uploads
    parser_classes = (MultiPartParser,)

    # This 'post' method is called when a POST request is made to this view's URL
    def post(self, request, *args, **kwargs):
        solution_key_file = request.data.get('solutionKey')
        student_sheet_file = request.data.get('studentSheet')

        if not solution_key_file or not student_sheet_file:
            return Response(
                {"error": "Both solutionKey and studentSheet files are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # For now, just print the filenames to the console to confirm receipt
        print(f"Received solution key: {solution_key_file.name}")
        print(f"Received student sheet: {student_sheet_file.name}")
        
        # In the future, OCR and NLP logic will go here.
        
        # Send a success response back to the frontend
        return Response(
            {"message": "Files received successfully. Processing started."},
            status=status.HTTP_200_OK
        )

