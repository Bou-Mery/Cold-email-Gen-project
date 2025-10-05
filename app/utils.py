import re

def clean_text(text):
    """
    Cleans a text by removing HTML tags, URLs, special characters,
    and extra whitespace.
    """
    # Remove HTML tags
    text = re.sub(r'<[^>]*?>', '', text)
    
    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    
    # Remove non-alphanumeric characters (except spaces)
    text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
    
    # Replace multiple consecutive spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Trim leading and trailing spaces
    text = text.strip()
    
    return text
