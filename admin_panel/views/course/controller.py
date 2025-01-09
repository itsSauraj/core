from rest_framework import status
from rest_framework.response import Response

from rest_framework.views import APIView


class CourseAPIView(APIView):

  def get(self, request):
    return Response(status=status.HTTP_200_OK)

  def post(self, request):
    return Response(status=status.HTTP_201_CREATED)

  def put(self, request):
    return Response(status=status.HTTP_200_OK)

  def delete(self, request):
    return Response(status=status.HTTP_204_NO_CONTENT)