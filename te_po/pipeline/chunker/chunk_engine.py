def chunk_text(text: str, max_len: int = 800) -> list[str]:
    words = text.split(" ")
    chunks = []
    buf = []

    for w in words:
        buf.append(w)
        if len(" ".join(buf)) > max_len:
            chunks.append(" ".join(buf))
            buf = []

    if buf:
        chunks.append(" ".join(buf))

    return chunks
