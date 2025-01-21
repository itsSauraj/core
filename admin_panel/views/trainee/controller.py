from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from admin_panel.roles_and_permissions.roles import IsInGroup
from admin_panel.roles_and_permissions.decorators import group_required

from admin_panel.services.trainee.serializer import CreateUserCollectionSerializer, ReportCourseCollectionSerializer
from admin_panel.services.trainee.service import TraineeCourseServices

class TraineeCourseAPIView(APIView):
  def get_permissions(self):
    return [IsAuthenticated(), IsInGroup('Admin')]
    
  def post(self, request):
    
    serializer = CreateUserCollectionSerializer(data=request.data)

    if not serializer.is_valid():
      return Response(serializer.errors, status=400)
    
    for collection in serializer.validated_data['collection']:
      if collection.created_by != request.user:
        return Response({"message": "You can not assign collection of which you are not the owner"}, status=400)
    
    TraineeCourseServices.create(request, serializer.validated_data)
    
    return Response({"message": "Added to collection"}, status=201)
  

  def delete(self, request, collection_id=None):
    if collection_id is None:
      return Response({"message": "Collection ID is required"}, status=400)
    
    status = TraineeCourseServices.delete(request, collection_id)
    if not status:
      return Response({"message": "Collection not found"}, status=404)
    
    return Response(status=204)
  

class TraineeAPIView():

  @staticmethod
  @api_view(['GET'])
  @group_required(['Trainee', 'Admin'])
  def get_all_assigned_collections(request):

    assigned_collections = request.user.enrolled_courses.all()
    return Response(ReportCourseCollectionSerializer(assigned_collections, many=True).data, status=200)