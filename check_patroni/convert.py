import click
import re
from typing import Union, Tuple


def size_to_byte(value: str) -> int:
    """Convert any size to Byte
    >>> size_to_byte('1TB')
    1099511627776
    >>> size_to_byte('5kB')
    5120
    >>> size_to_byte('.5kB')
    512
    >>> size_to_byte('.5 yoyo')
    Traceback (most recent call last):
    ...
    click.exceptions.BadParameter: Invalid unit for size f{value}
    """
    convert = {
        "B": 1,
        "kB": 1024,
        "MB": 1024 * 1024,
        "GB": 1024 * 1024 * 1024,
        "TB": 1024 * 1024 * 1024 * 1024,
    }
    val, unit = strtod(value)

    if val is None:
        val = 1

    if unit is None:
        # No unit, all good
        # we can round half bytes dont really make sense
        return round(val)
    else:
        try:
            multiplicateur = convert[unit]
        except KeyError:
            raise click.BadParameter("Invalid unit for size f{value}")

    # we can round half bytes dont really make sense
    return round(val * multiplicateur)


DBL_RE = re.compile(r"^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?")


def strtod(value: str) -> Tuple[Union[float, None], Union[str, None]]:
    """As most as possible close equivalent of strtod(3) function used by postgres to parse parameter values.
    >>> strtod(' A ') == (None, 'A')
    True
    """
    value = str(value).strip()
    match = DBL_RE.match(value)
    if match:
        end = match.end()
        return float(value[:end]), value[end:]
    return None, value
