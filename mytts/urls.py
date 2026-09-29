from django.urls import path

from . import views


urlpatterns = [

    path(
        "",
        views.home,
        name="home"
    ),

    path(
        "upload-voice/",
        views.upload_voice,
        name="upload_voice"
    ),

    path(
        "generate/",
        views.generate_tts,
        name="generate_tts"
    ),

]