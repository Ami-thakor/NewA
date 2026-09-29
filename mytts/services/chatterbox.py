import os
import re
import random
import tempfile
import shutil

import numpy as np
import soundfile as sf
import torch

from sentencex import segment
from chatterbox.mtl_tts import ChatterboxMultilingualTTS


# =========================================================
# CONFIG
# =========================================================

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

MODEL = None

MAX_CHARS_PER_CHUNK = 300

SUPPORTED_LANGUAGES = {
    "hi": "Hindi",
    "en": "English",
}


# =========================================================
# MODEL
# =========================================================

def get_or_load_model():
    """
    Load Chatterbox model only once.
    """

    global MODEL

    if MODEL is None:

        print("Loading Chatterbox Multilingual model...")

        MODEL = ChatterboxMultilingualTTS.from_pretrained(
            DEVICE
        )

        print(
            f"Chatterbox loaded successfully on: {DEVICE}"
        )

    return MODEL


# =========================================================
# SEED
# =========================================================

def set_seed(seed: int):

    torch.manual_seed(seed)

    if DEVICE == "cuda":
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)

    random.seed(seed)
    np.random.seed(seed)


# =========================================================
# TEXT CLEANING
# =========================================================

def clean_text(text: str) -> str:

    replacements = {
        "–": " ",
        "—": " ",
        "-": " ",
        "**": " ",
        "*": " ",
        "#": " ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove emojis
    emoji_pattern = re.compile(
        r'[\U0001F600-\U0001F64F]|'
        r'[\U0001F300-\U0001F5FF]|'
        r'[\U0001F680-\U0001F6FF]|'
        r'[\U0001F700-\U0001F77F]|'
        r'[\U0001F780-\U0001F7FF]|'
        r'[\U0001F800-\U0001F8FF]|'
        r'[\U0001F900-\U0001F9FF]|'
        r'[\U0001FA00-\U0001FA6F]|'
        r'[\U0001FA70-\U0001FAFF]|'
        r'[\U00002702-\U000027B0]|'
        r'[\U0001F1E0-\U0001F1FF]',
        flags=re.UNICODE
    )

    text = emoji_pattern.sub("", text)

    # Remove extra spaces/newlines
    text = re.sub(r"\s+", " ", text).strip()

    return text


# =========================================================
# WORD SPLIT
# =========================================================

def word_split(text, char_limit=300):

    words = text.split()

    chunks = []
    current_chunk = ""

    for word in words:

        # Extremely long word
        if len(word) > char_limit:

            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""

            for i in range(0, len(word), char_limit):
                chunks.append(
                    word[i:i + char_limit]
                )

            continue

        candidate = (
            word
            if not current_chunk
            else current_chunk + " " + word
        )

        if len(candidate) <= char_limit:

            current_chunk = candidate

        else:

            if current_chunk:
                chunks.append(current_chunk)

            current_chunk = word

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


# =========================================================
# SENTENCE + 300 CHAR CHUNKING
# =========================================================

def split_into_chunks(
    text,
    language_code,
    max_char_limit=300
):

    text = text.strip()

    if not text:
        return []

    if len(text) <= max_char_limit:
        return [text]

    print(
        "Text is longer than 300 characters. "
        "Splitting into smaller chunks..."
    )

    # sentencex expects language code
    try:

        raw_sentences = list(
            segment(language_code, text)
        )

    except Exception:

        # Fallback
        raw_sentences = re.split(
            r"(?<=[.!?।])\s+",
            text
        )

    chunks = []

    current_chunk = ""

    for sentence in raw_sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        sentence_chunks = word_split(
            sentence,
            char_limit=max_char_limit
        )

        for part in sentence_chunks:

            candidate = (
                part
                if not current_chunk
                else current_chunk + " " + part
            )

            if len(candidate) <= max_char_limit:

                current_chunk = candidate

            else:

                if current_chunk:
                    chunks.append(current_chunk)

                current_chunk = part

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


# =========================================================
# SINGLE CHUNK GENERATION
# =========================================================

def generate_tts_chunk(
    text,
    language,
    reference_audio,
    seed=12,
    exaggeration=0.5,
    temperature=0.8,
    cfg_weight=0.5,
):

    model = get_or_load_model()

    if seed != 0:
        set_seed(seed)

    print(
        f"Generating chunk: {text[:80]}..."
    )

    kwargs = {
        "exaggeration": exaggeration,
        "temperature": temperature,
        "cfg_weight": cfg_weight,
    }

    if reference_audio:
        kwargs["audio_prompt_path"] = reference_audio

        print(
            f"Reference voice: {reference_audio}"
        )

    wav = model.generate(
        text,
        language_id=language,
        **kwargs
    )

    # Chatterbox output -> numpy
    audio = wav.squeeze(0).detach().cpu().numpy()

    return model.sr, audio


# =========================================================
# FULL TTS GENERATION
# =========================================================

def generate_tts_audio(
    text,
    language,
    reference_audio,
    seed=12,
    exaggeration=0.5,
    temperature=0.8,
    cfg_weight=0.5,
):

    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            "Only Hindi and English are supported."
        )

    text = clean_text(text)

    if not text:
        raise ValueError(
            "Text is empty."
        )

    chunks = split_into_chunks(
        text,
        language,
        MAX_CHARS_PER_CHUNK
    )

    print(
        f"Total chunks: {len(chunks)}"
    )

    temp_dir = tempfile.mkdtemp(
        prefix="chatterbox_"
    )

    chunk_files = []

    try:

        # =========================================
        # GENERATE EACH CHUNK
        # =========================================

        for index, chunk in enumerate(chunks):

            print(
                f"[{index + 1}/{len(chunks)}]"
            )

            chunk_path = os.path.join(
                temp_dir,
                f"chunk_{index:04d}.wav"
            )

            try:

                sr, audio = generate_tts_chunk(
                    text=chunk,
                    language=language,
                    reference_audio=reference_audio,
                    seed=seed,
                    exaggeration=exaggeration,
                    temperature=temperature,
                    cfg_weight=cfg_weight,
                )

                sf.write(
                    chunk_path,
                    audio,
                    sr
                )

                chunk_files.append(
                    chunk_path
                )

            except Exception as e:

                print(
                    f"Chunk {index} failed: {e}"
                )

                raise

        # =========================================
        # MERGE
        # =========================================

        final_audio = []

        for file_path in chunk_files:

            audio, file_sr = sf.read(
                file_path,
                dtype="float32"
            )

            final_audio.append(audio)

        if not final_audio:
            raise RuntimeError(
                "No audio was generated."
            )

        final_audio = np.concatenate(
            final_audio
        )

        return sr, final_audio

    finally:

        shutil.rmtree(
            temp_dir,
            ignore_errors=True
        )