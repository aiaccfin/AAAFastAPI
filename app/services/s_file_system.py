import os, uuid

async def save_upload_file(oUploadFile):
    upload_folder = os.path.abspath("./tmp/v6")
    upload_name = f"{upload_folder}/{oUploadFile.filename}"
    os.makedirs(upload_folder, exist_ok=True)

    # Save uploaded PDF temporarily
    with open(upload_name, "wb") as f:
        f.write(await oUploadFile.read())

    return upload_name, upload_folder


async def save_img(oUploadFile):
    print(5)
    pdf_folder = os.path.abspath("./tmp/img")
    pdf_name = f"{pdf_folder}/{oUploadFile.filename}"
    os.makedirs(pdf_folder, exist_ok=True)
    print(5)

    # Save uploaded PDF temporarily
    with open(pdf_name, "wb") as f:
        f.write(await oUploadFile.read())

    return pdf_name, pdf_folder


async def save_upload_file_2_uuid(oUploadFile):
    upload_folder = os.path.abspath("./tmp/v7")
    
    # Get the file extension from the original file
    _, file_extension = os.path.splitext(oUploadFile.filename)
    
    
    # Generate a UUID for the uploaded file and append the original extension
    uuid_name = str(uuid.uuid4())
    unique_filename = f"{uuid_name}{file_extension}"
    upload_name_uuid = os.path.join(upload_folder, unique_filename)
    
    os.makedirs(upload_folder, exist_ok=True)
        
    # Save uploaded file temporarily
    with open(upload_name_uuid, "wb") as f:
        f.write(await oUploadFile.read())

    return uuid_name, upload_folder, upload_name_uuid


# async def save_upload_file_2_uuid(oUploadFile):
#     # Base folders
#     base_folders = {
#         "v6": "./tmp/v6",
#         "v61": "./tmp/v61",
#         "v62": "./tmp/v62"
#     }

#     # File extension from the original file
#     _, file_extension = os.path.splitext(oUploadFile.filename)

#     # Generate UUIDs
#     uuid_name = str(uuid.uuid4())
#     uuid_name1 = str(uuid.uuid4())
#     uuid_name2 = str(uuid.uuid4())

#     # Unique filenames
#     filenames = {
#         "v6": f"{uuid_name}{file_extension}",
#         "v61": f"{uuid_name1}{file_extension}",
#         "v62": f"{uuid_name2}{file_extension}",
#     }

#     # Make sure all folders exist
#     for folder in base_folders.values():
#         os.makedirs(os.path.abspath(folder), exist_ok=True)

#     # Read file content once
#     file_bytes = await oUploadFile.read()

#     # Save file into each folder
#     saved_paths = {}
#     for key, folder in base_folders.items():
#         full_path = os.path.join(os.path.abspath(folder), filenames[key])
#         with open(full_path, "wb") as f:
#             f.write(file_bytes)
#         saved_paths[key] = full_path

#     return {
#         uuid_name,
#         uuid_name1,
#         uuid_name2,
#     }