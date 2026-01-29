import openai, dotenv

CFG = dotenv.dotenv_values(".env")
age = 300 # seconds

client = openai.OpenAI(api_key = CFG['OPENAI_API_KEY'])
model = "gpt-4o"


# receipt_system_prompt = """
# You are an assistant that extracts structured data from receipts provided.
# Return a JSON object with the following fields, based on the ReceiptBase schema:

# - receipt_date: ISO 8601 date string (e.g., "2025-05-28")
# - payer_name: string
# - payee_name: string
# - vendor_name: string
# - coa: string

# - subtotal: number
# - tax: number
# - total: number

# - currency: string (e.g., "USD")
# - payment_method: string (e.g., "cash", "credit_card", etc.)
# - reference: string
# - description: string

# If a field is not found, return it with a null value.
# Do not guess missing information. Only extract data present in the receipt.
# Return only valid JSON.
# """


receipt_system_prompt = """
    You are an assistant that extracts structured data from receipts provided.
    Return the result as a JSON object with the following exact fields:

    - receipt_date: ISO 8601 date string (e.g., "2025-05-28")
    - payer_name: string
    - payee_name: string
    - vendor_name: string
    - coa: string

    - province_code: string
    - pst: string
    - gst: string
    - hst: string
    - rst: string
    - address: string
    - phone: string

    - subtotal: number
    - tax: number
    - total: number

    - currency: string (e.g., "USD")
    - payment_method: string
    - card_number: string
    - reference: string
    - description: string

    Rules:
    1. Always include all fields above, even if missing in the receipt.
    2. If a field cannot be found or read, set its value to exactly "not recognized".
    3. Do not guess missing information.
    4. Return only valid JSON with double quotes for keys and string values.
    5. Use the exact field names as given.
"""


def receipt_ai_txt(lines: list[str]):
    prompt_text = "\n".join(lines)
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": receipt_system_prompt},
            {"role": "user", "content": prompt_text},
        ],
        temperature=0.0,
    )
    return response.choices[0].message.content


def receipt_ai_b64(base64_image):
    response = client.chat.completions.create(
        model=model,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system",  "content": receipt_system_prompt},
            {"role": "user",    "content": [
                    {"type": "text", "text": "extract the data in this receipt and output into JSON "},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}", "detail": "high"}}
                ]
            }
        ],
        temperature=0.0,
    )
    return response.choices[0].message.content


    