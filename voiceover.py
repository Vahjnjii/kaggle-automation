import json
import os
from datetime import datetime

# Set Kaggle credentials from environment variables BEFORE importing
os.environ['KAGGLE_USERNAME'] = os.environ.get('KAGGLE_USERNAME', '')
os.environ['KAGGLE_KEY'] = os.environ.get('KAGGLE_KEY', '')

# NOW import Kaggle API (after credentials are set)
from kaggle.api.kaggle_api_extended import KaggleApi

def create_notebook():
    api = KaggleApi()
    api.authenticate()
    
    # Use FIXED notebook ID (will update same notebook every time)
    username = os.environ.get('KAGGLE_USERNAME', 'your-username')
    notebook_slug = "gemini-tts-voice-generator"
    
    # Notebook metadata
    metadata = {
        "id": f"{username}/{notebook_slug}",
        "title": "Gemini TTS Voice Generator",
        "code_file": "notebook.ipynb",
        "language": "python",
        "kernel_type": "notebook",
        "is_private": True,
        "enable_gpu": False,
        "enable_internet": True,
        "dataset_sources": [],
        "competition_sources": [],
        "kernel_sources": []
    }
    
    # YOUR COMPLETE ORIGINAL CODE
    complete_code = '''# Install required libraries
!pip install -q gradio google-generativeai

import gradio as gr
import random
import base64
import wave
import os
from datetime import datetime
from google import genai
from google.genai import types

# Your API Keys
API_KEYS = [
    'AIzaSyBWYWNkIt8Q7nl7I-JDj9ozaVwOAFf7WsA',
    'AIzaSyB4Y_Z8bc82VN15pGes-a049ZNcjTsJTFs',
    'AIzaSyD3vGJyJtdSKuaxbb4AZVosyJ76ult21d8',
    'AIzaSyAbmN08A4l61-q1mYjK3DQe29BKcSYmov8',
    'AIzaSyAD8-aEvVIvkBwQFUMugb9XgVDBUQR-zfk',
    'AIzaSyD-nf3OHLbI5R23f7VLVLO1FHTWM6OWwCs',
    'AIzaSyBjYlIv84CNzpudzYyl6ANCz-2xRtSw5Dc',
    'AIzaSyCLjFGChLdvNSBoCVKbTAtR4zNTegeI19U',
    'AIzaSyD5IB7uqfyAp9XbN7GrZb_ykofO44AFIWw',
    'AIzaSyAuLu3EU3o_bp4GsHKKQuvE-u02EXEi308',
    'AIzaSyDcwUdktdj5J1JsVn8pLY4aog2S-2hE1j4',
    'AIzaSyCNJdzUaErIF4CkHhd_W3cNAhU7qqWgWLI',
    'AIzaSyA94-jrtNUK1Rs9DWxE4YH7cAvpo4oGu5k',
    'AIzaSyBiR58evdCtCGAtZiOvIiwAKtc6P-K6d0o',
    'AIzaSyAC3au8LAdnk_-yrzKTZ9EfDUUypJc2K_0',
    'AIzaSyANdNVOWRlRKubxa7w0lX21MFztQtHirbM',
    'AIzaSyCqf1kobLM4Xo1WDkl49UJpXvJp3g1g6RE',
    'AIzaSyAclybUHEwGic8nIRsIgV976UQNmxCAqSQ',
    'AIzaSyCASH5DEm2l8JwfFWJw8gMtYgR8fjip2sA',
    'AIzaSyBN0V0v5IetKuEFaKTB9vfyBE0oVzZDVWg'
]

# Gemini TTS Voice Models (30 available voices)
VOICE_OPTIONS = {
    "🎭 Zephyr (Bright)": "Zephyr",
    "🎪 Puck (Upbeat)": "Puck",
    "📰 Charon (Informative)": "Charon",
    "🎙️ Kore (Professional)": "Kore",
    "🐺 Fenrir (Deep)": "Fenrir",
    "👸 Leda (Elegant)": "Leda",
    "🦉 Orus (Wise)": "Orus",
    "🎵 Aoede (Musical)": "Aoede",
    "🌊 Callirhoe (Flowing)": "Callirhoe",
    "🌸 Autonoe (Gentle)": "Autonoe",
    "⚡ Enceladus (Energetic)": "Enceladus",
    "🏔️ Iapetus (Strong)": "Iapetus",
    "🌙 Umbriel (Mysterious)": "Umbriel",
    "⭐ Algieba (Bright)": "Algieba",
    "🌺 Despina (Sweet)": "Despina",
    "💫 Erinome (Soft)": "Erinome",
    "🔮 Algenib (Mystical)": "Algenib",
    "👑 Rasalgethi (Regal)": "Rasalgethi",
    "🌟 Laomedeia (Celestial)": "Laomedeia",
    "💎 Achernar (Brilliant)": "Achernar",
    "🎯 Alnilam (Focused)": "Alnilam",
    "🌠 Schedar (Starry)": "Schedar",
    "✨ Gacrux (Sparkling)": "Gacrux",
    "🌹 Pulcherrima (Beautiful)": "Pulcherrima",
    "🎨 Achird (Artistic)": "Achird",
    "⚖️ Zubenelgenubi (Balanced)": "Zubenelgenubi",
    "🍇 Vindemiatrix (Rich)": "Vindemiatrix",
    "🌊 Sadachbia (Calm)": "Sadachbia",
    "🌅 Sadaltager (Warm)": "Sadaltager",
    "🎺 Sulafat (Melodic)": "Sulafat"
}

# Model options
MODEL_OPTIONS = {
    "Gemini 2.5 Flash (Fast & Efficient)": "gemini-2.5-flash-preview-tts",
    "Gemini 2.5 Pro (High Quality)": "gemini-2.5-pro-preview-tts"
}

def save_wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
    """Save PCM audio data to WAV file"""
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)

def generate_gemini_voiceover(text, voice_name, model_name, style_prompt=""):
    """
    Generate voiceover using Gemini's native TTS
    
    Args:
        text: Input text to convert to speech
        voice_name: Voice model name
        model_name: Gemini model to use
        style_prompt: Optional style instructions
    
    Returns:
        Path to the generated audio file and status message
    """
    try:
        # Validate input
        if not text or text.strip() == "":
            return None, "⚠️ Please enter some text to generate voiceover!"
        
        # Select random API key
        api_key = random.choice(API_KEYS)
        print(f"🔑 Using API Key: {api_key[:20]}...")
        
        # Initialize Gemini client
        client = genai.Client(api_key=api_key)
        
        # Prepare the prompt
        if style_prompt and style_prompt.strip():
            full_prompt = f"{style_prompt}: {text}"
        else:
            full_prompt = f"Say: {text}"
        
        print(f"🎤 Generating with voice: {voice_name}")
        print(f"📱 Using model: {model_name}")
        
        # Generate speech using Gemini TTS
        response = client.models.generate_content(
            model=model_name,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=t
