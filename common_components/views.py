from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from common_components.models import UserProfile
from common_components.serializers import UserProfileSerializer


class CheckProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_profile_exists = False
        profile_data = {}

        try:
            user_profile = request.user.userprofile
            user_profile_exists = True
            serializer = UserProfileSerializer(user_profile)
            profile_data = serializer.data
        except UserProfile.DoesNotExist:
            pass

        return Response({
            'has_profile': user_profile_exists,
            'user_profile': profile_data
        }, status=status.HTTP_200_OK)


class UserProfileCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Get the user associated with the bearer token
        user = request.user
        
        # Check if a user profile already exists
        if hasattr(user, 'userprofile'):
            return Response({'error': 'UserProfile already exists for this user.'}, status=status.HTTP_409_CONFLICT)

        # Extract additional fields from the request if needed
        gender = request.data.get('gender')
        dob = request.data.get('dob')

        # Create a new UserProfile instance
        user_profile_data = {
            'user': user.id,
            'gender': gender,
            'dob': dob,
        }

        serializer = UserProfileSerializer(data=user_profile_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Get the user associated with the bearer token
        user = request.user

        # Check if a user profile exists
        if not hasattr(user, 'userprofile'):
            return Response({'error': 'UserProfile does not exist for this user.'}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve the user profile
        user_profile = user.userprofile

        # Serialize the user profile data
        serializer = UserProfileSerializer(user_profile)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class UserProfileEditView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({'error': 'UserProfile does not exist for this user.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserProfileSerializer(user_profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
