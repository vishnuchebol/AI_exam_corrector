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

        # Check if both files were provided
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

