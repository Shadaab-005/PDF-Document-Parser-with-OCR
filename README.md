# PDF Document Parser with OCR and Gemini LLM

This project extracts **text, tables, and images (with OCR)** from PDF files and transforms the content into a **structured JSON format** using **Google’s Gemini LLM API**.

---

## ✨ Features

* **Text & Table Extraction**:
  Uses [pdfplumber](https://github.com/jsvine/pdfplumber) to read page text and detect tables as lists of lists.
* **Image OCR**:
  Detects embedded images on each page and applies [pytesseract](https://pypi.org/project/pytesseract/) to extract text from charts or scanned content.
* **LLM-Powered Structuring**:
  Sends all extracted text, tables, and OCR data to the Gemini API to receive **clean, schema-validated JSON** with:

  * Paragraphs
  * Tables (with data arrays)
  * Charts (with OCR-based descriptions)
* **Automatic JSON Output**:
  Stores final results in a single `output_llm1.json` file.

---

## 🗂️ Project Structure

```
project/
│
├─ main.py                  # The script (code shown above)
├─ sample_pdf.pdf           # Input file to parse (replace with your own)
└─ output_llm.json         # Output JSON created after running the script
```

---

## 🛠️ Requirements

| Package      | Purpose                           |
| ------------ | --------------------------------- |
| pdfplumber   | Extract text and tables from PDFs |
| pytesseract  | OCR for images and scanned pages  |
| Pillow (PIL) | Image manipulation for OCR        |
| requests     | HTTP calls to Gemini API          |

Install them:

```bash
pip install pdfplumber pytesseract pillow requests
```

You also need:

* **Tesseract OCR Engine**:
  Download and install from [Tesseract GitHub](https://github.com/tesseract-ocr/tesseract).
  Update the path in the script:

  ```python
  pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
  ```

---

## ⚙️ Setup

1. **Clone / Copy the Code**
   Place the script in your project folder.

2. **Google Gemini API Key**

   * Get an API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
   * Replace the placeholder in the code:

     ```python
     API_KEY = "YOUR_REAL_API_KEY"
     ```

3. **Add a PDF File**

   * Place your target PDF in the same folder, or change the path:

     ```python
     pdf_file_path = "sample_pdf.pdf"
     ```

---

## ▶️ Run the Script

```bash
python main.py
```

* Each page is processed sequentially.
* A new file `output_llm.json` will contain the structured output.

---

## 🔑 Output Format

The generated JSON follows this structure:

```json
{
  "pages": [
    {
      "page_number": 1,
      "content": [
        {
          "type": "paragraph",
          "section": "Overview",
          "sub_section": null,
          "text": "Cleaned paragraph text..."
        },
        {
          "type": "table",
          "table_data": [["Header1", "Header2"], ["Row1Col1", "Row1Col2"]]
        },
        {
          "type": "chart",
          "description": "Chart description extracted from OCR text."
        }
      ]
    }
  ]
}
```

---

## 🧩 Customization

* **Input/Output Paths**: Change `pdf_file_path` or `json_output_path` in `main()`.
* **LLM Prompt**: Adjust the instructions inside `call_llm_api()` to tailor the parsing logic.

---




