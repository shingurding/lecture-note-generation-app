"""
utils.py

This file contains utility functions used across the application.
"""
import io
import os
import streamlit as st

from pydub import AudioSegment
from openai import AzureOpenAI

from config import (
    API_VERSION
)

try:
    OAI_API_KEY = st.secrets["OAI_API_KEY"]
    OAI_API_ENDPOINT = st.secrets["OAI_API_ENDPOINT"]
except (KeyError, FileNotFoundError):
    OAI_API_KEY = os.getenv("OAI_API_KEY")
    OAI_API_ENDPOINT = os.getenv("OAI_API_ENDPOINT")

client = AzureOpenAI(
    api_key=OAI_API_KEY,
    api_version=API_VERSION,
    azure_endpoint=OAI_API_ENDPOINT
)

def split_audio(audio_file, max_size_mb=10):
    """s
    Splits an audio file into segments of specified maximum size.

    Args:
    - audio_file (str or file-like object): Path to the audio file or a file-like object (e.g., BytesIO).
    - max_size_mb (int, optional): Maximum size of each segment in megabytes. Default is 10 MB.

    Returns:
    List[io.BytesIO]: A list of audio segments as BytesIO objects, where each segment is less than or equal to the specified max_size_mb.
    """
    audio = AudioSegment.from_file(audio_file)
    max_size_bytes = max_size_mb * (1024 * 1024)
    segments = []
    start_time = 0
    segment_duration = 60 * 30 * 1000 # 60sec * 30min * 1000ms

    while start_time < len(audio):
        # Slice the audio into 30min segments
        segment = audio[start_time:(start_time+segment_duration)] # Slice audio
        segment_bytes = io.BytesIO() # Create buffer to store the audio
        segment_bytes.name = f'segment_{start_time}.mp3' # Need to set the name with the extension
        segment.export(segment_bytes, format='mp3') # Export the sliced audio to buffer
        segment_size = segment_bytes.getbuffer().nbytes # Get the size of the buffer

        # This while loop will run only if the sliced segment is still larger than max_size_byte
        # We reduce the length by 5 minute each time
        while segment_size > max_size_bytes:
            segment_duration -= 5 * 60 * 1000  # Reduce by 5 minutes
            segment = audio[start_time:(start_time + segment_duration)]
            segment_bytes = io.BytesIO()
            segment_bytes.name = f'segment_{start_time}.mp3'
            segment.export(segment_bytes, format='mp3')
            segment_size = segment_bytes.getbuffer().nbytes

        segment_bytes.seek(0)

        # Append the segment to the list as bytes
        segments.append(segment_bytes)
        start_time += len(segment)

    return segments

def speech_to_text(audio_file, language="en"):
    """
    Converts speech in an audio file to text using a speech-to-text service.

    Args:
    - audio_file (str or file-like object): Path to the audio file or a file-like object (e.g., BytesIO).
    - language (str, optional): The language of the audio file. Default is English ("en").

    Returns:
    str: The transcribed text from the audio file.
    """
    transcription = client.audio.transcriptions.create(
        file=audio_file,
        language=language,
        model="whisper-1"
    )
    return transcription.text

def get_headings(lecture_note_example):
    """
    Get the list of headings from the string that was inputted by the user.

    Args:
    - lecture_note_example: A string of all the headings the user want to include in their lecture note

    Returns:
    list: The list of headings
    """
    # Split the comma-separated string to list
    headings_list = lecture_note_example.split(",")
    headings_list = [heading.strip().replace(" ", "_") for heading in headings_list]
    return headings_list
