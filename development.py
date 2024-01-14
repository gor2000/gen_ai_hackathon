import re
from pathlib import Path

from newspaper import Article
from openai import OpenAI


def get_article(url):
    article = Article(url)
    article.download()
    article.parse()
    return article.text


def init_openai():
    # Read the API key
    api_key_path = 'files/api/api_key.txt'
    api_org_path = 'files/api/api_org.txt'
    with open(api_key_path, 'r') as file:
        api_key = file.read().strip()

    # Read the API organization key
    with open(api_org_path, 'r') as file:
        api_key2 = file.read().strip()
    myclient = OpenAI(api_key=api_key, organization=api_key2)
    return myclient


def create_summary(myclient, article):
    response = myclient.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are a summary tool and you need to create a detail summary between 50 to 100 words. "},
            {"role": "user", "content": f"Create a summary of this text{article}"}
        ]
    )
    return response.choices[0].message.content


def generate_summary_dict(text):
    """
    Generates a dictionary of summaries from a given text.

    Parameters:
    text (str): A string containing summaries, each starting with 'summary_'.

    Returns:
    dict: A dictionary with each summary under a unique key.
    """
    # Splitting the text into separate summaries using 'summary_' as a delimiter
    split_summaries = re.split(r'\* summary_\d+: ', text)[1:]
    # Initializing an empty dictionary
    summaries = {}

    # Assigning summaries to the dictionary
    for i, summary in enumerate(split_summaries):
        key = f'summary_{i + 1}'
        summaries[key] = summary.strip()  # Remove leading/trailing whitespace

    return summaries


def get_transcript(file_path, myclient):
    # speech to text
    # this will take that voice file and turn it back to text

    audio_file = open(file_path, "rb")
    transcript = myclient.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
    print(transcript.text)


def generate_script(transcript_text, article_text, video_seconds, myclient):
    prompt = (
        f"Generate 1 video script based on the provided inputs:\n\n"
        f"Transcript Text: {transcript_text}\n"
        f"Article Summary: {article_text}\n"
        f"Video Duration: {video_seconds} seconds\n\n"
        "Guidelines:\n"
        "1. Style Replication: Mimic language and sentence structure from the transcript.\n"
        "2. Tone Emulation: Match the emotional tone of the transcript.\n"
        "3. Creative Expansion: Incorporate themes from the article summary in a creative way.\n"
        "4. Time Consideration: Ensure the scripts are suitable for the specified video duration.\n"
        "5. Personality Reflection: Capture the speaker's personality traits.\n\n"
        "Output Format:\n"
        "[Script content for the first video based on the guidelines]\n"
    )
    prompt_2 = (f"Create a text ready to say that combines the following news article with the style and personality of the provided transcript. The text should be engaging, lively, and informative.\n\nNews Article:\n{article_text}\n\nTranscript Style:\n{transcript_text}\n\nGenerated Script:"
                f"The text must have between 80 to 100 words.")

    # Replace {transcript_text}, {article_text}, and {video_seconds} with your specific inputs.

    response = myclient.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt_2},
            {"role": "user", "content": "Please generate the scripts."}
        ]
    )
    return response.choices[0].message.content


import re


def generate_script_dict(text):
    """
    Generates a dictionary of scripts from a given text, removing newlines immediately following each script identifier.

    Parameters:
    text (str): A string containing scripts, each starting with '* script_' followed by a number.

    Returns:
    dict: A dictionary with each script under a unique key, with initial newlines removed.
    """
    # Splitting the text into separate scripts using the original pattern
    split_scripts = re.split(r'\* script_\d+: ', text)[1:]

    # Initializing an empty dictionary
    scripts = {}

    # Assigning scripts to the dictionary, removing initial newlines
    for i, script in enumerate(split_scripts):
        key = f'script_{i + 1}'
        # Remove leading newlines and whitespace
        scripts[key] = script.lstrip('\n').strip()

    return scripts


def generate_audio(transcript_text, article_text, myclient, video_seconds=100):
    prompt = (
        f"Generate 1 video script based on the provided inputs:\n\n"
        f"Transcript Text: {transcript_text}\n"
        f"Article Summary: {article_text}\n"
        f"Video number of words: {video_seconds} words\n\n"
        "Guidelines:\n"
        "1. Style Replication: Mimic language and sentence structure from the transcript.\n"
        "2. Tone Emulation: Match the emotional tone of the transcript.\n"
        "3. Creative Expansion: Incorporate themes from the article summary in a creative way.\n"
        "4. Words Consideration: Ensure the scripts are suitable for the specified number of words.\n"
        "5. Personality Reflection: Capture the speaker's personality traits.\n\n"
        "You must create a single line as it were a person talking. Do not add anything but the words of the person talking for the video"
        "Output Format:\n"
        "[Script content for the first video based on the guidelines, excluding any labels like 'Host:' or 'Speaker:']\n"
    )

    prompt_2 = (f"Create a text ready to say that combines the following news article with the style and personality of the provided transcript. The text should be engaging, lively, and informative.\n\nNews Article:\n{article_text}\n\nTranscript Style:\n{transcript_text}\n\nGenerated Script:"
                f"The text must have between 80 to 100 words.")
    # Replace {transcript_text}, {article_text}, and {video_seconds} with your specific inputs.

    response = myclient.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt_2},
            {"role": "user", "content": "Please generate the text ready to say."}
        ]
    )
    return response.choices[0].message.content


def text_to_audio(myclient, speech):
    speech_file_path = Path(__file__).parent / "speech.mp3"
    response = myclient.audio.speech.create(
        model="tts-1",
        voice="shimmer",
        input=speech
    )

    return response.stream_to_file(speech_file_path)
