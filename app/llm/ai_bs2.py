import openai, dotenv

CFG = dotenv.dotenv_values(".env")
age = 300 # seconds

client = openai.OpenAI(api_key = CFG['OPENAI_API_KEY'])
model = "gpt-4o"



bs_system_prompt = """
    You are a professional accountant. You are extracting transactions from bank statement raw text. Please extract and analyze the given text of bank statement in Part 3 of my question. Print your result into a formatted JSON Object. This formatted JSON Object output should contain a long list of transaction detail "ListUSBK_StateJsonTrxInfo"  and a summary information "US_BK_StateJsonSumInfo". I will give you the sample output in part 2. You must strictly follow the rules in Part 1:(Especially the 6th rule)
            Part 1: Rules
	        1. Output to a formatted JSON Object contains Transaction_Number_in_Text, Output_Transaction_Number_in_ChatGPT_Output, US_BK_StateJsonSumInfo and ListUSBK_StateJsonTrxInfo without any noise or irrevant explanation.
            2. Set "StateSrc_Type" to 1 when the statement is confirmed to be a credit card statement, othervise set it to 0 if it's a debit account bank statement. 
            3. Set Type in side the transaction detail output only with ""Payments and Credits", "New Charges", "Fees","Interest Charged", or "Cheque". 
            4. There might be some cheque transaction record rows where three cheque transactions are in one row, they have only date, cheque number and amount with different sequence. Please extract them as well. 
            5. Make sure to finish you output with a completed JSON Structure.
            6. Please double check and make sure to print all amount of transaction detail without missing any one of the transactions. If there are 100 transactions, you must output 100 of them, you cannot miss any of them. Double check Transaction_Number_in_Text and Output_Transaction_Numberbefore number before you finish extracting. If Transaction_Number_in_Text is not equal to Output_Transaction_Number_in_ChatGPT_Output, you need to re-extract and find whichever you missed and correct your output until they are equal.
            7. If the output reaches 15000 token, close the JSON bracket and terminate the output with the last integral JSON Object BankStateJsonTransactionDetailInfo.
            8. If you are sure that this raw text does not contain any transaction records, then output nothing.
            Part 2: Sample JSON Output
            {{
                "Transaction_Number_in_Text": 40,
		        "Output_Transaction_Number_in_ChatGPT_Output": 40,
                "US_BK_StateJsonSumInfo": {{
                    "BKStateEndDate": "2024-07-11",
                    "BKStateRawData": "",
                    "BKStateStartDate": "2024-06-12",
                    "BankAccNo": "5474 1516 2268 7538",
                    "BankCode": "BOA",
                    "BankName": "Bank of America",
                    "CloseBalanceAmt": -2607.69,
                    "OpenBalanceAmt": 1165.13,
                    "StateSrc_Type": 1,
                    "Status": 0,
                    "TotCalcDepositAmt": 0.0,
                    "TotCalcPaymentAmt": 0.0,
                    "TotDepositAmt": 0,
                    "TotPaymentTrxAmt": 0,
                    "companyName": "CORAL YANG CORP" }},
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


    
    
    
    
    