#main.py

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
        response = dev.create_summary(myclient, article)
        summaries_raw = response.choices[0].message.content
        summaries_dict = dev.generate_summary_dict(summaries_raw)
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
                # Print or display the transcription text
                print(transcript.text)
                # Alternatively, display it in the Streamlit app
                st.text(transcript.text)

if __name__ == "__main__":
    my_client = dev.init_openai()
    main(my_client)
