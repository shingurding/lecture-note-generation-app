"""
api_call.py

This file contains functions that handle the management of prompts for interacting with various APIs.
"""
import os
import streamlit as st
from typing import List
from openai import AzureOpenAI
from pydantic import BaseModel, create_model

from config import (
    API_VERSION,
    MODEL,
    TEMPERATURE,
    SEED
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

class LectureNote(BaseModel):
    """
    Default lecture note structure
    """
    lecture_title: str
    date: str
    lecturer: str
    course_name: str
    lecture_outline: str

    # Main sections of the lecture note
    introduction: str
    key_concepts: List[str]
    examples_or_case_studies: List[str]
    key_takeaways: List[str]
    discussion_points: List[str]
    critical_insights: List[str]
    follow_up_actions: List[str]

    additional_notes: str

def create_dynamic_lecture_note(headings: List[str]) -> BaseModel:
    """
    Creates a pydantic model that uses BaseModel.

    Args:
    - headings (List[str]): A list of headings to be used as attributes in the model.

    Returns:
    BaseModel: A dynamic Pydantic model with fields corresponding to the provided headings.
    """
    # Define the dynamic fields using `create_model`
    fields = {heading: (str, None) for heading in headings}  # Create a field for each heading
    LectureNoteExample = create_model('LectureNoteExample', **fields)
    return LectureNoteExample

def get_response(SYSTEM_PROMPT, USER_MESSAGE, structured_output, box=None):
    """
    Function to get a response from the chat model and stream the result.

    Args:
    - SYSTEM_PROMPT (str): The system message providing context to the model
    - USER_MESSAGE (str): The user's message to which the model will respond to
    - box: A UI element to display streaming results

    Returns:
    str: The full respond accumulated from the streaming content
    """
    # Response for clean transcription
    if structured_output == None:
        response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_MESSAGE}
        ],
        temperature=TEMPERATURE,
        seed=SEED,
        stream=True
        )
        results = ""
        for chunk in response:
            if chunk.choices[0].delta.content != "":
                try:
                    results += chunk.choices[0].delta.content
                    box.info(results)
                except TypeError:
                    pass
        return results

    # Response for lecture note generation
    else:
        response = client.beta.chat.completions.parse(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_MESSAGE}
            ],
            temperature=TEMPERATURE,
            seed=SEED,
            response_format=structured_output
        )

        return response.choices[0].message.parsed

def get_lecture_note_md(lecture_note, box):
    """
    Converts the string into markdown format

    Args:
    - lecture_note (str): The string to be converted to markdown format
    - box: A UI element to display streaming results

    Returns:
    str: The full respond accumulated from the streaming content
    """
    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system",
             "content": "You are a markdown formatter. Please take the provided string and format it into markdown. "
            "Each attribute should be treated as a heading, and the corresponding text should follow as a paragraph. "
            "Use appropriate markdown syntax for headings (e.g., `#` for H1, `##` for H2, etc.). "
            "Ensure the final output is well-structured and easy to read."},
            {"role": "user",
             "content": lecture_note}
        ],
        stream=True
    )
    results = ""
    for chunk in response:
        if chunk.choices[0].delta.content != "":
            try:
                results += chunk.choices[0].delta.content
                box.info(results)
            except TypeError:
                pass
    return results
