from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import UserProfile,SongPopResults
from .serializers import UserProfileSerializer,SongPopResultsSerializer # Create a serializer for UserProfile if not already done

class UserProfileCreateView(APIView):
    permission_classes = [IsAuthenticated]



    def post(self, request, *args, **kwargs):
        # Get the user associated with the bearer token
        user = request.user

        # Check if a user profile already exists
        if hasattr(user, 'userprofile'):
            return Response({'error': 'UserProfile already exists for this user.'}, status=status.HTTP_400_BAD_REQUEST)

        # Extract additional fields from the request if needed
        # For example, you can extract 'gender' and 'dob' fields
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
        
        
        
class SongView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Get the user associated with the bearer token
        user = request.user

        # Retrieve the SongPopResults for the user
        song_results = SongPopResults.objects.filter(user_profile__user=user)

        # Serialize the SongPopResults data
        serializer = SongPopResultsSerializer(song_results, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

