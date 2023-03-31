def snake_to_camel(string: str) -> str:
    """
    Converts a snake_case string to a camelCase string.

    Args:
        string (str): The snake_case string to be converted.

    Returns:
        str: The converted camelCase string.

    Example:

        snake_to_camel('example_string') returns 'exampleString'
    """
    splitted_string = string.split("_")
    return splitted_string[0] + "".join(
        token.capitalize() for token in splitted_string[1:]
    )
