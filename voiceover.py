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
    notebook_slug = "gemini-tts-processor"
    
    # Notebook metadata - IMPORTANT: Add request dataset as source
    metadata = {
        "id": f"{username}/{notebook_slug}",
        "title": "Gemini TTS Processor",
        "code_file": "notebook.ipynb",
        "language": "python",
        "kernel_type": "notebook",
        "is_private": True,
        "enable_gpu": False,
        "enable_internet": True,
        "dataset_sources": [
            f"{username}/voiceover-requests"  # This allows the notebook to read requests
        ],
        "competition_sources": [],
        "kernel_sources": []
    }
    
    # Complete processor code as a multi-line string
    complete_code = """# Install required packages
!pip install -q google-generativeai pydub

import json
import os
import time
import wave
import re
import random
from datetime import datetime
from google import genai
from google.genai import types
from pydub import AudioSegment
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Kaggle API setup
from kaggle.api.kaggle_api_extended import KaggleApi
api = KaggleApi()
api.authenticate()

# Configuration - UPDATE THIS WITH YOUR USERNAME
KAGGLE_USERNAME = "your-kaggle-username"  # ⚠️ CHANGE THIS
REQUEST_DATASET = f"{KAGGLE_USERNAME}/voiceover-requests"
OUTPUT_DATASET = f"{KAGGLE_USERNAME}/voiceover-outputs"

# API Keys
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

# Voice mapping
VOICE_MAP = {
    "Kore": "Kore",
    "Zephyr": "Zephyr",
    "Puck": "Puck",
    "Charon": "Charon",
    "Fenrir": "Fenrir",
    "Aoede": "Aoede"
}

# Model mapping
MODEL_MAP = {
    "Flash": "gemini-2.5-flash-preview-tts",
    "Pro": "gemini-2.5-pro-preview-tts"
}

# API Key Manager
class APIKeyManager:
    def __init__(self, keys):
        self.all_keys = keys.copy()
        self.current_pool = []
        self.index = 0
        self.consecutive_failures = 0
        self.lock = threading.Lock()
        self.failed_keys = set()
    
    def initialize(self):
        with self.lock:
            self.current_pool = self.all_keys.copy()
            random.shuffle(self.current_pool)
            self.index = 0
            self.consecutive_failures = 0
            self.failed_keys.clear()
            print(f"🔑 Initialized with {len(self.current_pool)} API keys")
    
    def get_next_key(self):
        with self.lock:
            if not self.current_pool:
                return None
            key = self.current_pool[self.index % len(self.current_pool)]
            self.index += 1
            return key
    
    def mark_failure(self, key):
        with self.lock:
            self.failed_keys.add(key)
            self.consecutive_failures += 1
            if self.consecutive_failures >= 3:
                print("⚠️ 3 consecutive failures - Re-randomizing API pool...")
                random.shuffle(self.current_pool)
                self.index = 0
                self.consecutive_failures = 0
    
    def mark_success(self):
        with self.lock:
            self.consecutive_failures = 0

key_manager = APIKeyManager(API_KEYS)

def save_audio_file(filename, audio_bytes):
    try:
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes(audio_bytes)
        return True
    except Exception as e:
        print(f"❌ Error saving audio: {e}")
        return False

def generate_audio(text, voice, model):
    key_manager.initialize()
    
    for attempt in range(10):
        api_key = key_manager.get_next_key()
        if not api_key:
            return None
        
        try:
            print(f"🔄 Attempt {attempt + 1} with key {api_key[:20]}...")
            
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=MODEL_MAP.get(model, "gemini-2.5-flash-preview-tts"),
                contents=f"Say: {text}",
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=VOICE_MAP.get(voice, "Kore")
                            )
                        )
                    )
                )
            )
            
            audio_data = response.candidates[0].content.parts[0].inline_data.data
            print(f"✅ Success on attempt {attempt + 1}")
            key_manager.mark_success()
            return audio_data
            
        except Exception as e:
            print(f"❌ Attempt {attempt + 1} failed: {e}")
            key_manager.mark_failure(api_key)
            if "429" in str(e) or "quota" in str(e).lower():
                time.sleep(1)
    
    return None

def check_for_requests():
    try:
        print("📥 Checking for new requests...")
        api.dataset_download_files(
            REQUEST_DATASET,
            path="requests_download",
            unzip=True
        )
        
        requests_found = []
        request_dir = "requests_download"
        
        if os.path.exists(request_dir):
            for filename in os.listdir(request_dir):
                if filename.endswith('.json') and filename.startswith('request_'):
                    filepath = os.path.join(request_dir, filename)
                    try:
                        with open(filepath, 'r') as f:
                            data = json.load(f)
                            if data.get('status') == 'pending':
                                requests_found.append(data)
                                print(f"📋 Found pending request: {data['id']}")
                    except Exception as e:
                        print(f"⚠️ Error reading {filename}: {e}")
        
        return requests_found
        
    except Exception as e:
        print(f"⚠️ No requests found or error: {e}")
        return []

def process_request(request_data):
    request_id = request_data['id']
    text = request_data['text']
    voice = request_data['voice']
    model = request_data['model']
    
    print(f"\\n{'='*60}")
    print(f"🎙️ Processing Request: {request_id}")
    print(f"📝 Text: {text[:100]}{'...' if len(text) > 100 else ''}")
    print(f"🎤 Voice: {voice}")
    print(f"🤖 Model: {model}")
    print(f"{'='*60}\\n")
    
    audio_data = generate_audio(text, voice, model)
    
    if not audio_data:
        print(f"❌ Failed to generate audio for {request_id}")
        return False
    
    output_filename = f"{request_id}_output.wav"
    if not save_audio_file(output_filename, audio_data):
        print(f"❌ Failed to save audio for {request_id}")
        return False
    
    print(f"✅ Audio saved: {output_filename}")
    return upload_output(output_filename)

def upload_output(output_filename):
    try:
        os.makedirs("outputs_upload", exist_ok=True)
        
        import shutil
        shutil.copy(output_filename, f"outputs_upload/{output_filename}")
        
        metadata = {
            "title": "Voiceover Outputs",
            "id": OUTPUT_DATASET,
            "licenses": [{"name": "CC0-1.0"}]
        }
        
        with open("outputs_upload/dataset-metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        try:
            api.dataset_create_new(
                folder="outputs_upload",
                convert_to_csv=False,
                dir_mode="zip"
            )
            print(f"✅ Created output dataset with {output_filename}")
        except:
            api.dataset_create_version(
                folder="outputs_upload",
                version_notes=f"New output: {output_filename}",
                convert_to_csv=False,
                dir_mode="zip"
            )
            print(f"✅ Updated output dataset with {output_filename}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error uploading output: {e}")
        return False

def main_loop(max_iterations=20, check_interval=10):
    print("🚀 Starting Voiceover Processing Notebook...")
    print(f"📍 Request Dataset: {REQUEST_DATASET}")
    print(f"📍 Output Dataset: {OUTPUT_DATASET}")
    print(f"⚠️ Make sure to update KAGGLE_USERNAME in the code!")
    print(f"\\n⏱️ Checking every {check_interval} seconds for {max_iterations} iterations\\n")
    
    processed_requests = set()
    
    for iteration in range(max_iterations):
        print(f"\\n{'='*60}")
        print(f"🔄 Check Cycle {iteration + 1}/{max_iterations}")
        print(f"{'='*60}")
        
        pending_requests = check_for_requests()
        
        for request_data in pending_requests:
            request_id = request_data['id']
            
            if request_id in processed_requests:
                print(f"⏭️ Skipping already processed: {request_id}")
                continue
            
            success = process_request(request_data)
            
            if success:
                processed_requests.add(request_id)
                print(f"✅ Successfully processed: {request_id}")
            else:
                print(f"❌ Failed to process: {request_id}")
        
        if not pending_requests:
            print("📭 No pending requests found")
        
        if iteration < max_iterations - 1:
            print(f"\\n⏳ Waiting {check_interval} seconds before next check...")
            time.sleep(check_interval)
    
    print(f"\\n{'='*60}")
    print(f"✅ Processing complete! Processed {len(processed_requests)} requests")
    print(f"{'='*60}")

# Start the processing loop
main_loop(max_iterations=20, check_interval=10)
"""
    
    # Create notebook with code as a single cell
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": complete_code
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
