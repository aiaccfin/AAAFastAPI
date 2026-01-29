import fitz  , io, os, base64

from pdf2image import convert_from_path
from PIL import Image


@staticmethod
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def pdf_to_base64_images_fitz(pdf_path):
    #Handles PDFs with multiple pages
    pdf_document = fitz.open(pdf_path)
    base64_images = []
    temp_image_paths = []

    total_pages = len(pdf_document)

    for page_num in range(total_pages):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes()))
        temp_image_path = f"temp_page_{page_num}.png"
        img.save(temp_image_path, format="PNG")
        temp_image_paths.append(temp_image_path)
        base64_image = encode_image(temp_image_path)
        base64_images.append(base64_image)

    for temp_image_path in temp_image_paths:
        os.remove(temp_image_path)

    return base64_images


def pdf_to_base64_images(pdf_path, dpi=300):
    # Convert PDF pages to images
    images = convert_from_path(pdf_path, dpi=dpi)
    base64_images = []

    for page_num, img in enumerate(images):
        # Save each page as a temporary PNG image
        temp_image_path = f"temp_page_{page_num}.png"
        img.save(temp_image_path, format="PNG")

        # Convert the temporary image to base64
        with open(temp_image_path, "rb") as img_file:
            base64_image = base64.b64encode(img_file.read()).decode("utf-8")
            base64_images.append(base64_image)

        # Remove the temporary image file
        os.remove(temp_image_path)

    return base64_images



def pdf_2_images_path(pdf_path):
    # Convert PDF pages to images
    pdf_folder = os.path.abspath("./tmp/pdf")
    print(3)
    print(pdf_path)
    images = convert_from_path(pdf_path, dpi=200)
    print(4)
    print(images)
    images_path = []

    for page_num, img in enumerate(images):
        temp_image_path = os.path.join(pdf_folder, f"temp_page_{page_num}.png")
        images_path.append(temp_image_path)
    print(5)
    print(images_path)

    return images_path


def pdf_2_images_path_fitz(pdf_path):
    pdf_folder = os.path.abspath("./tmp/pdf")
    pdf_document = fitz.open(pdf_path)
    temp_image_paths = []

    total_pages = len(pdf_document)

    for page_num in range(total_pages):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes()))

        temp_image_path = os.path.join(pdf_folder, f"temp_page_{page_num}.png")
        img.save(temp_image_path, format="PNG")
        temp_image_paths.append(temp_image_path)

    return temp_image_paths


def pdf_to_one_b64(pdf_path, dpi=300):
    # Convert only the first page of the PDF to image
    images = convert_from_path(pdf_path, dpi=dpi, first_page=1, last_page=1)
    if not images:        return None

    img = images[0]
    temp_image_path = "temp_page_0.png"
    img.save(temp_image_path, format="PNG")

    # Convert the image to base64
    with open(temp_image_path, "rb") as img_file:
        base64_image = base64.b64encode(img_file.read()).decode("utf-8")

    os.remove(temp_image_path)
    return base64_image