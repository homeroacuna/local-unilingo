from django.shortcuts import render
from django.views import View
from youtube.models import *
from .forms import VideoForm
from pydub import AudioSegment
import requests

from .mixins import *

import os

from PIL import Image
import pytesseract


class HomeView(View):
    template_name = 'youtube/home.html'
    form = VideoForm
    video_getter = VideoGetter()
    video_downloader = VideoDownloader()

    def get(self, request):
        form = self.form

        # Get data from DB
        lastVideo = Videos.objects.all().last()
        lastURL = lastVideo.url
        lastAudio = lastVideo.audio.url
        spanish_text = lastVideo.spanish_text
        lastSpeech = lastVideo.speech.url
        thumbnail = lastVideo.thumbnail.url
        ocr = lastVideo.ocr

        # Get video
        vid_id = self.video_getter.clean_id(lastURL)
        videoItem = self.video_getter.get_video(vid_id)
        comment = self.video_getter.get_comment(vid_id)

        context = {
            'form': form,
            'title': videoItem["snippet"]["title"],
            'viewCount': videoItem["statistics"]["viewCount"],
            "thumbnail": videoItem["snippet"]["thumbnails"]["medium"]["url"],
            "thumbnailFile": thumbnail,
            'comment': comment,
            "mp3_path": lastAudio,
            "spanishText": spanish_text,
            "speechPath": lastSpeech,
            "ocr": ocr
        }

        return render(request, 'home.html', context=context)

    def post(self, request):
        form = self.form(request.POST)

        if form.is_valid():
            url = form.cleaned_data['url']

            # Download video and convert to mp3
            video_file = self.video_downloader.download_video(url, settings.MEDIA_ROOT)

            mp3_file = self.video_downloader.video_to_mp3(os.path.join(settings.MEDIA_ROOT, "video.mp4"),
                                                          os.path.join(settings.MEDIA_ROOT, "audio.mp3"))

            mp3_path = os.path.join(settings.MEDIA_ROOT, "audio.mp3")

            audio_segment = AudioSegment.from_file(mp3_path, format="mp3")
            trimmed_mp3 = audio_segment[30000:45100]
            mp3_file = trimmed_mp3.export(mp3_path, format="mp3")

            # Clean id, get video, get comment
            vid_id = self.video_getter.clean_id(url)
            videoItem = self.video_getter.get_video(vid_id)
            comment = self.video_getter.get_comment(vid_id)

            # Get thumbnail
            thumbnailurl = videoItem["snippet"]["thumbnails"]["medium"]["url"]
            img_data = requests.get(thumbnailurl).content
            thumbnail_path = os.path.join(settings.MEDIA_ROOT, "thumbnail.jpeg")
            with open(thumbnail_path, 'wb') as handler:
                handler.write(img_data)

            # Transcribe audio to english text
            openapi = OpenAPI()
            english_text = openapi.speech_to_text(mp3_path)
            # Translate to spanish
            spanish_text = openapi.english_to_spanish(english_text)

            # Spanish speech to text
            speech_file_path = openapi.text_to_speech(spanish_text)

            # Run vision
            vision = CloudVision()
            ocr = vision.detect_text(thumbnail_path)

            # Save in DB
            newVideo = Videos.objects.create(
                url=url,
                audio=mp3_path,
                spanish_text=spanish_text,
                speech=speech_file_path,
                thumbnail=thumbnail_path,
                ocr=ocr
            )

            # Get correct urls
            audio = newVideo.audio.url
            speech = newVideo.speech.url
            thumbnail = newVideo.thumbnail.url


            newform = self.form
            context = {
                "id": videoItem["id"],
                "title": videoItem["snippet"]["title"],
                "description": videoItem["snippet"]["description"],
                "thumbnail": thumbnailurl,
                "thumbnailFile": thumbnail,
                "iframe": videoItem["player"]["embedHtml"],
                'viewCount': videoItem["statistics"]["viewCount"],
                'comment': comment,
                "form": newform,
                "mp3_path": audio,
                "spanishText": spanish_text,
                "speechPath": speech,
                "ocr": ocr
            }

            return render(request, 'home.html', context=context)
