# notifications/views.py
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

	def get_queryset(self):
		pass
	
	@action(detail=False, methods=['get'])
	def get_report(self, request):
		context = {
			'info_cards': DashboardService.getInfoCardsData(request.user)
		}

		return Response(context, status=status.HTTP_200_OK)
				