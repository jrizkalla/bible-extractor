import roman
to_roman = roman.toRoman
from_roman = roman.fromRoman

_greek_names = {
    "josue": "Joshua",
    "kings i": "Samuel I",
    "kings ii": "Samuel II",
    "kings iii": "Kings I",
    "kings iv": "Kings II",
    "paralipomenon i": "Chronicles I",
    "paralipomenon ii": "Chronicles II",
    "esdras i": "Ezra",
    "esdras ii": "Nehemiah",
    "tobias": "Tobit",
    "canticles": "Solomon",
    "isaias": "Isaiah",
    "jeremias": "Jeremiah",
    "ezechiel": "Ezeckiel",
    "osee": "Hosea",
    "abdias": "Obadiah",
    "jonas": "Jonah",
    "micheas": "Micah",
    "habacuc": "Habakkuk",
    "sophonias": "Zephaniah",
    "aggeus": "Haggai",
    "zacharias": "Zachariah",
    "malachias": "Malachi",
}

def fix_book_name(name: str) -> str:
    """
    Fix Bible book names so they're consistent among different Bibles.
    
    Conversions:
    
        - Convert <number> <name> to <name> <number in roman numerals>
        - Convert <roman numeral> <name> to <name> <roman numeral>
        - Convert Greek names to normal ones (e.g Josue -> Joshua)

    >>> fix_book_name("3 Kings")
    'Kings III'
    >>> fix_book_name("2 Esdras")
    'Nehemiah'
    
    """
    
    name = name.strip()
    try:
        # is it <num> <name>?
        num_str, partial_name = name.split(" ")
        num = int(num_str)
        name = f"{partial_name} {to_roman(num)}"
    except ValueError:
        # is it <roman> <name>?
        try:
            num_str, partial_name = name.split(" ")
            num = from_roman(num_str.upper())
            name = f"{partial_name} {to_roman(num)}"
        except (ValueError, roman.InvalidRomanNumeralError):
            # nope, do nothing to the name
            pass
    
    try:
        return _greek_names[name.lower()]
    except KeyError:
        return name
