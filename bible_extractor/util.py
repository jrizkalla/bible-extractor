from roman import toRoman as to_roman

def fix_book_name(name: str) -> str:
    """
    Fix Bible book names so they're consistent among different Bibles.
    
    Conversions:
    
        - Convert <number> <name> to <name> <number in roman numerals>
        - Convert Greek names to normal ones (TODO)

    >>> fix_book_name("3 Kings")
    'Kings III'
    
    """
    try:
        num_str, name = name.split(" ")
        num = int(num_str)
    except ValueError: return name
    return f"{name} {to_roman(num)}"
