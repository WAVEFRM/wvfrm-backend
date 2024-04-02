from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
import librosa
import numpy as np

class UploadMP3File(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        song_file = request.FILES['song_file']
        print(song_file)

        if song_file:
            # Save the uploaded file
            # user_profile = request.user.userprofile
            # print(user_profile)
            # mp3_file='/home/ajay/Downloads/Harry Styles - Watermelon Sugar (Official Audio).mp3'
            # popularity_prediction_task = user_profile.popularitypredictiontask_set.create(song_file=mp3_file)
            
            # Process the uploaded audio file
            y, sr = librosa.load(song_file, sr=None)  # Load audio file and specify sample rate
            
            # Extract duration
            duration = librosa.get_duration(y=y, sr=sr)
            print(duration)

            # Extract other features
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            print('tempo', tempo)
            energy = np.mean(librosa.feature.rms(y=y))
            print('energy', energy)
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            print('onset_env', onset_env)
            danceability = np.mean(onset_env)
            print('danceability', danceability)
            loudness = np.mean(librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max))
            print('loudness', loudness)
            chroma_stft = np.mean(librosa.feature.chroma_stft(y=y, sr=sr))
            print('chroma_stft', chroma_stft)
            valence = np.mean(librosa.feature.chroma_cens(y=y, sr=sr))
            print('valence', valence)
            y_harmonic, y_percussive = librosa.effects.hpss(y)
            print('y_harmonic', y_harmonic)
            centroid_harmonic = np.mean(librosa.feature.spectral_centroid(y=y_harmonic, sr=sr))
            print('centroid_harmonic', centroid_harmonic)
            centroid_percussive = np.mean(librosa.feature.spectral_centroid(y=y_percussive, sr=sr))
            print('centroid_percussive', centroid_percussive)
            instrumentalness = centroid_harmonic / centroid_percussive if centroid_percussive != 0 else 0
            print('instrumentalness', instrumentalness)
            acousticness = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
            print('acousticness', acousticness)
            speechiness = np.mean(librosa.feature.spectral_contrast(y=y, sr=sr))
            print('speechiness', speechiness)

            # Compute repetition score
            onset_times = librosa.frames_to_time(librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr), sr=sr)
            iois = np.diff(onset_times)
            repetition_score = len(iois) / np.sum(iois)

            # You can print or process these features further as needed
            print("Duration:", duration)
            print("Tempo:", tempo)
            print("Energy:", energy)
            print("Danceability:", danceability)
            print("Loudness:", loudness)
            print("Chroma STFT:", chroma_stft)
            print("Valence:", valence)
            print("Instrumentalness:", instrumentalness)
            print("Acousticness:", acousticness)
            print("Speechiness:", speechiness)
            print("Repetition Score:", repetition_score)

            return Response({"message": "MP3 file uploaded successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "No MP3 file provided"}, status=status.HTTP_400_BAD_REQUEST)