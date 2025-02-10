from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from admin_panel.roles_and_permissions.roles import IsInGroup

# from admin_panel.models import Course, CourseCollection, Module, Lesson, User
from admin_panel.services.dashboard.service import DashboardService

class DashboardViewSet(viewsets.ModelViewSet):
	def get_permissions(self):
		return [IsAuthenticated(), IsInGroup('Admin')]
	
	@action(detail=False, methods=['get'])
	def get_report(self, request):
		try:
			return Response(DashboardService.getInfoCardsData(request.user), status=status.HTTP_200_OK)
		except Exception as e:
			return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
	
	@action(detail=False, methods=['get'])
	def get_course_completion_status(self, request):
		try:
			context = DashboardService.getCourseDetails(request.user, call=1)
			# for i in range(2, 10):
			# 	context += DashboardService.getCourseDetails(request.user, call=i)
			return Response(context, status=status.HTTP_200_OK)
		except Exception as e:
			return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
				