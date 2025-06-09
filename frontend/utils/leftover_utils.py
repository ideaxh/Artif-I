# utils/leftover_utils.py

import json
import re
import cohere

co = cohere.ClientV2("FqKNvT8UV6daEZyTttXfJcZRdiubfq0gNpjBmqXu")  # Replace with your actual key


def _extract_json_from_response(text: str) -> dict:
    """
    Utility to clean markdown and parse JSON safely.
    """
    print("[DEBUG] Raw LLM response:", text)
    try:
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.IGNORECASE)
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON decode failed: {e}")
        return None


def ask_user_transfer_amount(leftover_amount: float, leftover_currency: str, user_input: str) -> dict:
    """
    Extract amount and currency based on user input.
    """
    amount_response = co.chat(
        model='command-r',
        messages=[
            {"role": "system", "content": f"""
You are a banking assistant that speaks English.
The user may want to transfer the entire amount ({leftover_amount} {leftover_currency}) or a smaller amount.
If the user says 'all', 'everything', or 'the full amount', return {{"amount": {leftover_amount}, "currency": "{leftover_currency}"}}.
If the user says 'another amount', 'a different amount', or something similar without giving an amount, return {{"amount": null, "currency": null}}.
If the user provides a specific amount and currency (e.g. 'transfer 10 EUR'), extract that number and currency and return a JSON with fields "amount" and "currency".
Do not explain anything, return only JSON with the fields 'amount' and 'currency'.
""" },
            {"role": "user", "content": user_input}
        ],
        temperature=0
    )

    response_text = amount_response.message.content[0].text
    parsed = _extract_json_from_response(response_text)

    if parsed:
        return parsed
    return {"amount": leftover_amount, "currency": leftover_currency}


def prompt_for_specific_amount(user_input: str) -> dict:
    """
    Parse numeric amount and currency from user input.
    """
    response = co.chat(
        model='command-r',
        messages=[
            {"role": "system", "content": """
You are a banking assistant that speaks English.
Extract only the numeric amount and currency (use uppercase currency code) from the user's input.
Return only JSON with the fields: "amount" (number) and "currency" (string).
If no valid number and currency are found, return {"amount": null, "currency": null}.
""" },
            {"role": "user", "content": user_input}
        ],
        temperature=0
    )

    response_text = response.message.content[0].text
    parsed = _extract_json_from_response(response_text)

    if parsed:
        return parsed
    return {"amount": None, "currency": None}


def leftover_transfer_handler(user_input: str, leftover_amount: float, leftover_currency: str) -> str:
    """
    Main logic to handle the leftover transfer based on input.
    """
    print("[DEBUG] User input:", user_input)
    amount_info = ask_user_transfer_amount(leftover_amount, leftover_currency, user_input)
    print("[DEBUG] Parsed amount_info:", amount_info)

    if amount_info.get("amount") is None or amount_info.get("currency") is None:
        return "How much exactly would you like to transfer? Please enter the amount and currency, e.g., '15 EUR'."

    amount = amount_info["amount"]
    currency = amount_info["currency"]

    if currency != leftover_currency:
        return f"The currency ({currency}) does not match the leftover currency ({leftover_currency})."

    if amount > leftover_amount:
        return f"The amount ({amount}) exceeds the leftover amount ({leftover_amount})."

    leftover_after = leftover_amount - amount
    return f"{amount} {currency} has been successfully transferred to your savings account. Remaining amount: {leftover_after:.2f} {leftover_currency}."
