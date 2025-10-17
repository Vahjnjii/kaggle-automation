import json
import os
from datetime import datetime
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
    
    # Your Gemini TTS code in notebook format
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Install required libraries\n",
                    "!pip install -q gradio google-generativeai\n"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "import gradio as gr\n",
                    "import random\n",
                    "import base64\n",
                    "import wave\n",
                    "import os\n",
                    "from datetime import datetime\n",
                    "from google import genai\n",
                    "from google.genai import types\n"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Your API Keys\n",
                    "API_KEYS = [\n",
                    "    'AIzaSyBWYWNkIt8Q7nl7I-JDj9ozaVwOAFf7WsA',\n",
                    "    'AIzaSyB4Y_Z8bc82VN15pGes-a049ZNcjTsJTFs',\n",
                    "    'AIzaSyD3vGJyJtdSKuaxbb4AZVosyJ76ult21d8',\n",
                    "    'AIzaSyAbmN08A4l61-q1mYjK3DQe29BKcSYmov8',\n",
                    "    'AIzaSyAD8-aEvVIvkBwQFUMugb9XgVDBUQR-zfk',\n",
                    "    'AIzaSyD-nf3OHLbI5R23f7VLVLO1FHTWM6OWwCs',\n",
                    "    'AIzaSyBjYlIv84CNzpudzYyl6ANCz-2xRtSw5Dc',\n",
                    "    'AIzaSyCLjFGChLdvNSBoCVKbTAtR4zNTegeI19U',\n",
                    "    'AIzaSyD5IB7uqfyAp9XbN7GrZb_ykofO44AFIWw',\n",
                    "    'AIzaSyAuLu3EU3o_bp4GsHKKQuvE-u02EXEi308',\n",
                    "    'AIzaSyDcwUdktdj5J1JsVn8pLY4aog2S-2hE1j4',\n",
                    "    'AIzaSyCNJdzUaErIF4CkHhd_W3cNAhU7qqWgWLI',\n",
                    "    'AIzaSyA94-jrtNUK1Rs9DWxE4YH7cAvpo4oGu5k',\n",
                    "    'AIzaSyBiR58evdCtCGAtZiOvIiwAKtc6P-K6d0o',\n",
                    "    'AIzaSyAC3au8LAdnk_-yrzKTZ9EfDUUypJc2K_0',\n",
                    "    'AIzaSyANdNVOWRlRKubxa7w0lX21MFztQtHirbM',\n",
                    "    'AIzaSyCqf1kobLM4Xo1WDkl49UJpXvJp3g1g6RE',\n",
                    "    'AIzaSyAclybUHEwGic8nIRsIgV976UQNmxCAqSQ',\n",
                    "    'AIzaSyCASH5DEm2l8JwfFWJw8gMtYgR8fjip2sA',\n",
                    "    'AIzaSyBN0V0v5IetKuEFaKTB9vfyBE0oVzZDVWg'\n",
                    "]\n"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Gemini TTS Voice Models (30 available voices)\n",
                    "VOICE_OPTIONS = {\n",
                    '    \"🎭 Zephyr (Bright)\": \"Zephyr\",\n',
                    '    \"🎪 Puck (Upbeat)\": \"Puck\",\n',
                    '    \"📰 Charon (Informative)\": \"Charon\",\n',
                    '    \"🎙️ Kore (Professional)\": \"Kore\",\n',
                    '    \"🐺 Fenrir (Deep)\": \"Fenrir\",\n',
                    '    \"👸 Leda (Elegant)\": \"Leda\",\n',
                    '    \"🦉 Orus (Wise)\": \"Orus\",\n',
                    '    \"🎵 Aoede (Musical)\": \"Aoede\",\n',
                    '    \"🌊 Callirhoe (Flowing)\": \"Callirhoe\",\n',
                    '    \"🌸 Autonoe (Gentle)\": \"Autonoe\",\n',
                    '    \"⚡ Enceladus (Energetic)\": \"Enceladus\",\n',
                    '    \"🏔️ Iapetus (Strong)\": \"Iapetus\",\n',
                    '    \"🌙 Umbriel (Mysterious)\": \"Umbriel\",\n',
                    '    \"⭐ Algieba (Bright)\": \"Algieba\",\n',
                    '    \"🌺 Despina (Sweet)\": \"Despina\",\n',
                    '    \"💫 Erinome (Soft)\": \"Erinome\",\n',
                    '    \"🔮 Algenib (Mystical)\": \"Algenib\",\n',
                    '    \"👑 Rasalgethi (Regal)\": \"Rasalgethi\",\n',
                    '    \"🌟 Laomedeia (Celestial)\": \"Laomedeia\",\n',
                    '    \"💎 Achernar (Brilliant)\": \"Achernar\",\n',
                    '    \"🎯 Alnilam (Focused)\": \"Alnilam\",\n',
                    '    \"🌠 Schedar (Starry)\": \"Schedar\",\n',
                    '    \"✨ Gacrux (Sparkling)\": \"Gacrux\",\n',
                    '    \"🌹 Pulcherrima (Beautiful)\": \"Pulcherrima\",\n',
                    '    \"🎨 Achird (Artistic)\": \"Achird\",\n',
                    '    \"⚖️ Zubenelgenubi (Balanced)\": \"Zubenelgenubi\",\n',
                    '    \"🍇 Vindemiatrix (Rich)\": \"Vindemiatrix\",\n',
                    '    \"🌊 Sadachbia (Calm)\": \"Sadachbia\",\n',
                    '    \"🌅 Sadaltager (Warm)\": \"Sadaltager\",\n',
                    '    \"🎺 Sulafat (Melodic)\": \"Sulafat\"\n',
                    "}\n",
                    "\n",
                    "# Model options\n",
                    "MODEL_OPTIONS = {\n",
                    '    \"Gemini 2.5 Flash (Fast & Efficient)\": \"gemini-2.5-flash-preview-tts\",\n',
                    '    \"Gemini 2.5 Pro (High Quality)\": \"gemini-2.5-pro-preview-tts\"\n',
                    "}\n"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "def save_wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):\n",
                    '    \"\"\"Save PCM audio data to WAV file\"\"\"\n',
                    "    with wave.open(filename, \"wb\") as wf:\n",
                    "        wf.setnchannels(channels)\n",
                    "        wf.setsampwidth(sample_width)\n",
                    "        wf.setframerate(rate)\n",
                    "        wf.writeframes(pcm)\n"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "def generate_gemini_voiceover(text, voice_name, model_name, style_prompt=\"\"):\n",
                    '    \"\"\"\n',
                    "    Generate voiceover using Gemini's native TTS\n",
                    "    \n",
                    "    Args:\n",
                    "        text: Input text to convert to speech\n",
                    "        voice_name: Voice model name\n",
                    "        model_name: Gemini model to use\n",
                    "        style_prompt: Optional style instructions\n",
                    "    \n",
                    "    Returns:\n",
                    "        Path to the generated audio file and status message\n",
                    '    \"\"\"\n',
                    "    try:\n",
                    "        # Validate input\n",
                    "        if not text or text.strip() == \"\":\n",
                    '            return None, \"⚠️ Please enter some text to generate voiceover!\"\n',
                    "        \n",
                    "        # Select random API key\n",
                    "        api_key = random.choice(API_KEYS)\n",
                    "        print(f\"🔑 Using API Key: {api_key[:20]}...\")\n",
                    "        \n",
                    "        # Initialize Gemini client\n",
                    "        client = genai.Client(api_key=api_key)\n",
                    "        \n",
                    "        # Prepare the prompt\n",
                    "        if style_prompt and style_prompt.strip():\n",
                    "            full_prompt = f\"{style_prompt}: {text}\"\n",
                    "        else:\n",
                    "            full_prompt = f\"Say: {text}\"\n",
                    "        \n",
                    "        print(f\"🎤 Generating with voice: {voice_name}\")\n",
                    "        print(f\"📱 Using model: {model_name}\")\n",
                    "        \n",
                    "        # Generate speech using Gemini TTS\n",
                    "        response = client.models.generate_content(\n",
                    "            model=model_name,\n",
                    "            contents=full_prompt,\n",
                    "            config=types.GenerateContentConfig(\n",
                    '                response_modalities=[\"AUDIO\"],\n',
                    "                speech_config=types.SpeechConfig(\n",
                    "                    voice_config=types.VoiceConfig(\n",
                    "                        prebuilt_voice_config=types.PrebuiltVoiceConfig(\n",
                    "                            voice_name=voice_name,\n",
                    "                        )\n",
                    "                    )\n",
                    "                )\n",
                    "            )\n",
                    "        )\n",
                    "        \n",
                    "        # Extract audio data\n",
                    "        audio_data = response.candidates[0].content.parts[0].inline_data.data\n",
                    "        \n",
                    "        # Create unique filename\n",
                    '        timestamp = datetime.now().strftime(\"%Y%m%d_%H%M%S\")\n',
                    "        output_file = f\"gemini_voiceover_{timestamp}.wav\"\n",
                    "        \n",
                    "        # Save as WAV file\n",
                    "        save_wave_file(output_file, audio_data)\n",
                    "        \n",
                    "        # Success message\n",
                    "        word_count = len(text.split())\n",
                    "        char_count = len(text)\n",
                    "        status_msg = (\n",
                    '            f\"✅ Hyper-Realistic Voiceover Generated!\\n\"\n',
                    '            f\"🎙️ Voice: {voice_name}\\n\"\n',
                    "            f\"�🤖 Model: {model_name.split('-')[2].upper()}\\n\"\n",
                    '            f\"📝 Words: {word_count} | Characters: {char_count}\\n\"\n',
                    '            f\"🔑 API: {api_key[:25]}...\"\n',
                    "        )\n",
                    "        \n",
                    "        return output_file, status_msg\n",
                    "        \n",
                    "    except Exception as e:\n",
                    '        error_msg = f\"❌ Error: {str(e)}\\n\\n💡 Tip: If you see rate limit errors, try again in a few seconds.\"\n',
                    "        return None, error_msg\n"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Create Gradio Interface\n",
                    "with gr.Blocks(theme=gr.themes.Soft(), title=\"Gemini TTS Voice Generator\") as demo:\n",
                    "    gr.Markdown(\n",
                    '        \"\"\"\n',
                    "        # 🎙️ Gemini Native TTS - Hyper-Realistic Voice Generator\n",
                    "        ### Generate professional studio-quality voiceovers with Google's Gemini 2.5 AI\n",
                    "        **Features:** 30+ Ultra-Realistic Voices | Multi-Language | Style Control | Random API Key Rotation\n",
                    '        \"\"\"\n',
                    "    )\n",
                    "    \n",
                    "    with gr.Row():\n",
                    "        with gr.Column(scale=2):\n",
                    "            text_input = gr.Textbox(\n",
                    '                label=\"📝 Enter Your Text\",\n',
                    '                placeholder=\"Paste your complete script here...\\n\\nExample: Welcome to our podcast! Today we\\'ll discuss artificial intelligence and its impact on society.\",\n',
                    "                lines=12,\n",
                    "                max_lines=25\n",
                    "            )\n",
                    "            \n",
                    "            style_input = gr.Textbox(\n",
                    '                label=\"🎨 Style Instructions (Optional)\",\n',
                    '                placeholder=\"Example: Say cheerfully | Speak in a calm professional tone | Narrate dramatically | Whisper mysteriously\",\n',
                    "                lines=2\n",
                    "            )\n",
                    "            \n",
                    "            with gr.Row():\n",
                    "                model_dropdown = gr.Dropdown(\n",
                    "                    choices=list(MODEL_OPTIONS.keys()),\n",
                    '                    value=\"Gemini 2.5 Flash (Fast & Efficient)\",\n',
                    '                    label=\"🤖 Select Model\"\n',
                    "                )\n",
                    "                \n",
                    "                voice_dropdown = gr.Dropdown(\n",
                    "                    choices=list(VOICE_OPTIONS.keys()),\n",
                    '                    value=\"🎙️ Kore (Professional)\",\n',
                    '                    label=\"🎤 Select Voice\"\n',
                    "                )\n",
                    "            \n",
                    "            generate_btn = gr.Button(\n",
                    '                \"🎵 Generate Hyper-Realistic Voiceover\", \n',
                    '                variant=\"primary\", \n',
                    '                size=\"lg\"\n',
                    "            )\n",
                    "        \n",
                    "        with gr.Column(scale=1):\n",
                    "            audio_output = gr.Audio(\n",
                    '                label=\"🔊 Generated Voiceover\",\n',
                    '                type=\"filepath\",\n',
                    "                interactive=False\n",
                    "            )\n",
                    "            status_output = gr.Textbox(\n",
                    '                label=\"📊 Generation Status\",\n',
                    "                lines=8,\n",
                    "                interactive=False\n",
                    "            )\n",
                    "    \n",
                    "    # Event handler\n",
                    "    def process_voiceover(text, voice_display, model_display, style):\n",
                    "        voice_name = VOICE_OPTIONS[voice_display]\n",
                    "        model_name = MODEL_OPTIONS[model_display]\n",
                    "        return generate_gemini_voiceover(text, voice_name, model_name, style)\n",
                    "    \n",
                    "    generate_btn.click(\n",
                    "        fn=process_voiceover,\n",
                    "        inputs=[text_input, voice_dropdown, model_dropdown, style_input],\n",
                    "        outputs=[audio_output, status_output]\n",
                    "    )\n",
                    "    \n",
                    "    # Example texts\n",
                    "    gr.Examples(\n",
                    "        examples=[\n",
                    "            [\n",
                    '                \"Welcome to the future of artificial intelligence. Today, we\\'re exploring how AI is transforming our world in ways we never imagined possible.\",\n',
                    '                \"🎙️ Kore (Professional)\",\n',
                    '                \"Gemini 2.5 Flash (Fast & Efficient)\",\n',
                    '                \"Say in a professional documentary style\"\n',
                    "            ]\n",
                    "        ],\n",
                    "        inputs=[text_input, voice_dropdown, model_dropdown, style_input],\n",
                    '        label=\"📖 Example Scripts - Click to Load\"\n',
                    "    )\n",
                    "\n",
                    "# Launch the interface\n",
                    "print(\"🚀 Launching Gemini Native TTS Interface...\")\n",
                    "demo.launch(share=True, debug=True)\n"
                ]
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
    print(f"📤 Pushing new notebook to Kaggle: {metadata['title']}")
    api.kernels_push('.')
    print(f"✅ Notebook created successfully!")
    print(f"🔗 View at: https://www.kaggle.com/code/{metadata['id']}")

if __name__ == "__main__":
    create_notebook()
