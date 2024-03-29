from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework import status
from tripexpensetrackerapi.models import User

class UserView(ViewSet):
    """View for handling requests for users"""

    def retrieve(self, request, pk):
        """Handle GET request for a single user
        
        Returns -> Response -- JSON serialized user"""
        try:
            user = User.objects.get(pk=pk)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        """Handle GET requests for all users
        
        Returns -> Response -- JSON serialized list of users"""
        try:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
        except User.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        
class UserSerializer(serializers.ModelSerializer):
    """JSON serializer for the User model"""
    class Meta:
        model = User
        fields = ('id', 'name', 'uid')
