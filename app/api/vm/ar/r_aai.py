from fastapi import APIRouter,HTTPException
from pydantic import BaseModel
import openai, dotenv

CFG = dotenv.dotenv_values(".env")
client = openai.OpenAI(api_key = CFG['OPENAI_API_KEY'])
model = "gpt-4o"

system_prompt_invoice = """
    You are an assistant that extracts structured data from invoices provided as images.
    Return a JSON object with at least the following fields:
    
    - my_business_name: string
    - my_business_address: string
    - my_business_phone: string
    - my_business_number: string

    - client_business_name: string
    - client_contact_name: string
    - client_address: string
    - client_phone: string

    - invoice_number: string
    - issue_date: ISO 8601 date string (e.g., "2025-05-28T00:00:00.000Z")
    - due_date: ISO 8601 date string (e.g., "2025-05-28T00:00:00.000Z")
    - reference: string

    - item_list: list

    - invoice_subtotal: number
    - invoice_discount: number
    - invoice_tax: number
    - invoice_total: number
    - invoice_notes: number
    - invoice_terms_conditions: number

    If the value is not found, return it as null.
    Return only valid JSON.
"""

system_prompt_client = """
    You are an assistant that extracts structured data from Name Card or similar documents provided as images. 
    Return a JSON object with at least the following fields:
    - client_business_name: string
    - client_contact_name: string
    - client_contact_title: string
    - client_address: string
    - client_email: string
    - client_phone: string
    - client_website: string    
    - client_currency: string, based on the address to return the possible currency. 
    - client_note: string

    If the value is not found, return it as null.
    Return only valid JSON.
"""

system_prompt_item = """
    You are an assistant that extracts structured data from Item List or similar documents provided as images. 
    Return a JSON object with at least the following fields:
    - item_name: string
    - item_rate: number
    - item_unit_of_measure: string
    - item_sku: string
    - item_description: string

    If the value is not found, return it as null.
    Return only valid JSON.
"""

system_prompt_me = """
    You are an assistant that extracts structured data from Name Card or similar documents provided as images.
    Return a JSON object with at least the following fields:
    - business_name: string
    - business_address: string
    - business_email: string
    - business_phone: string
    - business_number: string
    - business_bank_info: string
    - business_website: string    
    - business_currency: based on the address, pick a  currency from below list: USD, CAD, OTHER

    If the value is not found, return it as null.
    Return only valid JSON.
"""

class ImagePayload(BaseModel):base64_image: str

router = APIRouter()

def b64_2_json_invoice(base64_image):
    response = client.chat.completions.create(
        model=model,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system",  "content": system_prompt_invoice},
            {"role": "user",    "content": [
                    {"type": "text", "text": "extract the data in this invoice and output into JSON "},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}", "detail": "high"}}
                ]
            }
        ],
        temperature=0.0,
    )
    return response.choices[0].message.content


def client_b64_2_json(base64_image):
    response = client.chat.completions.create(
        model=model,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system",  "content": system_prompt_client},
            {"role": "user",    "content": [
                    {"type": "text", "text": "extract the data in this Name Card and output into JSON "},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}", "detail": "high"}}
                ]
            }
        ],
        temperature=0.0,
    )
    return response.choices[0].message.content



def me_b64_2_json(base64_image):
    response = client.chat.completions.create(
        model=model,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system",  "content": system_prompt_client},
            {"role": "user",    "content": [
                    {"type": "text", "text": "extract the data in this Name Card and output into JSON "},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}", "detail": "high"}}
                ]
            }
        ],
        temperature=0.0,
    )
    return response.choices[0].message.content


@router.post("/image_invoice_json")
async def invoice_image_to_json(payload: ImagePayload):
    try:
        result_json = b64_2_json_invoice(payload.base64_image)
        return {"data": result_json}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@router.post("/image_client_json")
async def client_image_to_json(payload: ImagePayload):
    try:
        result_json = client_b64_2_json(payload.base64_image)
        return {"data": result_json}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def item_b64_2_json(base64_image):
    response = client.chat.completions.create(
        model=model,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system",  "content": system_prompt_item},
            {"role": "user",    "content": [
                    {"type": "text", "text": "extract the data in this image and output into JSON "},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}", "detail": "high"}}
                ]
            }
        ],
        temperature=0.0,
    )
    return response.choices[0].message.content


    
    
@router.post("/image_item_json")
async def item_image_to_json(payload: ImagePayload):
    try:
        result_json = item_b64_2_json(payload.base64_image)
        return {"data": result_json}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
    
@router.post("/image_me_json")
async def me_image_to_json(payload: ImagePayload):
    try:
        result_json = me_b64_2_json(payload.base64_image)
        return {"data": result_json}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
    
    


    


