from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from admin_panel.roles_and_permissions.roles import IsInGroup
from admin_panel.roles_and_permissions.decorators import group_required

from admin_panel.services.course.course_collection import CourseCollectionAPIService
from admin_panel.services.examination.service import ExaminationService
from admin_panel.services.examination.serializer import (
  ExamScheduleSerializer, ResponseExamScheduleSerializer
)

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
        created = ExaminationService.create_exam(request.user, serializer.validated_data)
        return Response(ResponseExamScheduleSerializer(created).data, status=201)
      except Exception as e:
        return Response({"message": str(e)}, status=400)
      
    return Response(serializer.errors, status=400)
  
  def get(self, request, exam_id=None):
    if exam_id:
      try:
        exam = ExaminationService.get_exam_by_id(request.user, exam_id)
        return Response(ResponseExamScheduleSerializer(exam).data, status=200)
      except Exception as e:
        return Response({"message": str(e)}, status=400)
    exams = ExaminationService.get_all_exams(request.user)
    serializer = ResponseExamScheduleSerializer(exams, many=True)
    return Response(serializer.data, status=200)
  
  def delete(self, request, exam_id):
    if not exam_id:
      return Response({"message": "Exam id is required"}, status=400)
    try:
      ExaminationService.delete_exam(request.user, exam_id)
      return Response({"message": "Exam deleted successfully"}, status=204)
    except Exception as e:
      return Response({"message": str(e)}, status=400)

  def patch(self, request, exam_id, notify="false"):
    if not exam_id:
      return Response({"message": "Exam id is required"}, status=400)

    notify = notify.lower() == "true"
      
    serializer = ExamScheduleSerializer(data=request.data)
    if serializer.is_valid():
      try:
        updated = ExaminationService.update_exam(request.user, exam_id, serializer.validated_data, notify)
        return Response(ResponseExamScheduleSerializer(updated).data, status=200)
      except Exception as e:
        return Response({"message": str(e)}, status=400)
    return Response(serializer.errors, status=400)