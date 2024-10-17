"""
app.py

This file serves as the main entry point for the application.
"""
import streamlit as st

from api_call import (
    LectureNote,
    get_response,
    create_dynamic_lecture_note,
    get_lecture_note_md
)
from utils import (
    speech_to_text,
    split_audio,
    get_headings
)
from prompts import (
    user_message_lecture_note_fn,
    user_message_clean_fn,
    SYSTEM_PROMPT_get_lecture_note,
    SYSTEM_PROMPT_get_clean
)

st.set_page_config(layout="wide")
st.title("Lecture Note Generation")

if "transcription" not in st.session_state:
    st.session_state.transcription = None

if "lecture_note" not in st.session_state:
    st.session_state.lecture_note = None

col1, col2 = st.columns(2)

completed = False  # Default value
downloaded = True

with col1:
    st.header("Audio :loud_sound:")
    audio_file = st.file_uploader("Upload audio file", type=["mp3", "m4a", "mpeg"])

    # Transcribe audio if an audio file is uplaoded
    if audio_file is not None:
        audio_file_size_mb = audio_file.size / (1024 * 1024)

        if st.button("Transcribe"):
            box = st.empty()

            try:
                with st.spinner("Transcribing audio - this takes about 5 to 10 minutes..."):

                    # Split the audio into smaller segments
                    # If audio file size is more than 20MB, recursively split the audio into 20MB each before transcribing
                    segments = None
                    if audio_file_size_mb > 20:
                        segments = split_audio(audio_file)

                    # Iterate through segments to get the transcription if segments exist
                    if segments is not None:
                        raw_transcription = ""
                        for segment in segments:

                            # Pass the segment to the speech-to-text function
                            segment_transcription = speech_to_text(segment)
                            raw_transcription += segment_transcription  # Concatenate all the segment transcriptions

                    else:
                        # If do not need to slice audio, just transcibe per normal
                        raw_transcription = speech_to_text(audio_file)

                    USER_MESSAGE_get_clean = user_message_clean_fn(raw_transcription)
                    clean_transcription = get_response(SYSTEM_PROMPT_get_clean, USER_MESSAGE_get_clean, structured_output=None, box=box)  # will print response
                    st.session_state.transcription = raw_transcription  # Use raw transcript to generate lecture note

            except:
                st.warning("Unexpected error occurred. Please try again in ~ 1 minute.", icon="⚠️")
                st.stop()

            st.success(":white_check_mark: Successfully transcripted and cleaned!")

    # Upload an example of a lecture note to feed to system
    st.header("Lecture Note Headings")
    headings_string = st.text_area("Write the headings (comma-separated) you'd like to include in your lecture note (e.g., heading 1, heading 2,...) **(optional)**", height=100)

    st.header("Additional Details")
    with st.container(border=True):
        st.subheader("Raw Notes")
        lecture_title = st.text_input("Lecture Title **(required)**")
        date_of_lecture = st.text_input("Date of Lecture (DD/MM/YYYY)")
        lecturer_name = st.text_input("Name of Lecturer")
        course_name = st.text_input("Course Name")
        lecture_outline = st.text_area("Lecture Outline")
        key_takeaways = st.text_area("Key Takeaways and Important Points Discussed")

        st.subheader("Additional Notes")
        additional_notes = st.text_area("Any supplementary information or details mentioned during the lecture")

    raw_notes = f"""
        Lecture Title: {lecture_title},
        Date of Lecture: {date_of_lecture},
        Lecturer Name: {lecturer_name},
        Course Name: {course_name},
        Lecture Outline: {lecture_outline},
        Key Takeaways: {key_takeaways}
        """

    # if `get_lecture_note` button is clicked, run the user_message_fn
    get_lecture_note = st.button("Generate lecture note")

with col2:
    st.header("Generated Lecture Note :page_facing_up:")

    if get_lecture_note:

        box = st.empty()

        # If Audio file is uploaded
        if audio_file is not None:

            # Check if transcription is made if an audio file has been uploaded
            if st.session_state.transcription is not None:

                USER_MESSAGE_get_lecture_note = user_message_lecture_note_fn(
                    transcript=st.session_state.transcription,
                    raw_notes=raw_notes,
                    additional_notes=additional_notes
                )

                # An example was given, need to use a different system prompt
                if headings_string != "":
                    # If there is a desired sample to follow
                    headings_list = get_headings(headings_string)
                    # Pass the headings as attributes into the class
                    LectureNoteExample = create_dynamic_lecture_note(headings_list)

                    # Getting the structure of the lecture note (if headings present) Use lecture note example in system prompt
                    lecture_note = get_response(
                        SYSTEM_PROMPT=SYSTEM_PROMPT_get_lecture_note,
                        USER_MESSAGE=USER_MESSAGE_get_lecture_note,
                        structured_output=LectureNoteExample
                    )
                    lecture_note_string = str(lecture_note)
                    lecture_note_md = get_lecture_note_md(lecture_note_string, box)

                # No example was given
                else:
                    lecture_note = get_response(
                        SYSTEM_PROMPT=SYSTEM_PROMPT_get_lecture_note,  # Use standard example in system prompt
                        USER_MESSAGE=USER_MESSAGE_get_lecture_note,
                        structured_output=LectureNote
                    )
                    lecture_note_string = str(lecture_note)
                    lecture_note_md = get_lecture_note_md(lecture_note_string, box)

                st.session_state.lecture_note = lecture_note_md
                completed = True

                # Clear st.session_state.transcription
                st.session_state.transcription = None

            else: # Transcription is not done yet
                st.warning("⚠️ Please transcribe the audio audio file before generating the lecture note.")

        # If no audio file is being uploaded: transcription=None
        else:
            USER_MESSAGE_get_lecture_note = user_message_lecture_note_fn(
                transcript=None,
                raw_notes=raw_notes,
                additional_notes=additional_notes
            )

            # An example was given, need to use a different system prompt
            if headings_string != "":
                # If there is a desired sample to follow
                headings_list = get_headings(headings_string)
                # Pass the headings as attributes into the class
                LectureNoteExample = create_dynamic_lecture_note(headings_list)

                lecture_note = get_response(
                    SYSTEM_PROMPT=SYSTEM_PROMPT_get_lecture_note,
                    USER_MESSAGE=USER_MESSAGE_get_lecture_note,
                    structured_output=LectureNoteExample
                )
                lecture_note_string = str(lecture_note)
                lecture_note_md = get_lecture_note_md(lecture_note_string, box)

            # No example was given
            else:
                lecture_note = get_response(
                    SYSTEM_PROMPT=SYSTEM_PROMPT_get_lecture_note,  # Use standard example in system prompt
                    USER_MESSAGE=USER_MESSAGE_get_lecture_note,
                    structured_output=LectureNote
                )
                lecture_note_string = str(lecture_note)
                lecture_note_md = get_lecture_note_md(lecture_note_string, box)

            st.session_state.lecture_note = lecture_note_md
            completed = True

            # Clear st.session_state.transcription
            st.session_state.transcription = None

    if st.session_state.lecture_note and st.download_button(
        "Download lecture note",
        data=st.session_state.lecture_note,
        file_name="lecture_note.txt"
    ):
        st.markdown(st.session_state.lecture_note)
        completed = False
