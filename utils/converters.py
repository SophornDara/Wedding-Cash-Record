"""Text and number conversion utilities."""


def khmer_to_arabic(text):
    """Converts Khmer numerals (១២៣) to standard numbers (123).
    
    Args:
        text: Input text containing Khmer numerals
        
    Returns:
        str: Converted text with Arabic numerals
    """
    if not text:
        return ""
    
    replacements = {
        '០': '0', '១': '1', '២': '2', '៣': '3', '៤': '4',
        '៥': '5', '៦': '6', '៧': '7', '៨': '8', '៩': '9',
        ',': '', ' ': ''  # Remove commas and spaces
    }
    
    text_str = str(text)
    for k, v in replacements.items():
        text_str = text_str.replace(k, v)
        
    return text_str
