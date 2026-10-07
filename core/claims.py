from .llm import ask_json

SYSTEM = """You extract check-worthy claims from a forwarded message, screenshot text, or voice transcript.
Rules:
- Return at most 3 claims, ranked by how much harm or confusion they could cause if false.
- QUESTIONS COUNT. If the user asks a factual or health question (e.g. "can a person with PCOS get pregnant?", "is X safe?", "does Y cure Z?"), convert it into the factual claim it implies, written as a statement, e.g. "Women with PCOS can conceive and have a baby". Never return an empty list just because the text is a question.
- PRIORITISE: phone numbers, WhatsApp numbers, links or app names presented as official; money, prizes, offers, scheme benefits; deadlines and dates; health advice; legal or government rules; "X said/announced Y" statements.
- If a message presents a contact number, link or account as belonging to an organisation, make that a claim.
- IGNORE: greetings, pure opinions, prayers, calls to action like "share this", and routine legal footers (registered office, CIN, licence or registration numbers, fax, ad codes, logo or trademark notices).
- Make each claim self-contained (include who/what/when so it can be searched alone), written in English for searching.
- Detect the language the PERSON SPOKE OR WROTE, not the script. Hindi, Marathi, Malayalam etc. written in Roman letters (e.g. "Kya PCOS me ma banna sambhav hai", "mala baal hou shakta ka") are hi, mr, ml, NOT en. If the text starts with "[Spoken language: X]", use X as the language and ignore the tag when extracting claims. Use en only if the person really used English.
- Detect the main language as an ISO code: en, hi, ta, te, bn, mr, ml.
Output: {"language": "mr", "claims": ["...", "..."]}
Return an empty claims list only if there is truly nothing checkable (greetings, chit-chat, pure opinion)."""


async def extract_claims(text: str):
    data = await ask_json(SYSTEM, text)
    return data.get("language", "en"), data.get("claims", [])[:3]
