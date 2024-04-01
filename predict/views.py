from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import librosa
import numpy as np

class UploadMP3File(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        mp3_file = request.FILES.get('mp3_file')

        if mp3_file:
            # Save the uploaded file
            user_profile = request.user.userprofile
            print(user_profile)
            # mp3_file='/home/ajay/Downloads/Harry Styles - Watermelon Sugar (Official Audio).mp3'
            # popularity_prediction_task = user_profile.popularitypredictiontask_set.create(song_file=mp3_file)
            
            # Process the uploaded audio file
            y, sr = librosa.load(mp3_file, sr=None)  # Load audio file and specify sample rate
            
            # Extract duration
            duration = librosa.get_duration(y=y, sr=sr)

            # Extract other features
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            energy = np.mean(librosa.feature.rms(y=y))
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            danceability = np.mean(onset_env)
            loudness = np.mean(librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max))
            chroma_stft = np.mean(librosa.feature.chroma_stft(y=y, sr=sr))
            valence = np.mean(librosa.feature.chroma_cens(y=y, sr=sr))
            y_harmonic, y_percussive = librosa.effects.hpss(y)
            centroid_harmonic = np.mean(librosa.feature.spectral_centroid(y=y_harmonic, sr=sr))
            centroid_percussive = np.mean(librosa.feature.spectral_centroid(y=y_percussive, sr=sr))
            instrumentalness = centroid_harmonic / centroid_percussive if centroid_percussive != 0 else 0
            acousticness = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
            speechiness = np.mean(librosa.feature.spectral_contrast(y=y, sr=sr))

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