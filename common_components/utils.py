import cloudinary
import cloudinary.uploader

from dotenv import load_dotenv
import os

load_dotenv()

CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

cloudinary.config(cloud_name=CLOUDINARY_CLOUD_NAME, api_key=CLOUDINARY_API_KEY, api_secret=CLOUDINARY_API_SECRET)


def upload_profile_pic_cloudinary(image_file):
    response = cloudinary.uploader.upload(
        image_file,
        folder="profile_pics",
        allowed_formats=["jpg", "jpeg", "png", "gif", "svg"],
        unique_filename=False,
        overwrite=True,
    )
    return response.get("secure_url", None)


def upload_song_cover_art_pic_cloudinary(image_file):
    response = cloudinary.uploader.upload(
        image_file,
        folder="song_cover_art",
        allowed_formats=["jpg", "jpeg", "png", "gif", "svg"],
        unique_filename=False,
        overwrite=True,
    )
    return response.get("secure_url", None)


def upload_song_file_cloudinary(video_file):
    response = cloudinary.uploader.upload(
        video_file,
        folder="song_files",
        allowed_formats=["mp3"],
        resource_type="video",
        unique_filename=False,
        overwrite=True,
    )
    return response.get("secure_url", None)
