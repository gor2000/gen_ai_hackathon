#main.py

import streamlit as st
import requests
import os
import time
import development as dev


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
        st.write(summaries_raw)
        summaries_dict = dev.generate_summary_dict(summaries_raw)
        st.write(summaries_dict['summary_1'])




if __name__ == "__main__":
    my_client = dev.init_openai()
    main(my_client)
