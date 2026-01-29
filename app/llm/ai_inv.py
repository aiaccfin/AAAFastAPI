import openai, dotenv

CFG = dotenv.dotenv_values(".env")
age = 300 # seconds

client = openai.OpenAI(api_key = CFG['OPENAI_API_KEY'])
model = "gpt-4o"


inv_system_prompt = """
    You are an assistant that extracts structured data from invoices provided.
    Return a JSON object with at least the following fields, based on the InvoiceBase schema:

    - invoice_number: string
    - biz_id: integer (set to null if not available)
    - biz_name: string
    - customer_id: integer (set to null if not available)
    - customer_name: string
    - client_id: integer (set to null if not available)
    - client_name: string
    - client_address: string
    - client_payment_method: string
    - issue_date: ISO 8601 date string (e.g., "2025-05-28")
    - due_date: ISO 8601 date string (e.g., "2025-05-28")
    - payment_status: string

    - item_description: string
    - item_quantity: number
    - item_unit_price: number
    - item_tax_rate: number
    - item_tax: number
    - item_amount: number

    - invoice_total_amount: number
    - invoice_recurring: boolean
    - invoice_note: string

    If the value is not found, return it as null.
    Return only valid JSON.
"""


def inv_ai_txt(lines: list[str]):
    prompt_text = "\n".join(lines)
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": inv_system_prompt},
            {"role": "user", "content": prompt_text},
        ],
        temperature=0.0,
    )
    return response.choices[0].message.content


def inv_ai_b64(base64_image):
    response = client.chat.completions.create(
        model=model,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system",  "content": inv_system_prompt},
            {"role": "user",    "content": [
                    {"type": "text", "text": "extract the data in this invoice and output into JSON "},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}", "detail": "high"}}
                ]
            }
        ],
        temperature=0.0,
    )
    return response.choices[0].message.content


