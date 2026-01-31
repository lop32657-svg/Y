import re
from typing import Optional, Tuple

CARD_PATTERN = re.compile(
    r"""
    (?P<cc>\d{12,19})
    \s*[|:/\-\s]\s*
    (?P<mm>\d{1,2})
    \s*[|:/\-\s]\s*
    (?P<yy>\d{2,4})
    \s*[|:/\-\s]\s*
    (?P<cvv>\d{3,4})
    """,
    re.VERBOSE
)

def getcards(text: str) -> Optional[Tuple[str, str, str, str]]:
    if not text:
        return None

    matches = list(CARD_PATTERN.finditer(text))

    # ❌ ၂ ခုထက်ပိုရင် mass cc → မယူ
    if len(matches) > 2:
        return None

    if not matches:
        return None

    m = matches[0]

    cc = m.group("cc")
    mm = m.group("mm").zfill(2)
    yy = m.group("yy")
    cvv = m.group("cvv")

    if len(yy) == 2:
        yy = f"20{yy}"

    if not 1 <= int(mm) <= 12:
        return None

    return cc, mm, yy, cvv