from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from .grading_utils import perform_grading

class GradeView(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request, *args, **kwargs):
        # 1. Get files from the request
        solution_key_file = request.data.get('solutionKey')
        student_sheet_file = request.data.get('studentSheet')

        # 2. Basic Validation
        if not solution_key_file or not student_sheet_file:
            return Response(
                {"error": "Both solutionKey and studentSheet files are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 3. Call the grading logic (handles both Text and PDF/Image internally)
            graded_data, total_score = perform_grading(solution_key_file, student_sheet_file)

            # 4. Check for errors returned by the utility
            if "error" in graded_data:
                return Response(graded_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # 5. Construct success response
            final_response = {
                "total_score": total_score,
                "graded_questions": graded_data
            }
            
            return Response(final_response, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error in GradeView: {e}")
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )