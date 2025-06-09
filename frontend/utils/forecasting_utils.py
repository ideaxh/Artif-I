import cohere

cohere_api_key = "sKcXnS3ilXvhWw6kxjaJxdDAl0UVmSEN235G29Mg"

def summarize_forecast(forecast_series):
    co = cohere.Client(cohere_api_key)

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
        max_tokens=200,
        temperature=0.6
    )

    return response.text.strip()