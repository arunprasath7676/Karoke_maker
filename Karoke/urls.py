from django.contrib import admin
from django.urls import path
from .views import remove_vocals,generate_srt,merge_audio_and_karaoke

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('views/remove_vocals/', remove_vocals, name='remove_vocals'),
    path('views/generate_srt/',generate_srt,name='generate_srt'),
    path('views/merge_audio_and_karaoke/',merge_audio_and_karaoke,name='merge_audio_and_karaoke'),

]