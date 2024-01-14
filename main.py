# main.py
from pathlib import Path

import streamlit as st
import requests
import os
import time
import development as dev
from io import StringIO


def main(myclient):
    st.set_page_config(page_title="AI Whisperers", page_icon="📽️")
    st.title("AI Whisperers")
    user_input_link = st.text_input("Enter a Link from a Newspaper:")
    # Display the link after it's entered
    if user_input_link:
        article = dev.get_article(user_input_link)
        st.success(f"Link successfully added!")
        summary_1 = dev.create_summary(myclient, article)
        summary_2 = dev.create_summary(myclient, article)
        summary_3 = dev.create_summary(myclient, article)

        summaries_dict = {
            'summary_1': summary_1,
            'summary_2': summary_2,
            'summary_3': summary_3,
        }
        st.markdown("## Summaries")

        # Display summaries using expander
        for i in range(1, 4):
            summary_key = f'summary_{i}'
            with st.expander(f"Summary {i}", expanded=True):
                st.write(summaries_dict[summary_key])

        # Allow the user to select their favorite summary
        favorite_summary = st.selectbox(
            "Select your favorite summary:",
            ('Summary 1', 'Summary 2', 'Summary 3')
        )

        if favorite_summary:
            st.write("You selected:", favorite_summary)
            if favorite_summary == 'Summary 1':
                sum_fav = summaries_dict['summary_1']
            elif favorite_summary == 'Summary 2':
                sum_fav = summaries_dict['summary_2']
            else:
                sum_fav = summaries_dict['summary_3']

        st.markdown("## Upload your video")
        uploaded_file = st.file_uploader("Upload a video", type=['mp4', 'mp3'])
        # Directory where the file will be temporarily saved
        temp_dir = "tempDir"

        # Ensure temp_dir exists
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        if uploaded_file is not None:
            # Path to save the uploaded file
            temp_file_path = os.path.join(temp_dir, uploaded_file.name)

            # Write the file to the temporary directory
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("File saved!")
            st.video(temp_file_path)

            with open(temp_file_path, "rb") as audio_file:
                transcript = myclient.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )

                with st.expander('Video Transcript'):
                    st.write(transcript.text)

                seconds = st.selectbox("Select the video duration in seconds:", ('30', '60'))
                if seconds == '30':
                    s = 30
                else:
                    s = 60
                if st.button('Generate Script', type='primary'):
                    script_1 = dev.generate_script(transcript.text, article, s, myclient)
                    script_2 = dev.generate_script(transcript.text, article, s, myclient)
                    script_3 = dev.generate_script(transcript.text, article, s, myclient)

                    script_dicc = {
                        'script_1': script_1,
                        'script_2': script_2,
                        'script_3': script_3,
                    }
                    print(script_dicc)
                    st.markdown("## Scripts")
                    for i in range(1, 4):
                        script_key = f'script_{i}'
                        with st.expander(f"Script {i}", expanded=True):
                            st.write(script_dicc[script_key])

                    favorite_script = st.selectbox(
                        "Select your favorite script:",
                        ('Script 1', 'Script 2', 'Script 3')
                    )

                    if favorite_script:
                        st.write("You selected:", favorite_script)
                        if favorite_script == 'Script 1':
                            script_fav = script_dicc['script_1']
                        elif favorite_summary == 'Script 2':
                            script_fav = script_dicc['script_2']
                        else:
                            script_fav = script_dicc['script_3']

                    # Button to convert text to speech

                    if script_fav:
                        # Call your text_to_audio function
                        dev.text_to_audio(myclient, script_fav)

                        # Assuming the function saves the audio file in the same directory as the script
                        audio_file = Path(__file__).parent / "speech.mp3"

                        # Display audio player
                        if audio_file.is_file():
                            audio_bytes = open(audio_file, "rb").read()
                            st.audio(audio_bytes, format="audio/mp3")
                        else:
                            st.error("Error: Audio file not found.")


if __name__ == "__main__":
    my_client = dev.init_openai()
    main(my_client)
