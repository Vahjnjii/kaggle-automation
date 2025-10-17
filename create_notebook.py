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
    
    # Generate unique notebook ID with timestamp
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    username = os.environ.get('KAGGLE_USERNAME', 'your-username')
    notebook_slug = f"gemini-tts-{timestamp}"
    
    # Notebook metadata
    metadata = {
        "id": f"{username}/{notebook_slug}",
        "title": f"Gemini TTS Voice Generator {timestamp}",
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
    
    # Complete Gemini TTS code
    complete_code = """# Install required libraries
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

# Gemini TTS Voice Models
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

MODEL_OPTIONS = {
    "Gemini 2.5 Flash (Fast & Efficient)": "gemini-2.5-flash-preview-tts",
    "Gemini 2.5 Pro (High Quality)": "gemini-2.5-pro-preview-tts"
}

def save_wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)

def generate_gemini_voiceover(text, voice_name, model_name, style_prompt=""):
    try:
        if not text or text.strip() == "":
            return None, "⚠️ Please enter some text!"
        
        api_key = random.choice(API_KEYS)
        client = genai.Client(api_key=api_key)
        
        full_prompt = f"{style_prompt}: {text}" if style_prompt else f"Say: {text}"
        
        response = client.models.generate_content(
            model=model_name,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice_name,
                        )
                    )
                )
            )
        )
        
        audio_data = response.candidates[0].content.parts[0].inline_data.data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"gemini_voiceover_{timestamp}.wav"
        save_wave_file(output_file, audio_data)
        
        return output_file, f"✅ Generated! Words: {len(text.split())}"
    except Exception as e:
        return None, f"❌ Error: {str(e)}"

with gr.Blocks(theme=gr.themes.Soft(), title="Gemini TTS") as demo:
    gr.Markdown("# 🎙️ Gemini TTS Voice Generator")
    
    with gr.Row():
        with gr.Column(scale=2):
            text_input = gr.Textbox(label="📝 Text", lines=10)
            style_input = gr.Textbox(label="🎨 Style", lines=2)
            
            with gr.Row():
                model_dropdown = gr.Dropdown(
                    choices=list(MODEL_OPTIONS.keys()),
                    value="Gemini 2.5 Flash (Fast & Efficient)",
                    label="Model"
                )
                voice_dropdown = gr.Dropdown(
                    choices=list(VOICE_OPTIONS.keys()),
                    value="🎙️ Kore (Professional)",
                    label="Voice"
                )
            
            generate_btn = gr.Button("🎵 Generate", variant="primary")
        
        with gr.Column(scale=1):
            audio_output = gr.Audio(label="Output")
            status_output = gr.Textbox(label="Status", lines=5)
    
    def process(text, voice_display, model_display, style):
        voice_name = VOICE_OPTIONS[voice_display]
        model_name = MODEL_OPTIONS[model_display]
        return generate_gemini_voiceover(text, voice_name, model_name, style)
    
    generate_btn.click(
        fn=process,
        inputs=[text_input, voice_dropdown, model_dropdown, style_input],
        outputs=[audio_output, status_output]
    )

demo.launch(share=True, debug=True)
"""
    
    # Create notebook
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": complete_code.split('\n')
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.10.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    # Save files
    with open('notebook.ipynb', 'w') as f:
        json.dump(notebook, f, indent=2)
    
    with open('kernel-metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Push to Kaggle
    print(f"📤 Pushing new notebook: {metadata['title']}")
    api.kernels_push('.')
    print(f"✅ Success! View at: https://www.kaggle.com/code/{metadata['id']}")

if __name__ == "__main__":
    create_notebook()
