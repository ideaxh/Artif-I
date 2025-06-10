import re
import cohere
import json

co = cohere.Client(api_key="sKcXnS3ilXvhWw6kxjaJxdDAl0UVmSEN235G29Mg")  # Replace with your key

def normalize_albanian_name(name: str) -> str:
    """
    Normalize an Albanian name by removing suffixes and capitalizing.
    """
    name = name.strip().capitalize()
    suffix_map = {
        "itës": "a", "ites": "a", "it": "i",
        "ësë": "a", "ës": "a", "së": "a",
        "es": "a", "ut": "u"
    }
    for suffix, replacement in suffix_map.items():
        if name.endswith(suffix) and len(name) > len(suffix) + 1:
            return name[:-len(suffix)] + replacement
    return name

def parse_transfer_command(user_input: str):
    """
    Extract transfer details (amount, currency, recipient) from user's command.
    """
    try:
        response = co.chat(
            model='command-r',
            chat_history=[],
            message=user_input,
            prompt_truncation='OFF',
            temperature=0.3,
            preamble="""
You are a banking assistant that speaks English.
When the user requests a transfer, always return a JSON object with the following fields: amount (as a number), currency (EUR, USD, GBP, etc.), and recipient (a person's name).
Do not explain anything — return only the JSON.

The recipient's name can appear:
- at the beginning, middle, or end of the sentence,
- before or after the amount,
- capitalized or not.

When extracting the recipient's name, always return it in the nominative form (base name).
"""
        )

        content = getattr(response, "text", "") or getattr(response, "message", {}).get("content", "")
        print("[DEBUG] Raw response:", content)

        # Remove Markdown-style ```json ... ``` if present
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip(), flags=re.IGNORECASE)
        parsed = json.loads(cleaned)

        if all(key in parsed for key in ["amount", "currency", "recipient"]):
            return parsed
        return None

    except Exception as e:
        print(f"[ERROR] During parsing: {e}")
        return None

def perform_transfer(amount, currency, recipient):
    """
    Format the transfer confirmation message.
    """
    return f"{amount} {currency} were successfully transferred to {recipient}."
