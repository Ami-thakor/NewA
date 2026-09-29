import os
import uuid

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.core.files.base import ContentFile

from .models import Voice, Generation
from .services.chatterbox import (
    generate_tts_audio,
    SUPPORTED_LANGUAGES,
)


# =========================================================
# HOME
# =========================================================

def home(request):

    voices = Voice.objects.all().order_by("-created_at")

    return render(
        request,
        "index.html",
        {
            "voices": voices,
        }
    )


# =========================================================
# UPLOAD VOICE
# =========================================================

def upload_voice(request):

    if request.method == "POST":

        name = request.POST.get("name")
        reference_audio = request.FILES.get(
            "reference_audio"
        )

        if not name:
            return redirect("home")

        if not reference_audio:
            return redirect("home")

        Voice.objects.create(
            name=name,
            reference_audio=reference_audio,
            model="chatterbox"
        )

        return redirect("home")

    return redirect("home")


# =========================================================
# GENERATE TTS
# =========================================================

def generate_tts(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "success": False,
                "error": "POST request required."
            },
            status=405
        )

    try:

        # =========================================
        # GET DATA
        # =========================================

        text = request.POST.get(
            "text",
            ""
        ).strip()

        voice_id = request.POST.get(
            "voice"
        )

        model_name = request.POST.get(
            "model",
            "chatterbox"
        )

        language = request.POST.get(
            "language",
            "hi"
        )

        seed = int(
            request.POST.get(
                "seed",
                "12"
            )
        )

        pace = float(
            request.POST.get(
                "pace",
                "0.5"
            )
        )

        # =========================================
        # VALIDATION
        # =========================================

        if not text:

            return JsonResponse(
                {
                    "success": False,
                    "error": "Please enter some text."
                },
                status=400
            )

        if len(text) > 30000:

            return JsonResponse(
                {
                    "success": False,
                    "error": "Maximum 30,000 characters allowed."
                },
                status=400
            )

        if not voice_id:

            return JsonResponse(
                {
                    "success": False,
                    "error": "Please select a voice."
                },
                status=400
            )

        if language not in SUPPORTED_LANGUAGES:

            return JsonResponse(
                {
                    "success": False,
                    "error": "Only Hindi and English are supported."
                },
                status=400
            )

        if model_name != "chatterbox":

            return JsonResponse(
                {
                    "success": False,
                    "error": "Only Chatterbox is currently enabled."
                },
                status=400
            )

        # CFG/Pace
        if pace < 0.2 or pace > 1.0:

            return JsonResponse(
                {
                    "success": False,
                    "error": "Pace must be between 0.2 and 1.0."
                },
                status=400
            )

        # =========================================
        # VOICE
        # =========================================

        voice = Voice.objects.get(
            id=voice_id
        )

        reference_audio = voice.reference_audio.path

        if not os.path.exists(reference_audio):

            return JsonResponse(
                {
                    "success": False,
                    "error": "Reference audio file not found."
                },
                status=404
            )

        # =========================================
        # GENERATE
        # =========================================

        print("=" * 60)

        print("TTS REQUEST")
        print("Voice:", voice.name)
        print("Language:", language)
        print("Seed:", seed)
        print("CFG/Pace:", pace)
        print("Characters:", len(text))

        print("=" * 60)

        sample_rate, audio = generate_tts_audio(
            text=text,
            language=language,
            reference_audio=reference_audio,
            seed=seed,
            exaggeration=0.5,
            temperature=0.8,
            cfg_weight=pace,
        )

        # =========================================
        # SAVE WAV
        # =========================================

        output_dir = os.path.join(
            settings.MEDIA_ROOT,
            "outputs"
        )

        os.makedirs(
            output_dir,
            exist_ok=True
        )

        filename = (
            f"tts_{uuid.uuid4().hex}.wav"
        )

        relative_path = (
            f"outputs/{filename}"
        )

        # Save directly to memory
        import io

        buffer = io.BytesIO()

        import soundfile as sf

        sf.write(
            buffer,
            audio,
            sample_rate,
            format="WAV"
        )

        buffer.seek(0)

        # =========================================
        # DB RECORD
        # =========================================

        generation = Generation(
            voice=voice,
            text=text,
            model=model_name,
            language=language,
            seed=seed,
            pace=pace,
        )

        generation.output_audio.save(
            filename,
            ContentFile(buffer.read()),
            save=True
        )

        # =========================================
        # RESPONSE
        # =========================================

        audio_url = (
            settings.MEDIA_URL
            + generation.output_audio.name
        )

        print(
            "Generated:",
            audio_url
        )

        return JsonResponse(
            {
                "success": True,
                "audio_url": audio_url,
                "filename": os.path.basename(
                    generation.output_audio.name
                ),
            }
        )

    # =============================================
    # ERRORS
    # =============================================

    except Voice.DoesNotExist:

        return JsonResponse(
            {
                "success": False,
                "error": "Selected voice does not exist."
            },
            status=404
        )

    except Exception as e:

        print(
            "TTS ERROR:",
            repr(e)
        )

        return JsonResponse(
            {
                "success": False,
                "error": str(e)
            },
            status=500
        )