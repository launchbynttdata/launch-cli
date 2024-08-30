import logging

logger = logging.getLogger(__name__)


def recursive_dictionary_merge(a: dict, b: dict, path=[]) -> dict:
    """Merges dictionary 'b' into dictionary 'a', will halt upon encountering a difference in the two dictionaries' values.

    Args:
        a (dict): Dictionary of arbitrary depth
        b (dict): Dictionary of arbitrary depth
        path (list, optional): Mechanism to report on where conflicts arise, no need to set this for external callers. Defaults to [].

    Raises:
        ValueError: Raised when both dictionaries contain a common key with a differing value.

    Returns:
        dict: Modified 'a' dictionary with keys and values merged from 'b'
    """
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                recursive_dictionary_merge(a[key], b[key], path + [str(key)])
            elif a[key] != b[key]:
                raise ValueError(f"Conflict at {'.'.join(path + [str(key)])}")
        else:
            a[key] = b[key]
    return a


def extract_uuid_key(source_data: dict) -> dict:
    """Given a 'source_data' dictionary of arbitrary depth, find and return any 'uuid' keys while retaining the structure
    of the dictionary. If there is not 'uuid' key, an dictionary matching the structure will be returned with no keys other
    than the ones required to give it that structure.

    Args:
        source_data (dict): Nested dictionary

    Returns:
        dict: Nested dictionary with all keys excepting 'uuid' removed. The nesting structure of the input will be otherwise maintained.
    """
    for key in source_data:
        if isinstance(source_data[key], dict):
            return {key: extract_uuid_key(source_data=source_data[key])}
        elif key == "uuid":
            return {key: source_data[key]}
    return {}


def extract_repo_name_from_url(url: str) -> str:
    """
    Extract the repository name from a git URL.

    Args:
        url (str): URL to extract the repository name from

    Returns:
        str: Repository name
    """
    return url.split("/")[-1].replace(".git", "")
