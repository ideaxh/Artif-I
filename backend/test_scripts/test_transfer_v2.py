import cohere
import json

co = cohere.Client(api_key="GENERATE_TEST_KEY") 
def normalize_albanian_name(name: str) -> str:
    """
    Attempts to normalize an Albanian name to its nominative form by removing common suffixes.
    This is useful when names are in indirect cases (like 'Kleas', 'Idees', 'Arbit', etc.)

    Args:
        name (str): The possibly declined name (e.g. 'Kleas')

    Returns:
        str: Likely nominative form (e.g. 'Klea')
    """
    name = name.strip().capitalize()

    # Generic patterns (remove suffixes)
    suffix_map = {
        "itës": "a",
        "ites": "a",
        "it": "i",
        "ësë": "a",
        "ës": "a",
        "së": "a",
        "es": "a",
        "ut": "u"
    }

    for suffix, replacement in suffix_map.items():
        if name.endswith(suffix) and len(name) > len(suffix) + 1:
            return name[:-len(suffix)] + replacement

    return name

def parse_transfer_command(user_input: str):
    """
    Uses Cohere Command R+ to extract amount, currency, and recipient from Albanian user input.
    Always returns a dictionary on success, or None on failure.
    """
    try:
        response = co.chat(
            model='command-r',  
            chat_history=[],
            message=user_input,
            prompt_truncation='OFF',
            temperature=0.3,
            connectors=[],
            tools=[],
            preamble="""
            Je një ndihmës bankar që flet shqip. 
            Kur përdoruesi kërkon një transfer, kthe gjithmonë një JSON me fushat: amount (si numër), currency (EUR, USD, GBP, etj), dhe recipient (si emër).
            Mos shpjego, kthe vetëm JSON-in.

            Emri i personit që merr paratë mund të jetë:
            - në fillim, mes, ose në fund të fjalisë,
            - përpara ose pas shumës
            - me shkronjë të kapitalizuar ose jo.

            Kur nxjerr emrin e personit, ktheje gjithmonë në trajtën emërore: 
            """
        )

        response_text = response.text.strip()
        print(f"\n[DEBUG] Cohere response:\n{response_text}\n")

        parsed = json.loads(response_text)

        if all(key in parsed for key in ["amount", "currency", "recipient"]):
            return parsed
        else:
            print("[ERROR] Mungojnë fushat në JSON.")
            return None

    except Exception as e:
        print(f"[ERROR] Gjatë analizimit: {e}")
        return None


def perform_transfer(amount, currency, recipient):
    """
    Simulates a money transfer.
    """
    if amount and currency and recipient:
        return f"{amount} {currency} u transferuan me sukses te {recipient}."
    return "Gabim: mungojnë të dhënat për transferim."


if __name__ == "__main__":
    user_input = "pls qoja 10 milion euro idees"
    details = parse_transfer_command(user_input)

    if isinstance(details, dict):
        details['recipient'] = normalize_albanian_name(details['recipient'])
        result = perform_transfer(details.get('amount'), details.get('currency'), details.get('recipient'))
        print(result)
    else:
        print("Nuk mund të ektraktosh të dhënat nga komanda.")

    if details:
        result = perform_transfer(details['amount'], details['currency'], details['recipient'])
        print(result)
    else:
        print("Nuk mund të ektraktosh të dhënat nga komanda.")