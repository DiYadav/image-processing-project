import os, json, re
from openai import OpenAI

def call_deepseek_extract(pdf_text, fields):
    """
    fields: either list of keys (["client_name",...]) OR list of dicts [{"label":..,"key":..},...]
    Returns dict { key: value }
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set")

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

    # Normalize fields
    if isinstance(fields, list) and fields and isinstance(fields[0], dict):
        keys = [f["key"] for f in fields]
        labels = [f["label"] for f in fields]
    else:
        keys = list(fields)
        labels = list(fields)

    prompt = f"""
You are a strict JSON extractor. Given the PDF text below, extract values for each of the following fields.
Return ONLY a valid JSON object mapping the machine keys to single-string values.
If you cannot find a value, return an empty string for that key.

Fields (labels): {labels}
Keys (machine): {keys}

PDF TEXT:
----------------
{pdf_text}
----------------

Return JSON, e.g.:
{{"{keys[0]}": "value", "{keys[1]}": "value", ...}}
"""

    response = client.chat.completions.create(
        model="deepseek/deepseek-chat",
        messages=[{"role":"user","content":prompt}],
        max_tokens=800
    )
    # For OpenRouter API response:
    raw = response.choices[0].message.content   
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        # try direct json parse
        try:
            return json.loads(raw)
        except Exception as e:
            raise ValueError("LLM did not return JSON. Raw response: " + raw)
    try:
        return json.loads(m.group(0))
    except Exception as e:
        raise ValueError("Failed to parse JSON from LLM response: " + str(e) + "\nRaw:" + raw)
