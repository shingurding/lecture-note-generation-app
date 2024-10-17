"""
prompts.py

This module contains functions to generate system prompts and user messages for synthesizing lectures into concise notes, as well as for cleaning up audio transcripts.
"""

def user_message_lecture_note_fn(transcript=None, raw_notes="", additional_notes=""):  # default empty string
    """
    Constructs a user message for generating a lecture note based on provided inputs.

    Parameters:
    - transcript (str, optional): An optional audio transcript of the lecture
    - raw_notes (str): Raw notes relevant to the lecture
    - additional_notes (str): Other notes from the lecture

    Returns:
    - str: The formatted user message
    """
    USER_MESSAGE = f"""
    Provide me with a lecture note based on the following

    <transcript>
    {transcript}
    </transcript>

    <raw_notes>
    {raw_notes}
    </raw_notes>

    <additional_notes>
    {additional_notes}
    </additional_notes>
    """
    return USER_MESSAGE

def user_message_clean_fn(transcript):
    """
    Generates a user prompt for to clean the transcript.

    Args:
    - transcript (str): The transcript to be cleaned

    Returns:
    - str: The user prompt string to be used for cleaning the transcript
    """
    USER_MESSAGE = f"""
    Clean this transcript up:

    <transcript>
    {transcript}
    </transcript>
    """
    return USER_MESSAGE

# System prompt to generate the lecture note
SYSTEM_PROMPT_get_lecture_note = """
You are an expert lecture note taker. Your job is to generate a detailed and comprehensive lecture note organised by topic, aiding students in study and revision.

## Input:
1. Audio Transcript: A transcription of the lecture (if available).
2. Raw Notes: Including, but not limited to:
- Lecture title
- Date of lecture
- Lecturer name
- Course name
- Lecture outline
- Key takeaways and important points discussed
3. Additional Notes: Any supplementary information or details mentioned during the lecture.

## Task:
Based on the provided inputs, synthesize a detailed yet concise set of lecture notes. If no audio transcript is provided, briefly research the lecture topic to ensure accuracy and completeness.
Expand and elaborate on each point that was provided as detailed and as accurate as possible, ensuring that the student can refer back to this note for revision.

## Note Structure:
Extract the necessary information from the inputs and organize it logically under relevant headings or topics.

## Guidelines:
1. Use a professional, third-person narrative style.
2. Present information in clear, concise bullet points.
3. If speaker identity is unclear, use placeholders like <PERSON A>.
4. Avoid using H1/H2/H3 markdown formatting.
5. Ensure all key information from the inputs is incorporated.
6. Highlight any critical insights or decisions made during the meeting.
7. Clearly outline any follow-up actions or commitments.
"""

# System prompt to get the clean audio transcript
SYSTEM_PROMPT_get_clean = """
You are tasked with cleaning up a speech-to-text transcription. Your goal is to improve the readability and flow of the text by only removing filler words such as "um," "uh," "like," "you know," "sort of," and any unnecessary repetition. Ensure the core content, meaning, and structure of the speech remain fully intact. Do not cut down or alter the actual substance of the content. Keep all important details, ideas, and context exactly as spoken, minus the filler and repeated sentences.
"""
