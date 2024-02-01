from django.conf import settings
from .secret import GOOGLE_API_KEY, OPENAI_API_KEY
import os
import moviepy.editor as mp
from pytube import *

import googleapiclient.discovery
import googleapiclient.errors

from openai import OpenAI


class CloudVision:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'youtube/credentials.json'
    
    def detect_text(self, path):
        from google.cloud import vision

        client = vision.ImageAnnotatorClient()

        with open(path, "rb") as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        response = client.text_detection(image=image)
        texts = response.text_annotations

        output_string = ''
        for text in texts:
            # output_string += f'"{text.description}"\n'
            output_string += text.description
            # vertices = [
            #     f"({vertex.x},{vertex.y})" for vertex in text.bounding_poly.vertices
            # ]
            #
            # output_string += "bounds: {}\n".format(",".join(vertices))
        return output_string

        if response.error.message:
            raise Exception(
                "{}\nFor more info on error messages, check: "
                "https://cloud.google.com/apis/design/errors".format(response.error.message)
            )


class OpenAPI:
    client = OpenAI(api_key=OPENAI_API_KEY)

    def text_to_speech(self, text):
        speech_file_path = os.path.join(settings.MEDIA_ROOT, "speech.mp3")
        response = self.client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        response.stream_to_file(speech_file_path)
        return speech_file_path

    def speech_to_text(self, url):
        audio_file = open(url, 'rb')
        transcript = self.client.audio.transcriptions.create(
            model='whisper-1',
            file=audio_file
        )
        return transcript.text

    def english_to_spanish(self, text):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You will be provided with a text in some language, and your task is to translate it into Spanish."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0.7,
            max_tokens=64,
            top_p=1
        )
        text = response.choices[0].message.content
        return text


class VideoDownloader:
    def download_video(self, url, output_directory):
        yt = YouTube(url)
        ys = yt.streams.filter(only_audio=False).first()
        video_output_path = os.path.join(output_directory, "video.mp4")  # Set the output file path
        ys.download(output_path=output_directory, filename="video.mp4")  # Specify the filename with .mp4 extension
        return video_output_path  # Return the full path to the downloaded video

    # Function to convert video to MP3
    def video_to_mp3(self, video_path, mp3_path, target_fps=30):
        audio_clip = mp.AudioFileClip(video_path)
        audio_clip.write_audiofile(mp3_path)


class VideoGetter:

    def clean_id(self, url):
        if 'v=' in url:
            trimurl = url.split('v=')[1]
            vid_id = trimurl[:11]
        else:
            trimurl = url.replace('https://youtu.be/', '')
            vid_id = trimurl[:11]

        return vid_id

    def get_comment(self, vid_id):

        # Prepare API
        api_service_name = settings.API_SERVICE_NAME
        api_version = settings.API_VERSION
        developer_key = GOOGLE_API_KEY

        youtube = googleapiclient.discovery.build(
            api_service_name,
            api_version,
            developerKey=developer_key
        )

        comment_thread_request = youtube.commentThreads().list(
            part="snippet",
            videoId=vid_id,
            maxResults=1
        )

        comment_thread_response = comment_thread_request.execute()

        # item = comment_thread_response["items"][0]

        comment = ''

        for item in comment_thread_response["items"]:
            cmt = item['snippet']['topLevelComment']['snippet']
            comment = cmt['textDisplay']

        return comment

    def get_video(self, vid_id):

        # Prepare API
        api_service_name = settings.API_SERVICE_NAME
        api_version = settings.API_VERSION
        developer_key = GOOGLE_API_KEY

        youtube = googleapiclient.discovery.build(
            api_service_name,
            api_version,
            developerKey=developer_key
        )

        video_request = youtube.videos().list(
            part="contentDetails,snippet,statistics,player",
            id=vid_id
        )

        video_response = video_request.execute()

        item = video_response["items"][0]

        return item
