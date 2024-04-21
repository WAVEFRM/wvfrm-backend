from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny

from predict.models import PopularityPredictionTask
from predict.serializers import PopularityPredictionTaskSerializer
from common_components.utils import upload_profile_pic_cloudinary, upload_song_file_cloudinary
from django.core.files.base import ContentFile

from io import BytesIO

import threading
import librosa
import numpy as np
import joblib

from dotenv import load_dotenv
import os

load_dotenv()

CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

PROFILE_PIC_DEFAULT = os.getenv("PROFILE_PIC_DEFAULT")


class CustomPagination(PageNumberPagination):
    page_size = 10  # Set the default page size
    max_page_size = 50  # Set the maximum page size
    page_size_query_param = "page_size"  # Set the query parameter name for page size

    def get_paginated_response(self, data):
        return Response(
            {
                "nextPage": self.page.number + 1 if self.page.has_next() else None,
                "totalPages": self.page.paginator.num_pages,
                "totalCount": self.page.paginator.count,
                "pageCount": len(data),
                "data": data,
            }
        )


# class PopularityPredictionTaskListView(APIView):
#     permission_classes = [IsAuthenticated]
#     pagination_class = CustomPagination

#     def get(self, request):
#         try:
#             # Get the user profile associated with the authenticated user
#             user_profile = request.user.userprofile
#         except AttributeError:
#             return Response({"error": "UserProfile does not exist for this user."}, status=status.HTTP_404_NOT_FOUND)

#         # Retrieve all PopularityPredictionTask instances related to the user profile
#         tasks = PopularityPredictionTask.objects.filter(user_profile=user_profile)

#         # Paginate the queryset
#         paginator = CustomPagination()
#         result_page = paginator.paginate_queryset(tasks, request)

#         # Serialize the paginated queryset
#         serializer = PopularityPredictionTaskSerializer(result_page, many=True)

#         return paginator.get_paginated_response(serializer.data)


class PopularityPredictionTaskListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get the user profile associated with the authenticated user
            user_profile = request.user.userprofile
        except AttributeError:
            return Response({"error": "UserProfile does not exist for this user."}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve all PopularityPredictionTask instances related to the user profile
        tasks = PopularityPredictionTask.objects.filter(user_profile=user_profile)

        # Serialize the queryset
        serializer = PopularityPredictionTaskSerializer(tasks, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class LowLevelPredictionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get the user associated with the bearer token
        user = request.user

        # Check if a user profile exists
        if not hasattr(user, "userprofile"):
            return Response({"error": "UserProfile does not exist for this user."}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve the user profile
        user_profile = user.userprofile

        song_name = request.data.get("song_name")

        explicit = int(request.data.get("explicit", 0))

        # Check if the file exists in the request
        if "song_file" not in request.FILES:
            return Response({"error": "No file was uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate the file type
        song_file = request.FILES["song_file"]
        if not song_file.name.lower().endswith(".mp3"):
            return Response(
                {"error": "Invalid file format. Please upload an mp3 file"}, status=status.HTTP_400_BAD_REQUEST
            )
        print(song_file)

        # song_file_copy = ContentFile(song_file.read())
        # song_file_copy.name = song_file.name

        try:

            y, sr = librosa.load(song_file, sr=None)  # Load audio file and specify sample rate
        except:
            return Response({"error": "Format not recognised"}, status=status.HTTP_400_BAD_REQUEST)

        print("checkpoint")

        # Extract duration
        # duration = librosa.get_duration(y=y, sr=sr)
        # print(duration)

        song_art_cover_url = PROFILE_PIC_DEFAULT
        if "song_art_cover" in request.FILES:
            song_art_cover = request.FILES["song_art_cover"]
            song_art_cover_url = upload_profile_pic_cloudinary(song_art_cover)

        print(song_art_cover_url)

        # song_file = request.FILES["song_file1"]
        # if not song_file.name.lower().endswith(".mp3"):
        #     return Response(
        #         {"error": "Invalid file format. Please upload an mp3 file"}, status=status.HTTP_400_BAD_REQUEST
        #     )
        # print(song_file)

        song_file.seek(0)

        song_file_content = song_file.read()

        # print(song_file_content)

        try:
            # Create the task with status pending
            # task_instance = PopularityPredictionTask.objects.create(user_profile=user_profile, status="pending")

            task_instance = PopularityPredictionTask.objects.create(
                user_profile=user_profile, song_name=song_name, song_cover_art_url=song_art_cover_url, status="pending"
            )

            # Serialize the task data
            serializer = PopularityPredictionTaskSerializer(task_instance)

            # Start the analysis task thread
            analysis_thread = threading.Thread(
                target=self.run_analysis_thread,
                args=(user_profile, task_instance, song_file_content, song_file, y, sr, explicit),
                daemon=True,
            )
            analysis_thread.start()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def run_analysis_thread(self, user_profile, task_instance, song_file_content, song_file, y, sr, explicit):
        try:
            print("Starting Analysis")

            try:
                model = joblib.load("predict/models/adaboost_model_low_level.pkl")
                print(model)
            except FileNotFoundError:
                return Response({"error": "Model file not found"}, status=status.HTTP_404_NOT_FOUND)

            print("Uploading song file to Cloudinary")

            # print(song_file_content)

            response = upload_song_file_cloudinary(song_file_content)
            print("Song URL : ", response)
            if response is not None:
                task_instance.song_file_url = response
                task_instance.save()
                print("Task updated successfully")

            # print(song_file)
            # y, sr = librosa.load(song_file, sr=None)
            # duration = librosa.get_duration(y=y, sr=sr)
            # print(duration)

            duration = librosa.get_duration(y=y, sr=sr)
            print(duration)

            # Extract other features
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            print("tempo", tempo)
            energy = np.mean(librosa.feature.rms(y=y))
            print("energy", energy)
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            print("onset_env", onset_env)
            danceability = np.mean(onset_env)
            print("danceability", danceability)
            loudness = np.mean(librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max))
            print("loudness", loudness)
            chroma_stft = np.mean(librosa.feature.chroma_stft(y=y, sr=sr))
            print("chroma_stft", chroma_stft)
            valence = np.mean(librosa.feature.chroma_cens(y=y, sr=sr))
            print("valence", valence)
            y_harmonic, y_percussive = librosa.effects.hpss(y)
            print("y_harmonic", y_harmonic)
            centroid_harmonic = np.mean(librosa.feature.spectral_centroid(y=y_harmonic, sr=sr))
            print("centroid_harmonic", centroid_harmonic)
            centroid_percussive = np.mean(librosa.feature.spectral_centroid(y=y_percussive, sr=sr))
            print("centroid_percussive", centroid_percussive)
            instrumentalness = centroid_harmonic / centroid_percussive if centroid_percussive != 0 else 0
            print("instrumentalness", instrumentalness)
            acousticness = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
            print("acousticness", acousticness)
            speechiness = np.mean(librosa.feature.spectral_contrast(y=y, sr=sr))
            print("speechiness", speechiness)

            # Compute repetition score
            # onset_times = librosa.frames_to_time(librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr), sr=sr)
            # iois = np.diff(onset_times)
            # repetition_score = len(iois) / np.sum(iois)

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

            album_release_date = 2024.0  ## as of now the model assumes the release_date as today , it is used in the trained model (good enough co-relation)

            X_new = [
                [
                    tempo,
                    energy,
                    danceability,
                    loudness,
                    chroma_stft,
                    valence,
                    instrumentalness,
                    acousticness,
                    speechiness,
                    album_release_date,
                    explicit,
                ]
                # Replace tempo, energy, ... with your actual feature values
            ]

            predictions = model.predict(X_new)
            print("predictions")
            print(predictions[0])
            predicted_popularity = predictions[0]

            print("Problems")

            print(valence)
            print(type(tempo))
            print(type(energy))
            print(type(danceability))
            print(type(loudness))
            print(type(chroma_stft))
            print(type(valence))
            print(energy)

            print("problems")

            energy_float64 = np.float64(energy)
            danceability_float64 = np.float64(danceability)
            loudness_float64 = np.float64(loudness)
            chroma_stft_float64 = np.float64(chroma_stft)
            valence_float64 = np.float64(valence)

            task_instance.status = "completed"
            task_instance.result = {
                "duration": duration,
                "tempo": tempo,
                "energy": energy_float64,
                "danceability": danceability_float64,
                "loudness": loudness_float64,
                "chroma_stft": chroma_stft_float64,
                "valence": valence_float64,
                "instrumentalness": instrumentalness,
                "acousticness": acousticness,
                "speechiness": speechiness,
                "explicit": explicit,
                "predicted_popularity": predicted_popularity,
            }
            task_instance.save()

            print("Ending Analysis")
        except Exception as e:
            if task_instance is not None:
                task_instance.status = "failed"
                task_instance.save()
            print("Error in async_analysis_helper:", e)


class HighLevelPredictionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get the user associated with the bearer token
        user = request.user

        # Check if a user profile exists
        if not hasattr(user, "userprofile"):
            return Response({"error": "UserProfile does not exist for this user."}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve the user profile
        user_profile = user.userprofile

        # Load the model
        try:
            model = joblib.load("predict/models/model.pkl")
            print(model)
        except FileNotFoundError:
            return Response({"error": "Model file not found"}, status=status.HTTP_404_NOT_FOUND)

        # Extract data from the request
        data = request.data
        print(data)
        keys = [
            "acousticness",
            "danceability",
            "duration_ms",
            "energy",
            "explicit",
            "instrumentalness",
            "liveness",
            "loudness",
            "speechiness",
            "tempo",
            "valence",
            "year",
            "key_1",
            "key_2",
            "key_3",
            "key_4",
            "key_5",
            "key_6",
            "key_7",
            "key_8",
            "key_9",
            "key_10",
            "key_11",
            "mode",
            "acousticness_ar",
            "danceability_ar",
            "duration_ms_ar",
            "energy_ar",
            "instrumentalness_ar",
            "liveness_ar",
            "loudness_ar",
            "speechiness_ar",
            "tempo_ar",
            "valence_ar",
            "popularity_ar",
        ]

        # Validate if all required keys are present in the request
        for key in keys:
            if key not in data:
                return Response(
                    {"error": f"Key '{key}' not found in request data"}, status=status.HTTP_400_BAD_REQUEST
                )

        # Make prediction
        try:
            prediction = model.predict([[float(data[key]) for key in keys]])
            output = prediction[0]
            return Response({"output": output}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Prediction failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class UploadMP3File(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):


#         if 'song_file' not in request.FILES:
#             return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

#         song_file = request.FILES['song_file']

#         # Check the file name
#         if not song_file.name.endswith('.mp3'):
#             return Response({"error": "Invalid file format. Please upload an MP3 file"}, status=status.HTTP_400_BAD_REQUEST)


#         if song_file:
#             # Save the uploaded file
#             # user_profile = request.user.userprofile
#             # print(user_profile)
#             # mp3_file='/home/ajay/Downloads/Harry Styles - Watermelon Sugar (Official Audio).mp3'
#             # popularity_prediction_task = user_profile.popularitypredictiontask_set.create(song_file=mp3_file)

#             # Process the uploaded audio file
#             y, sr = librosa.load(song_file, sr=None)  # Load audio file and specify sample rate

#             # Extract duration
#             duration = librosa.get_duration(y=y, sr=sr)
#             print(duration)

#             # Extract other features
#             tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
#             print('tempo', tempo)
#             energy = np.mean(librosa.feature.rms(y=y))
#             print('energy', energy)
#             onset_env = librosa.onset.onset_strength(y=y, sr=sr)
#             print('onset_env', onset_env)
#             danceability = np.mean(onset_env)
#             print('danceability', danceability)
#             loudness = np.mean(librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max))
#             print('loudness', loudness)
#             chroma_stft = np.mean(librosa.feature.chroma_stft(y=y, sr=sr))
#             print('chroma_stft', chroma_stft)
#             valence = np.mean(librosa.feature.chroma_cens(y=y, sr=sr))
#             print('valence', valence)
#             # y_harmonic, y_percussive = librosa.effects.hpss(y)
#             # print('y_harmonic', y_harmonic)
#             # centroid_harmonic = np.mean(librosa.feature.spectral_centroid(y=y_harmonic, sr=sr))
#             # print('centroid_harmonic', centroid_harmonic)
#             # centroid_percussive = np.mean(librosa.feature.spectral_centroid(y=y_percussive, sr=sr))
#             # print('centroid_percussive', centroid_percussive)
#             # instrumentalness = centroid_harmonic / centroid_percussive if centroid_percussive != 0 else 0
#             # print('instrumentalness', instrumentalness)
#             acousticness = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
#             print('acousticness', acousticness)
#             speechiness = np.mean(librosa.feature.spectral_contrast(y=y, sr=sr))
#             print('speechiness', speechiness)

#             # Compute repetition score
#             # onset_times = librosa.frames_to_time(librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr), sr=sr)
#             # iois = np.diff(onset_times)
#             # repetition_score = len(iois) / np.sum(iois)

#             # You can print or process these features further as needed
#             print("Duration:", duration)
#             print("Tempo:", tempo)
#             print("Energy:", energy)
#             print("Danceability:", danceability)
#             print("Loudness:", loudness)
#             print("Chroma STFT:", chroma_stft)
#             print("Valence:", valence)
#             # print("Instrumentalness:", instrumentalness)
#             print("Acousticness:", acousticness)
#             print("Speechiness:", speechiness)
#             # print("Repetition Score:", repetition_score)

#             return Response({"message": "MP3 file uploaded successfully"}, status=status.HTTP_201_CREATED)
#         else:
#             return Response({"error": "No MP3 file provided"}, status=status.HTTP_400_BAD_REQUEST)
