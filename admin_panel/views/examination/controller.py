from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from admin_panel.roles_and_permissions.roles import IsInGroup
from admin_panel.roles_and_permissions.decorators import group_required

from admin_panel.services.course.course_collection import CourseCollectionAPIService
from admin_panel.services.examination.service import ExaminationService
from admin_panel.services.examination.serializer import ExamScheduleSerializer

class ExaminationAPIView(APIView):
  def get_permissions(self):
    if self.request.method in ['POST', 'DELETE', 'PATCH']:
      return [IsAuthenticated(), IsInGroup('Admin')]
    else:
      return [IsAuthenticated()]

  def post(self, request):
    serializer = ExamScheduleSerializer(data=request.data)
    if serializer.is_valid():
      try:
        ExaminationService.create_exam(request.user, serializer.validated_data)
      except Exception as e:
        return Response({"message": str(e)}, status=400)
      
    return Response(serializer.errors, status=400)