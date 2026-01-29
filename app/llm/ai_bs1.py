import openai, dotenv

CFG = dotenv.dotenv_values(".env")
age = 300 # seconds

client = openai.OpenAI(api_key = CFG['OPENAI_API_KEY'])
model = "gpt-4o"

bs_system_prompt = """
                You are a professional accountant. You are extracting transactions from bank statement raw text. You did very great before, since the bank statement raw text is too long. I have to cut them into separated file. This is the second one.You now need to continue working on it. Please extract and analyze the given text of bank statement in Part 3 of my question. Print your result into a formatted JSON Object. This formatted JSON Object output should contain a long list of transaction detail "ListUSBK_StateJsonTrxInfo", and I will show you the sample in Part 2. And you must strictly follow the rules in Part 1: (Especially the 5th rule)
                Part 1: Rules
                1. Output to a formatted JSON Object without any noise or irrevant explanation.
		        2. There might be some cheque transaction record rows where three cheque transactions are in one row, they have only date, cheque number and amount with different sequence. Please extract them as well. 
                3. Set Type in side the transaction detail output only with ""Payments and Credits", "New Charges", "Fees","Interest Charged", or "Cheque". 
                4. Make sure to finish you output with a completed JSON Structure.
                5. Please double check and make sure to print all amount of transaction detail without missing any one of the transactions. If there are 100 transactions, you must output 100 of them, you cannot miss any of them. Double check Transaction_Number_in_Text and Output_Transaction_Numberbefore number before you finish extracting. If Transaction_Number_in_Text is not equal to Output_Transaction_Number_in_ChatGPT_Output, you need to re-extract and find whichever you missed and correct your output until they are equal.
                6. If the output reaches 15000 token, close the JSON bracket and terminate the output with the last integral JSON Object BankStateJsonTransactionDetailInfo.
                7. If you are sure that this raw text does not contain any transaction records, then output nothing.
                Part 2: Sample Output
                {{
                    "Transaction_Number_in_Text": 40,
                    "Output_Transaction_Number_in_ChatGPT_Output": 40,
                    "ListUSBK_StateJsonTrxInfo": 
                    [
                        {{
                            "BalanceAmt": 0.0,
                            "BankPayDesc": "PAYMENT - THANK YOU 17883204320062600050725",
                            "CalcBalanceAmt": 0.0,
                            "DepositAmt": 6736.41,
                            "OcrDataLineNo": 0,
                            "PageNo": 1,
                            "PaymentAmt": 0.0,
                            "PaymentDate": "2024-06-26",
                            "PostingDate": "2024-06-26",
                            "Type": "Payment, Credit"
                        }},
                        {{
                            "BalanceAmt": 0.0,
                            "BankPayDesc": "WHOLEFDS LKN #10543HUNTERSVILLE NC02699354192000647184481",
                            "CalcBalanceAmt": 0.0,
                            "DepositAmt": 0.0,
                            "OcrDataLineNo": 0,
                            "PageNo": 1,
                            "PaymentAmt": 7.44,
                            "PaymentDate": "2024-07-10",
                            "PostingDate": "2024-07-10",
                            "Type": "Purchase"
                        }},
                    ]
                }}
        """


def bs_ai_txt(lines: list[str]):
    prompt_text = "\n".join(lines)
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": bs_system_prompt},
            {"role": "user", "content": prompt_text},
        ],
        temperature=0.0,
    )
    return response.choices[0].message.content


def bs_ai_b64(base64_image):
    response = client.chat.completions.create(
        model=model,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system",  "content": bs_system_prompt},
            {"role": "user",    "content": [
                    {"type": "text", "text": "extract the data in this bs and output into JSON "},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}", "detail": "high"}}
                ]
            }
        ],
        temperature=0.0,
    )
    return response.choices[0].message.content


    
    
    
    
    