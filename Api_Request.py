from openai import OpenAI

def askAI(userInput):
    client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
    )
    user = userInput
    completion = client.chat.completions.create(
    extra_headers={
        "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
        "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
    },
    extra_body={},
    model="openai/gpt-oss-20b:free",
    messages=[
        {
        "role": "user",
        "content": user + "Don't add markdown syntax, just give me simple text response."
        }
    ]
    )
    return completion.choices[0].message.content