import json
import re
import cohere

co = cohere.ClientV2("GENERATE_TEST_KEY")  

import json

def ask_user_confirmation(leftover_amount: float, leftover_currency: str) -> bool:
    """
    Ask user if they want to transfer leftover money.
    Returns True if user confirms, False otherwise.
    """
    print(f"Është fundi i muajit dhe ke {leftover_amount} {leftover_currency} të mbetura.")
    user_decision = input(f"Dëshiron t’i transferoj në llogarinë e kursimeve? (po/jo): ")

    confirm_response = co.chat(
        model='command-r',
        messages=[
            {"role": "system", "content": """Je një ndihmës që flet vetëm shqip. 
-Përgjigju me JSON me fushën 'confirmed' true nëse përdoruesi thotë po
-Përgjigju me JSON me fushën 'confirmed' false nëse përdoruesi thotë jo""" },
            {"role": "user", "content": user_decision}
        ],
        temperature=0
    )

    try:
        confirmed_json = json.loads(confirm_response.message.content[0].text.strip())
        return bool(confirmed_json.get("confirmed", False))
    except json.JSONDecodeError:
        return False

def ask_user_transfer_amount(leftover_amount: float, leftover_currency: str) -> dict:
    """
    Ask user if they want to transfer full or specific amount.
    Return dict with keys: "amount" (float or None), "currency" (str).
    """
    user_amount_input = input(f"Dëshiron të transferosh të gjithë shumën ({leftover_amount} {leftover_currency}) apo një shumë specifike? ")

    amount_response = co.chat(
        model='command-r',
        messages=[
            {"role": "system", "content": f"""
Je një ndihmës bankar që flet shqip.
Përdoruesi mund të dojë të transferojë të gjithë shumën ({leftover_amount} {leftover_currency}) ose një shumë më të vogël.
Nëse përdoruesi thotë 'të gjithën', 'krejt' ose 'tonat', kthe {{"amount": {leftover_amount}, "currency": "{leftover_currency}"}}.
Nëse përdoruesi thotë 'një shumë tjetër', 'një shumë specifike' ose diçka të ngjashme pa dhënë shumën, kthe {{"amount": null, "currency": null}} që do të tregojë se duhet ta pyesësh më pas për shumën.
Nëse përdoruesi jep një shumë numerike dhe valutë (p.sh. 'transfero 10 EUR'), nxirr atë numër dhe valutë dhe kthe JSON me fushat "amount" dhe "currency".
Mos shpjego, kthe vetëm JSON me fushat 'amount' dhe 'currency' (si numër dhe string ose null).
"""}
            ,
            {"role": "user", "content": user_amount_input}
        ],
        temperature=0
    )

    try:
        amount_json = json.loads(amount_response.message.content[0].text.strip())
        return amount_json
    except json.JSONDecodeError:
        # If unable to parse JSON, fallback to full amount & currency
        return {"amount": leftover_amount, "currency": leftover_currency}

def prompt_for_specific_amount() -> dict:
    """
    Ask user for numeric transfer amount and currency, extracted via LLM.
    Repeat until valid amount and currency are extracted.
    Returns dict with keys: "amount" (float) and "currency" (str).
    """
    while True:
        user_input = input("Sa saktësisht dëshiron të transferosh? (shkruaj shumën dhe valutën, p.sh. '15 EUR') ")

        response = co.chat(
            model='command-r',
            messages=[
                {"role": "system", "content": """
Je një ndihmës bankar që flet shqip.
Nxirr vetëm shumën numerike dhe valutën (shkurtim me shkronja kapital) nga input-i i përdoruesit.
Kthe vetëm JSON me fushat: "amount" (numër) dhe "currency" (string).
Nëse nuk gjen një numër dhe valutë të vlefshme, kthe {"amount": null, "currency": null}.
Mos shpjego asgjë tjetër."""},
                {"role": "user", "content": user_input}
            ],
            temperature=0
        )

        try:
            response_text = response.message.content[0].text.strip()
            extracted = json.loads(response_text)
            amount = extracted.get("amount")
            currency = extracted.get("currency")

            if amount is not None and currency:
                return {"amount": float(amount), "currency": currency}
            else:
                print("Nuk u gjetën shumë dhe valutë valide. Provo përsëri.")
        except (json.JSONDecodeError, ValueError):
            print("Ndodhi një gabim gjatë leximit të përgjigjes. Provo përsëri.")

def leftover_transfer_flow(leftover_amount: float, leftover_currency: str):
    """
    Full flow to handle leftover transfer with separation of concerns.
    Reduces transferred amount from leftover_amount.
    """
    confirmed = ask_user_confirmation(leftover_amount, leftover_currency)
    if not confirmed:
        print("Transferimi i shumës së mbetur u anulua ose nuk u konfirmua.")
        return

    amount_info = ask_user_transfer_amount(leftover_amount, leftover_currency)
    if amount_info.get("amount") is None or amount_info.get("currency") is None:
        amount_info = prompt_for_specific_amount()

    transfer_amount = amount_info['amount']
    transfer_currency = amount_info['currency']

    if transfer_currency != leftover_currency:
        print(f"Valuta e transferimit ({transfer_currency}) nuk përputhet me valutën e shumës së mbetur ({leftover_currency}). Transferimi u anulua.")
        return

    if transfer_amount > leftover_amount:
        print(f"Shuma që dëshiron të transferosh ({transfer_amount}) është më e madhe se shumën e mbetur ({leftover_amount}). Transferimi u anulua.")
        return

    # Deduct the transferred amount from leftover
    leftover_amount -= transfer_amount

    # Mock transfer action (replace with actual logic)
    print(f"{transfer_amount} {transfer_currency} u transferuan me sukses te Llogaria e kursimeve.")
    print(f"Shuma e mbetur pas transferimit është: {leftover_amount} {leftover_currency}.")

if __name__ == "__main__":
    leftover_amount = 150.0
    leftover_currency = "EUR"
    leftover_transfer_flow(leftover_amount, leftover_currency)

