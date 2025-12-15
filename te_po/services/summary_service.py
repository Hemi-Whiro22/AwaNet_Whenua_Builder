import json
import uuid

from te_po.services.local_storage import save, timestamp
from te_po.utils.openai_client import client, generate_text


def summarize_text(text: str, mode: str = "research"):
    if client is None:
        return {"id": None, "summary": "[offline] OpenAI client not configured.", "mode": mode, "saved": False}
    try:
        style = "deep academic analysis" if mode == "research" else "taonga-aligned cultural summary"
        out = generate_text(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"Summarize with {style}. "
                        "Provide a comprehensive, in-depth summary structured as follows:\n\n"
                        "1) **Executive Summary** — 2-3 paragraphs providing a thorough overview of the document's main purpose, scope, and significance.\n\n"
                        "2) **Key Points & Ideas** — 12-15 detailed bullet points covering:\n"
                        "   • Main arguments and central themes\n"
                        "   • Key people, organizations, and places mentioned\n"
                        "   • Important dates, events, and timelines\n"
                        "   • Actions, policies, or recommendations\n"
                        "   • Data, statistics, or evidence cited\n"
                        "   Each bullet should be clear and specific, providing context.\n\n"
                        "3) **Cultural & Māori Context** — 6-8 detailed bullets on:\n"
                        "   • Māori concepts, mātauranga Māori, and tikanga references\n"
                        "   • Taonga (treasured knowledge/resources) and their significance\n"
                        "   • Whakapapa (genealogy/connections) and relationship dynamics\n"
                        "   • Mana (prestige/authority) and kaitiakitanga (guardianship) implications\n"
                        "   • Indigenous perspectives and cultural gaps or misalignments\n"
                        "   • Recommendations for cultural alignment or consideration\n\n"
                        "4) **Implications & Significance** — 4-6 bullets outlining:\n"
                        "   • Why this document matters\n"
                        "   • Who is affected and how\n"
                        "   • Future considerations or next steps\n\n"
                        "Ensure the response is culturally aware, respectful of Te Ao Māori, and contextually rich."
                    ),
                },
                {"role": "user", "content": text},
            ],
        )
        entry_id = f"summary_{uuid.uuid4().hex}"
        save(
            "openai",
            f"{entry_id}.json",
            json.dumps(
                {"id": entry_id, "mode": mode, "input": text, "output": out, "ts": timestamp()},
                indent=2,
            ),
        )
        return {"id": entry_id, "summary": out, "mode": mode, "saved": True}
    except Exception as exc:
        return {"id": None, "summary": f"Summary failed: {exc}", "mode": mode, "saved": False}
