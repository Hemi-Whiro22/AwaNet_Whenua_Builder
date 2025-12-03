import re


def clean_text(txt: str) -> str:
    txt = txt.replace("\n\n", "\n")
    txt = txt.strip()
    txt = re.sub(r"\s+", " ", txt)
    return txt
