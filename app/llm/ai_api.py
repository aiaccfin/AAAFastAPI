import openai, dotenv
from app.llm.prompt_engineer import system_prompt, txt2json_prompt, save2db_prompt

CFG = dotenv.dotenv_values(".env")
age = 300 # seconds

client = openai.OpenAI(api_key = CFG['OPENAI_API_KEY'])
model = "gpt-4o"

def b64_2_json(base64_image):
    response = client.chat.completions.create(
        model=model,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system",  "content": system_prompt},
            {"role": "user",    "content": [
                    {"type": "text", "text": "extract the data in this bank statement and output into JSON "},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}", "detail": "high"}}
                ]
            }
        ],
        temperature=0.0,
    )
    return response.choices[0].message.content



def generate_strict_answer(prompt: str) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a factual assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
    )

    return response.choices[0].message.content.strip()


# def extract_from_b64(base64_image, page_number):
#     st.warning(ai_model)
    
#     response = client.chat.completions.create(
#         model=model,
#         response_format={ "type": "json_object" },
#         messages=[
#             {
#                 "role": "system",
#                 "content": system_prompt
#             },
#             {
#                 "role": "user",
#                 "content": [
#                     {"type": "text", "text": "extract the data in this bank statement and output into JSON "},
#                     {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}", "detail": "high"}}
#                 ]
#             }
#         ],
#         temperature=0.0,
#         stream=stream
#     )

#     if stream:
#         result=""
#         start_time = time.time()

#         for chunk in response:
#             elapsed_time = time.time() - start_time
            
#             if elapsed_time > age: 
#                 st.write(f"time used: {elapsed_time:.0f} seconds")
#                 result = json.dumps({"NOTICE": f"Page {page_number} not extracted due to time limit."})
#                 break
            
#             if chunk.choices[0].delta.content is not None:
#                 result += chunk.choices[0].delta.content
        
#         st.info(f"used time: {elapsed_time:.0f} seconds")
#         return result
#     else:
#         st.write(response)
#         return response.choices[0].message.content

def txt2json(txt_file):
    

    # with open(txt_file, 'r', encoding='utf-8') as f:
    #     file_content = f.read()

    prompt = (
        "You are an expert at extracting structured data from unstructured text. Below is a bank statement. "
        "Extract all transaction details, categorizing them into deposits/credits, withdrawals/debits, and checks. "
        "Each transaction should include:\n"
        "- Date\n"
        "- Description\n"
        "- Amount\n"
        "- Category (Deposit/Credit, Withdrawal/Debit, or Check)\n\n"
        "Input:\n" + txt_file
    )

    response = client.chat.completions.create(
        model=model,
        response_format={ "type": "json_object" },
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert at extracting structured data from unstructured text. Below is a bank statement "
                    "text file. Extract all the transaction details, categorizing them into deposits/credits, "
                    "withdrawals/debits, and checks. Each transaction should include: Date, Description, Amount, and Category."
                )
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
    )
    return response.choices[0].message.content


def txtpdf_json(txt_file):
    response = client.chat.completions.create(
        model=model,
        response_format={ "type": "json_object" },
        messages=[
            {
                "role": "system",
                "content": "You are a tool that converts plain text into JSON format."
            },
            {
                "role": "user",
                "content": txt_file
            }
        ]
    )
    json_result = response.choices[0].message.content


def save2db_response(details):

    response = client.chat.completions.create(
        model=model,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system",
             "content": (
                    "You are a data parsing assistant specializing in analyzing financial documents. "
                    "Your role is to extract relevant data and structure it into a clear JSON format."
                )
            },
            {"role": "user",    "content": save2db_prompt(details)},
        ],
        temperature=0.0,
    )
    return response.choices[0].message.content


def classify_b64_file(base64_file):
    prompt = (
        "Classify the following document as one of: bank statement, invoice, receipt, or other. "
        "Return only the category name."
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": [
                {"type": "text", "text": "Here is the document to classify."},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_file}", "detail": "high"}}
            ]}
        ],
        temperature=0.0,
    )
    return response.choices[0].message.content