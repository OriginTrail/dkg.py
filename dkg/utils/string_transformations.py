def snake_to_camel(string: str) -> str:
    splitted_string = string.split('_')
    return splitted_string[0] + ''.join(token.capitalize() for token in splitted_string[1:])
