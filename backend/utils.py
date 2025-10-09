import re

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)  # collapse multiple spaces
    text = re.sub(r'Page \d+ of \d+', '', text)  # remove footer markers
    return text.strip()
