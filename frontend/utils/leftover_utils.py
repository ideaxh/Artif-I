# utils/leftover_utils.py

import json
import cohere

co = cohere.ClientV2("GENERATE_TEST_KEY")  # Replace with your actual key

def ask_user_transfer_amount(leftover_amount: float, leftover_currency: str, user_input: str) -> dict:
    """
    Extract amount and currency based on user input.
    """
    amount_response = co.chat(
        model='command-r',
        messages=[
            {"role": "system", "content": f"""
Je një ndihmës bankar që flet shqip.
Përdoruesi mund të dojë të transferojë të gjithë shumën ({leftover_amount} {leftover_currency}) ose një shumë më të vogël.
Nëse përdoruesi thotë 'të gjithën', 'krejt' ose 'tonat', kthe {{"amount": {leftover_amount}, "currency": "{leftover_currency}"}}.
Nëse përdoruesi thotë 'një shumë tjetër', 'një shumë specifike' ose diçka të ngjashme pa dhënë shumën, kthe {{"amount": null, "currency": null}}.
Nëse përdoruesi jep një shumë numerike dhe valutë (p.sh. 'transfero 10 EUR'), nxirr atë numër dhe valutë dhe kthe JSON me fushat "amount" dhe "currency".
Mos shpjego, kthe vetëm JSON me fushat 'amount' dhe 'currency'.
""" },
            {"role": "user", "content": user_input}
        ],
        temperature=0
    )

    try:
        amount_json = json.loads(amount_response.message.content[0].text.strip())
        return amount_json
    except json.JSONDecodeError:
        return {"amount": leftover_amount, "currency": leftover_currency}


def prompt_for_specific_amount(user_input: str) -> dict:
    """
    Parse numeric amount and currency from user input.
    """
    response = co.chat(
        model='command-r',
        messages=[
            {"role": "system", "content": """
Je një ndihmës bankar që flet shqip.
Nxirr vetëm shumën numerike dhe valutën (shkurtim me shkronja kapital) nga input-i i përdoruesit.
Kthe vetëm JSON me fushat: "amount" (numër) dhe "currency" (string).
Nëse nuk gjen një numër dhe valutë të vlefshme, kthe {"amount": null, "currency": null}.
""" },
            {"role": "user", "content": user_input}
        ],
        temperature=0
    )

    try:
        extracted = json.loads(response.message.content[0].text.strip())
        return extracted
    except json.JSONDecodeError:
        return {"amount": None, "currency": None}


def leftover_transfer_handler(user_input: str, leftover_amount: float, leftover_currency: str) -> str:
    """
    Main logic to handle the leftover transfer based on input.
    """
    amount_info = ask_user_transfer_amount(leftover_amount, leftover_currency, user_input)

    if amount_info.get("amount") is None or amount_info.get("currency") is None:
        return "Sa saktësisht dëshiron të transferosh? Shkruaj shumën dhe valutën, p.sh. '15 EUR'."

    amount = amount_info["amount"]
    currency = amount_info["currency"]

    if currency != leftover_currency:
        return f"Valuta ({currency}) nuk përputhet me valutën e shumës së mbetur ({leftover_currency})."

    if amount > leftover_amount:
        return f"Shuma ({amount}) është më e madhe se shuma e mbetur ({leftover_amount})."

    leftover_after = leftover_amount - amount
    return f"{amount} {currency} u transferuan me sukses te llogaria e kursimeve. Shuma e mbetur: {leftover_after:.2f} {leftover_currency}."
