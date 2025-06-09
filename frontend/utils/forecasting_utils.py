import cohere

def summarize_forecast(api_key, forecast_series):
    co = cohere.Client(api_key)

    forecast_text = "\n".join(
        f"{date.strftime('%B %Y')}: {amount:.2f} EUR"
        for date, amount in forecast_series.items()
    )

    prompt = (
        "Here is a 6-month expense forecast:\n"
        f"{forecast_text}\n\n"
        "Please summarize this forecast in a short paragraph for a banking app user."
    )

    response = co.chat(
        model='command-r',
        message=prompt,
        max_tokens=100,
        temperature=0.7
    )

    return response.text.strip()