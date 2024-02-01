from .models import Videos
from django.forms import ModelForm


class VideoForm(ModelForm):
    class Meta:
        label = 'Enter a URL'
        model = Videos
        fields = {'url'}

