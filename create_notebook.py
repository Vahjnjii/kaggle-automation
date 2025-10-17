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
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice_name,
                        )
                    )
                )
            )
        )
        
        # Extract audio data
        audio_data = response.candidates[0].content.parts[0].inline_data.data
        
        # Create unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"gemini_voiceover_{timestamp}.wav"
        
        # Save as WAV file
        save_wave_file(output_file, audio_data)
        
        # Success message
        word_count = len(text.split())
        char_count = len(text)
        status_msg = (
            f"✅ Hyper-Realistic Voiceover Generated!\\n"
            f"🎙️ Voice: {voice_name}\\n"
            f"🤖 Model: {model_name.split('-')[2].upper()}\\n"
            f"📝 Words: {word_count} | Characters: {char_count}\\n"
            f"🔑 API: {api_key[:25]}..."
        )
        
        return output_file, status_msg
        
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}\\n\\n💡 Tip: If you see rate limit errors, try again in a few seconds."
        return None, error_msg

# Create Gradio Interface
with gr.Blocks(theme=gr.themes.Soft(), title="Gemini TTS Voice Generator") as demo:
    gr.Markdown(
        """
        # 🎙️ Gemini Native TTS - Hyper-Realistic Voice Generator
        ### Generate professional studio-quality voiceovers with Google's Gemini 2.5 AI
        **Features:** 30+ Ultra-Realistic Voices | Multi-Language | Style Control | Random API Key Rotation
        """
    )
    
    with gr.Row():
        with gr.Column(scale=2):
            text_input = gr.Textbox(
                label="📝 Enter Your Text",
                placeholder="Paste your complete script here...\\n\\nExample: Welcome to our podcast! Today we'll discuss artificial intelligence and its impact on society.",
                lines=12,
                max_lines=25
            )
            
            style_input = gr.Textbox(
                label="🎨 Style Instructions (Optional)",
                placeholder="Example: Say cheerfully | Speak in a calm professional tone | Narrate dramatically | Whisper mysteriously",
                lines=2
            )
            
            with gr.Row():
                model_dropdown = gr.Dropdown(
                    choices=list(MODEL_OPTIONS.keys()),
                    value="Gemini 2.5 Flash (Fast & Efficient)",
                    label="🤖 Select Model"
                )
                
                voice_dropdown = gr.Dropdown(
                    choices=list(VOICE_OPTIONS.keys()),
                    value="🎙️ Kore (Professional)",
                    label="🎤 Select Voice"
                )
            
            generate_btn = gr.Button(
                "🎵 Generate Hyper-Realistic Voiceover", 
                variant="primary", 
                size="lg"
            )
        
        with gr.Column(scale=1):
            audio_output = gr.Audio(
                label="🔊 Generated Voiceover",
                type="filepath",
                interactive=False
            )
            status_output = gr.Textbox(
                label="📊 Generation Status",
                lines=8,
                interactive=False
            )
    
    gr.Markdown(
        """
        ---
        ### 🌟 Available Voice Styles:
        - **Zephyr**: Bright and energetic
        - **Puck**: Upbeat and friendly
        - **Charon**: Clear and informative
        - **Kore**: Professional narrator
        - **Fenrir**: Deep and authoritative
        - **Aoede**: Musical and expressive
        - ...and 24 more voices!
        
        ### 💡 Pro Tips:
        - ✨ **Style Control**: Use natural language to guide tone (e.g., "Say cheerfully", "Speak in a documentary style")
        - 🚀 **Fast Mode**: Use Flash model for quick generation
        - 💎 **Quality Mode**: Use Pro model for maximum realism
        - 🔄 **Auto Retry**: System automatically rotates through 20 API keys
        - 🌍 **Multi-Language**: Supports 24+ languages automatically detected
        - 📚 **Long Form**: Perfect for audiobooks, podcasts, and video narration
        
        ### ⚠️ Important Notes:
        - Each generation uses Gemini's native TTS (Preview)
        - Maximum quality with near-human voice synthesis
        - Rate limits apply - if you see errors, wait 30 seconds and retry
        """
    )
    
    # Event handler
    def process_voiceover(text, voice_display, model_display, style):
        voice_name = VOICE_OPTIONS[voice_display]
        model_name = MODEL_OPTIONS[model_display]
        return generate_gemini_voiceover(text, voice_name, model_name, style)
    
    generate_btn.click(
        fn=process_voiceover,
        inputs=[text_input, voice_dropdown, model_dropdown, style_input],
        outputs=[audio_output, status_output]
    )
    
    # Example texts
    gr.Examples(
        examples=[
            [
                "Welcome to the future of artificial intelligence. Today, we're exploring how AI is transforming our world in ways we never imagined possible.",
                "🎙️ Kore (Professional)",
                "Gemini 2.5 Flash (Fast & Efficient)",
                "Say in a professional documentary style"
            ],
            [
                "Once upon a time, in a magical forest filled with wonder, there lived a curious little fox who loved adventures.",
                "🌸 Autonoe (Gentle)",
                "Gemini 2.5 Pro (High Quality)",
                "Narrate as a bedtime story"
            ],
            [
                "Breaking news! Scientists have made a groundbreaking discovery that could change everything we know about the universe.",
                "📰 Charon (Informative)",
                "Gemini 2.5 Flash (Fast & Efficient)",
                "Say as a news anchor"
            ],
            [
                "In the depths of the ancient library, whispers echoed through the shadows, revealing secrets long forgotten.",
                "🌙 Umbriel (Mysterious)",
                "Gemini 2.5 Pro (High Quality)",
                "Speak in a spooky whisper"
            ]
        ],
        inputs=[text_input, voice_dropdown, model_dropdown, style_input],
        label="📖 Example Scripts - Click to Load"
    )

# Launch the interface
print("🚀 Launching Gemini Native TTS Interface...")
demo.launch(share=True, debug=True)'''
    
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
    print(f"📤 Updating notebook: {metadata['title']}")
    api.kernels_push('.')
    print(f"✅ Success! View at: https://www.kaggle.com/code/{metadata['id']}")

if __name__ == "__main__":
    create_notebook()
