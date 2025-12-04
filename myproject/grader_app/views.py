from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from .grading_utils import perform_grading

class GradeView(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request, *args, **kwargs):
        # 1. Get files from the request
        solution_key_file = request.FILES.get('solutionKey')
        # Use getlist to retrieve multiple files for the same key
        student_sheet_files = request.FILES.getlist('studentSheet')

        # 2. Basic Validation
        if not solution_key_file or not student_sheet_files:
            return Response(
                {"error": "Both solutionKey and at least one studentSheet file are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        results = []
        errors = []

        try:
            # 3. Iterate through each student sheet
            for student_file in student_sheet_files:
                # Reset solution file pointer for each iteration if it's read multiple times
                # However, perform_grading might read it. 
                # Ideally, we should read solution once, but perform_grading takes a file object.
                # We need to ensure perform_grading doesn't close it or we seek(0) before reuse.
                # Let's check perform_grading implementation. It does seek(0) in some cases.
                # To be safe, we should seek(0) on solution_key_file before each call.
                solution_key_file.seek(0)
                
                try:
                    graded_data, total_score = perform_grading(solution_key_file, student_file)
                    
                    if "error" in graded_data:
                         errors.append({
                             "filename": student_file.name,
                             "error": graded_data["error"]
                         })
                    else:
                        results.append({
                            "filename": student_file.name,
                            "total_score": total_score,
                            "graded_questions": graded_data
                        })
                except Exception as e:
                    errors.append({
                        "filename": student_file.name,
                        "error": str(e)
                    })

            # 5. Construct final response
            final_response = {
                "results": results,
                "errors": errors,
                "total_processed": len(student_sheet_files),
                "success_count": len(results),
                "error_count": len(errors)
            }
            
            return Response(final_response, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error in GradeView: {e}")
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )