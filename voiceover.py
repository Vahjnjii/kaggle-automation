import json
import os
from datetime import datetime

os.environ['KAGGLE_USERNAME'] = os.environ.get('KAGGLE_USERNAME', '')
os.environ['KAGGLE_KEY'] = os.environ.get('KAGGLE_KEY', '')

from kaggle.api.kaggle_api_extended import KaggleApi

def create_notebook():
    api = KaggleApi()
    api.authenticate()
    
    username = os.environ.get('KAGGLE_USERNAME', 'shreevathsbbhh')
    notebook_slug = "gemini-tts-processor-gdrive"
    
    metadata = {
        "id": f"{username}/{notebook_slug}",
        "title": "Gemini TTS Processor (Google Drive)",
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
    
    complete_code = """# Install required packages
!pip install -q google-generativeai pydub google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

import json
import os
import time
import wave
import random
from datetime import datetime
from google import genai
from google.genai import types
from pydub import AudioSegment
import threading
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

# Configuration
REQUEST_FOLDER_ID = "1gm2LWQKiVNJxfghgvrtGdOeC3REX2GEm"
OUTPUT_FOLDER_ID = "1Tu0CphcQl8ImQ5Lfl1peTzlGbezJ9pLt"
OUTPUT_WORKING_PATH = "/kaggle/working/outputs"

# Service Account Credentials
SERVICE_ACCOUNT_INFO = {
    "type": "service_account",
    "project_id": "keen-rhino-401606",
    "private_key_id": "5983a6e48566f24b95047fcb1cf985c4be4c6b88",
    "private_key": "-----BEGIN PRIVATE KEY-----\\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDD/RDCXgoZJUU0\\nMaEIwOI3HbWMjbWLlOFo2q547fGGlYcLUdVpEufVOAXJz0Q+i9fnYJBecOANQ0G8\\nPB7OIIrrtgxfEXYuAOgaeCvDdhVCHRQVnV4SQ1KZ1a9RyZquoJfwcjM7dh9uauyh\\n/IHyhaV8v0SRmwcsrlBJaBrqjAVsz5ZO4H5C2zvglYtH3ACN9a4Xcj4sl+KmpadZ\\nt4uhF4GI67H1XkUcERJWCgGnxd7aezcSJltFtBbhZMmtzr3WGixxFro69iO76kqi\\nx/uxAv3/7VYFZY2YM7mc8Squtuyndvq1dwoQ5pkzC/fQNEYfZG9V0vOOe0wrpzks\\nMyYmfXuRAgMBAAECggEACXfKPXmJh1lzlGfpXaDjzMHUqWuXH50bnpMh5pmoF1ZV\\n5cgYRTEynexM60jmBReAYJ8bmlRdnoZnQI6u9kpAK87pnhYb3XERxWWUx6aGtGDv\\nPXQSvVMfRGs8Qvk4TcNYU7dQnkjAj/b+Y3ztUif+rJ4Y0+fnWtM48bLjyfzlrjHr\\nbfl8KUYSV0ZNN5VPWRNvxmlqhUHpRVsDKOpnmuOtLr85m4nxxM+9MFrSRv2jJib+\\nYjivTL/JOJGzSHs7MAIpns15dhm97C3uHA8Jlt1WNTzatQK4n9y4K9l3d4Yg7Zz5\\nJi5AqGbi2gF7sTtUtUCzioXWQv2NoUOy7LTduD5PGQKBgQDjd9sLPzdVoXs56kG8\\nBzLB2S2O+h4gv5tYJypPSnx2weez6/w6NCoSdL6MJsweN8HCt1A3K/N4wrXdG9+9\\nNFESJ72ukVdv5rHMd+aB0p/y0CUgMa9G6HltNYHyWUmlGeBgB9p3/dD/6/sXPsEU\\nONC7xzRRgZolPomUohSKdbE4MwKBgQDckmD4iDr5tJ65rud+Y+21mD/B5usURsEr\\nyXhU+f/JaLNtj3vP0U00l7ZNvH6scBhW/E5/hGYOzwsdjlWPAWnhcgMm3ZiOKK3g\\nfjwRFUvUzYh/a3MxSt5b4gvRkABoFE69WrLR5nysczAc/jQhMk8RlAGz7yNoCFa2\\nx+mxHAPJKwKBgB6D/cbMfEfomfdzDc6DyLNox0vfEhuimNyCpJJuk7P633KrvfKw\\n/NPtBYMX0VpccIoGvaQpKUiSFoPLMYDYe+fLnQ7GQMyqTj/39dyEvSB9+/0NrU39\\n8gxMmVpB0Ddt+UPoyc4/JsKujcjYil6EILyQRNyKXnuQoDRoagkJMPUxAoGBANDh\\nMkHKSQdV/AZd004G9gLFpoNK2g4+nwqHZZQbmBa1N04m1hpM3G9UyMi/G7rTAMnH\\nb9Mkn72gZqdbtjySGyHrZX611ZWygk8ZXGrVHxXsejoomFLy0rZyz7xqQWhO6u44\\n6SULv79T6hlaxiU1zlkYL7ClY4NOekfn86/Mlu03AoGAX3ChcsihroZNX2axLF2J\\n/pDK5oS6o3lFssW5YujCi43SoLyBssfF9fmtxqSpDboHBP8wSXCu/q9yvYZGWQLC\\nOSej4B5iGGCcvBrpyIJTwc693/j5brcsU139k7CH+QXa9GMMVsdTdVHA9I4FnJae\\n18fR6jmhVZLGumDdlDeszbM=\\n-----END PRIVATE KEY-----\\n",
    "client_email": "tts-automation@keen-rhino-401606.iam.gserviceaccount.com",
    "client_id": "101032843980915693986",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/tts-automation%40keen-rhino-401606.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

# API Keys for Gemini
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

VOICE_MAP = {"Kore": "Kore", "Zephyr": "Zephyr", "Puck": "Puck", "Charon": "Charon", "Fenrir": "Fenrir", "Aoede": "Aoede"}
MODEL_MAP = {"Flash": "gemini-2.5-flash-preview-tts", "Pro": "gemini-2.5-pro-preview-tts"}

# Initialize Google Drive API
def get_drive_service():
    credentials = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO,
        scopes=['https://www.googleapis.com/auth/drive']
    )
    return build('drive', 'v3', credentials=credentials)

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
                print("⚠️ Re-randomizing API pool...")
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
            print(f"🔄 Attempt {attempt + 1}")
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
            print(f"✅ Success")
            key_manager.mark_success()
            return audio_data
            
        except Exception as e:
            print(f"❌ Failed: {e}")
            key_manager.mark_failure(api_key)
            time.sleep(1)
    
    return None

def upload_output_to_drive(output_file, request_id):
    try:
        service = get_drive_service()
        
        output_filename = f"{request_id}_output.wav"
        file_metadata = {
            'name': output_filename,
            'parents': [OUTPUT_FOLDER_ID]
        }
        
        media = MediaFileUpload(output_file, mimetype='audio/wav')
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        print(f"✅ Uploaded to Drive: {file.get('id')}")
        return True
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

def download_request_from_drive(file_id):
    try:
        service = get_drive_service()
        request = service.files().get_media(fileId=file_id)
        
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        fh.seek(0)
        return json.load(fh)
    except Exception as e:
        print(f"❌ Download error: {e}")
        return None

def check_for_requests():
    try:
        print("📥 Checking for requests in Google Drive...")
        service = get_drive_service()
        
        # List all JSON files in request folder
        query = f"'{REQUEST_FOLDER_ID}' in parents and mimeType='application/json' and trashed=false"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])
        
        requests_found = []
        for file in files:
            if file['name'].startswith('request_') and file['name'].endswith('.json'):
                request_data = download_request_from_drive(file['id'])
                if request_data and request_data.get('status') == 'pending':
                    request_data['file_id'] = file['id']  # Store for potential deletion
                    requests_found.append(request_data)
                    print(f"📋 Found: {request_data['id']}")
        
        return requests_found
    except Exception as e:
        print(f"⚠️ Error: {e}")
        return []

def process_request(request_data):
    request_id = request_data['id']
    text = request_data['text']
    voice = request_data['voice']
    model = request_data['model']
    
    print(f"\\n{'='*60}")
    print(f"🎙️ Processing: {request_id}")
    print(f"📝 Text: {text[:100]}")
    print(f"{'='*60}\\n")
    
    audio_data = generate_audio(text, voice, model)
    
    if not audio_data:
        print(f"❌ Failed to generate")
        return False
    
    os.makedirs(OUTPUT_WORKING_PATH, exist_ok=True)
    output_filename = f"{OUTPUT_WORKING_PATH}/{request_id}_output.wav"
    
    if not save_audio_file(output_filename, audio_data):
        print(f"❌ Failed to save")
        return False
    
    print(f"✅ Saved: {output_filename}")
    
    if not upload_output_to_drive(output_filename, request_id):
        print(f"❌ Failed to upload")
        return False
    
    return True

def main_loop(max_iterations=20, check_interval=10):
    print("🚀 Starting Processing Notebook (Google Drive)...")
    print(f"📁 Request Folder: {REQUEST_FOLDER_ID}")
    print(f"📁 Output Folder: {OUTPUT_FOLDER_ID}\\n")
    
    processed_requests = set()
    
    for iteration in range(max_iterations):
        print(f"\\n🔄 Check {iteration + 1}/{max_iterations}")
        
        pending_requests = check_for_requests()
        
        for request_data in pending_requests:
            request_id = request_data['id']
            
            if request_id in processed_requests:
                print(f"⭐️ Already processed: {request_id}")
                continue
            
            success = process_request(request_data)
            
            if success:
                processed_requests.add(request_id)
                print(f"✅ Done: {request_id}")
            else:
                print(f"❌ Failed: {request_id}")
        
        if not pending_requests:
            print("🔭 No pending requests")
        
        if iteration < max_iterations - 1:
            print(f"⏳ Waiting {check_interval}s...")
            time.sleep(check_interval)
    
    print(f"\\n✅ Complete! Processed {len(processed_requests)} requests")

main_loop(max_iterations=20, check_interval=10)
"""
    
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
    
    with open('notebook.ipynb', 'w') as f:
        json.dump(notebook, f, indent=2)
    
    with open('kernel-metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"📤 Updating notebook: {metadata['title']}")
    api.kernels_push('.')
    print(f"✅ Success! View at: https://www.kaggle.com/code/{metadata['id']}")

if __name__ == "__main__":
    create_notebook()
