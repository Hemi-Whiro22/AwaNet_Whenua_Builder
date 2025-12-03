from te_po.utils.openai_client import generate_embedding


def embed_text(txt: str) -> list[float]:
    return list(generate_embedding(txt))
