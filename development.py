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
                        "You have to give 3 different summaries with exactly this format:"
                        "summary_1, summary_2:, summary_1: "},
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
    split_summaries = re.split(r'summary_\d+: ', text)[1:]

    # Initializing an empty dictionary
    summaries = {}

    # Assigning summaries to the dictionary
    for i, summary in enumerate(split_summaries):
        key = f'summary_{i+1}'
        summaries[key] = summary.strip()  # Remove leading/trailing whitespace

    return summaries
