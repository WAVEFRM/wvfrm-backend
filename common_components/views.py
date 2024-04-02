from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from common_components.models import UserProfile
from common_components.serializers import UserProfileSerializer, UserProfileViewSerializer

from common_components.utils import upload_profile_pic_cloudinary, upload_song_file_cloudinary

from dotenv import load_dotenv
import os 
load_dotenv()

CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')

PROFILE_PIC_DEFAULT = os.getenv('PROFILE_PIC_DEFAULT')

class CheckProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_profile_exists = False
        profile_data = {}

        try:
            user_profile = request.user.userprofile
            user_profile_exists = True
            serializer = UserProfileViewSerializer(user_profile)
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
        
        profile_pic_url = None
        if 'profile_pic' in request.FILES:
            profile_pic = request.FILES['profile_pic']
            profile_pic_url = upload_profile_pic_cloudinary(profile_pic)
            
        # Extract additional fields from the request if needed
        gender = request.data.get('gender')
        dob = request.data.get('dob')

        # Create a new UserProfile instance
        user_profile_data = {
            'user': user.id,
            'gender': gender,
            'dob': dob,
            'profile_pic_url': profile_pic_url if profile_pic_url else PROFILE_PIC_DEFAULT,
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
        serializer = UserProfileViewSerializer(user_profile)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class UserProfileEditView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({'error': 'UserProfile does not exist for this user.'}, status=status.HTTP_404_NOT_FOUND)

        # Check if a profile picture is included in the request
        profile_pic_url = user_profile.profile_pic_url
        if 'profile_pic' in request.FILES:
            profile_pic = request.FILES['profile_pic']
            profile_pic_url = upload_profile_pic_cloudinary(profile_pic)

        # Update the profile data including the profile picture URL
        request.data['profile_pic_url'] = profile_pic_url

        serializer = UserProfileSerializer(user_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            # Retrieve the authenticated user
            user = request.user
            # Delete the user
            user.delete()
            return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            # If any exception occurs during the deletion process
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)