import pdfplumber
import json
import re
import requests
from PIL import Image
import pytesseract
import io

import pytesseract

# Full path to the executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


API_KEY = "AIz..........."



def extract_text_and_tables_from_pdf(pdf_path):
    """
    Extracts text and tables from a PDF page by page.
    """
    pages_data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            tables = page.extract_tables()
            
            page_data = {
                "page_number": page_number,
                "text": text,
                "tables": tables
            }
            pages_data.append(page_data)
    return pages_data

def extract_images_with_ocr(pdf_path):
    """
    Extracts images from a PDF and performs OCR on them.
    """
    all_images_ocr = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                for image in page.images:
                    try:
                        # Crop the page to the image's bounding box to get the image object
                        cropped_page = page.crop((image['x0'], image['top'], image['x1'], image['bottom']))
                        # Convert the cropped page to a PIL Image object
                        img = cropped_page.to_image().original
                        
                        # Use pytesseract to perform OCR on the image
                        ocr_text = pytesseract.image_to_string(img)
                        if ocr_text.strip():
                            all_images_ocr.append({
                                "page_number": page.page_number,
                                "x0": image['x0'],
                                "y0": image['y0'],
                                "x1": image['x1'],
                                "y1": image['y1'],
                                "ocr_text": ocr_text.strip()
                            })
                    except Exception as e:
                        print(f"Error processing image on page {page.page_number}: {e}")
    except FileNotFoundError:
        print(f"Error: The file '{pdf_path}' was not found.")
    return all_images_ocr

def call_llm_api(page_data, ocr_data):
    """
    Calls the LLM API to parse a single page's content into structured JSON.
    Includes OCR text for charts and images.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={API_KEY}"
    
    #  JSON schema
    response_schema = {
        "type": "ARRAY",
        "items": {
            "type": "OBJECT",
            "properties": {
                "type": {"type": "STRING", "enum": ["paragraph", "table", "chart"]},
                "section": {"type": "STRING", "nullable": True},
                "sub_section": {"type": "STRING", "nullable": True},
                "text": {"type": "STRING", "nullable": True},
                "table_data": {"type": "ARRAY", "nullable": True, "items": {"type": "ARRAY", "items": {"type": "STRING"}}},
                "description": {"type": "STRING", "nullable": True}
            },
            "required": ["type"]
        }
    }

    # User prompting with our available data
    prompt_lines = [
        "You are a highly skilled document parser. Your task is to analyze the following content from a PDF page and extract structured information.",
        "",
        "The content is from a financial fact sheet. Identify paragraphs, tables, and charts. For tables, extract the data into a list of lists. For charts, provide a brief description and, if possible, extract the underlying data based on the OCR text provided.",
        "",
        f"The content from the page is:",
        f"--- Page {page_data['page_number']} Text ---",
        page_data['text'],
        "",
        f"--- Page {page_data['page_number']} Tables (parsed as lists) ---",
        str(page_data['tables']),
        "",
        f"--- Page {page_data['page_number']} OCR from Images/Charts ---",
        "\n".join([img['ocr_text'] for img in ocr_data]) if ocr_data else "No images found on this page.",
        "",
        "Ignore any page headers, footers, or watermarks. Do not include a preamble or any text before the JSON.",
        "",
        "Please return the result as a JSON object that adheres to the provided schema."
    ]
    prompt = "\n".join(prompt_lines)

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": response_schema
        }
    }

    try:
        response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling LLM API: {e}")
        return None

def main():
    """
    Main function to run the PDF parsing and JSON generation using an LLM.
    """
    pdf_file_path = "sample_pdf.pdf"
    json_output_path = "output_llm.json"

    try:
        pages_data = extract_text_and_tables_from_pdf(pdf_file_path)
    except FileNotFoundError:
        print(f"Error: The file '{pdf_file_path}' was not found.")
        print("Please ensure the 'sample_pdf.pdf' file is in the same directory as the script.")
        return

    extracted_content = []
    # Extract the images with OCR 
    all_images_ocr = extract_images_with_ocr(pdf_file_path)

    for page_data in pages_data:
        print(f"Processing page {page_data['page_number']}...")
        # Filter OCR data for the current page
        page_ocr_data = [item for item in all_images_ocr if item['page_number'] == page_data['page_number']]
        llm_response = call_llm_api(page_data, page_ocr_data)
        
        if llm_response and 'candidates' in llm_response and llm_response['candidates']:
            try:
                
                json_string = llm_response['candidates'][0]['content']['parts'][0]['text']
                # The model's response might have markdown. Let's clean it up.
                json_string = json_string.strip('`').strip('json').strip()
                page_content = json.loads(json_string)
                extracted_content.append({
                    "page_number": page_data['page_number'],
                    "content": page_content
                })
            except (json.JSONDecodeError, IndexError) as e:
                print(f"Could not parse JSON response for page {page_data['page_number']}: {e}")
                print(f"Raw LLM response: {llm_response}")
                
    # Saving the final structured data to a JSON file
    try:
        with open(json_output_path, 'w', encoding='utf-8') as f:
            json.dump({"pages": extracted_content}, f, ensure_ascii=False, indent=2)
        print(f"Successfully extracted and saved LLM-parsed data to '{json_output_path}'")
    except IOError as e:
        print(f"Error: Could not write to file '{json_output_path}'. Reason: {e}")

if __name__ == "__main__":
    main()
