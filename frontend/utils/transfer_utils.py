import cohere
import json

co = cohere.Client(api_key="GENERATE_TEST_KEY")  # Replace with your key

def normalize_albanian_name(name: str) -> str:
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
    try:
        response = co.chat(
            model='command-r',
            chat_history=[],
            message=user_input,
            prompt_truncation='OFF',
            temperature=0.3,
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
        parsed = json.loads(response.text.strip())
        if all(key in parsed for key in ["amount", "currency", "recipient"]):
            return parsed
        return None
    except Exception as e:
        print(f"[ERROR] Gjatë analizimit: {e}")
        return None

def perform_transfer(amount, currency, recipient):
    return f"{amount} {currency} u transferuan me sukses te {recipient}."
