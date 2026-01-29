from langfuse_client import Client

import dotenv
CFG = dotenv.dotenv_values(".env")

lf_client = Client(
    api_key=CFG["LANGFUSE_SECRET_KEY"], 
    base_url=CFG["LANGFUSE_BASE_URL"]  # optional)
)
