import re

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
             "content": "You are a summary tool and you need to create a detail summary between 50 to 100 words. "
                        "You have to give 3 different summaries with exactly this format"
                        " * summary_1:, * summary_2:, * summary_3"
                        "That's an example of how the format should be. Please include * just before summary. It is mandatory "
                        "and essential to have this exact format so I can work on it later."
                        "* summary_1: "
                        "* summary_2: "
                        "* summary_3: "},
            {"role": "user", "content": f"Create a summary of this text{article}"}
        ]
    )
    return response


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
    prompt = f"Generate 3 scripts based on the following inputs: \n\n" \
             f"Transcript Text: {transcript_text}\n" \
             f"Article Summary: {article_text}\n" \
             f"Video Duration: {video_seconds} seconds\n\n" \
             "The scripts should follow these guidelines: " \
             "1. Style Replication: Use language, sentence structure, and unique features from the transcript text. " \
             "2. Tone Emulation: Reflect the emotional tone of the transcript. " \
             "3. Creative Expansion: Add new ideas and narratives that align with the themes of the article summary. " \
             "4. Time Consideration: The content should be appropriate for the specified video duration. " \
             "5. Personality Reflection: Reflect the speaker's personality traits.\n\n" \
             "The format must be: * script_1:, * script_2:, * script_3"\
             "That's an example of how the format should be. Please include * just before script. It is mandatory and essential to have this exact format so I can work on it later." \
             "* script_1: "\
             "* script_2: " \
             "* script_3: "

    response = myclient.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": "Please generate the scripts."}
      ]
    )
    return response.choices[0].message.content

def generate_script_dict(text):
    """
    Generates a dictionary of scripts from a given text.

    Parameters:
    text (str): A string containing scripts, each starting with '* script_'.

    Returns:
    dict: A dictionary with each script under a unique key.
    """
    # Splitting the text into separate scripts using '* script_' as a delimiter
    split_scripts = re.split(r'\* script_\d+: ', text)[1:]

    # Initializing an empty dictionary
    scripts = {}

    # Assigning scripts to the dictionary
    for i, script in enumerate(split_scripts):
        key = f'script_{i+1}'
        scripts[key] = script.strip()  # Remove leading/trailing whitespace

    return scripts