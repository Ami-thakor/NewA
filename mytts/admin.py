from django.contrib import admin
from .models import Voice, Generation


@admin.register(Voice)
class VoiceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "model",
        "created_at",
    )


@admin.register(Generation)
class GenerationAdmin(admin.ModelAdmin):
    list_display = (
        "voice",
        "model",
        "language",
        "seed",
        "pace",
        "created_at",
    )