from django.urls import include, path
from .views import GradeView

urlpatterns = [
    # This maps the URL 'grade/' to our GradeView class.
    # The full URL will be /api/grade/
    path('grade/', GradeView.as_view(), name='grade_files'),
]
