import os
import fitz  # PyMuPDF
import re
import string
from num2words import num2words


def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF while removing bold and center-aligned lines.
    Skips lines with slide references.
    Converts the text to lower case.
    Converts numbers to their equivalent spoken word representations.
    Removes punctuation.

    Args:
    - pdf_path: Path to the PDF file.

    Returns:
    - Extracted text as a string.
    """
    text = ""
    try:
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            blocks = page.get_text("dict")["blocks"]  # Extract blocks of text
            
            for block in blocks:
                if block['type'] == 0:  # If it's a text block
                    for line in block['lines']:
                        line_text = ""
                        is_bold = False
                        is_center_aligned = False
                        is_slide_ref = False

                        for span in line['spans']:
                            # Check if the text is bold
                            if 'bold' in span['font'].lower():
                                is_bold = True
                            # Check if the text is center-aligned by looking at x coordinate
                            if span['bbox'][0] == span['bbox'][2]:
                                is_center_aligned = True

                            line_text += span['text']

                        if re.search(r"\(refer.* time: \d\d:\d\d\)", line_text.lower()):
                            is_slide_ref = True

                        def replace_digits_with_words(match):
                            return num2words(match.group())
                        
                        # Replace digits by their spoken form
                        line_text = re.sub(r'\b\d+\b', replace_digits_with_words, line_text)

                        #remove punctuation
                        line_text = line_text.translate(str.maketrans("", "", string.punctuation))

                        # make lower case
                        line_text = line_text.lower()
                        
                        # If line is not bold and not center-aligned, keep it
                        if not is_bold and not is_center_aligned and not is_slide_ref:
                            text += line_text
    
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")

    if not text.strip():  # If the extracted text is empty, log a warning
        print(f"No text extracted from {pdf_path}.")

    return text


def save_text_to_file(text, output_path):
    """
    Save the processed text to a file.
    """
    try:
        if not text.strip():  # Avoid saving empty text
            logging.warning(f"Attempted to save empty text to {output_path}. Skipping.")
            return

        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(text)

    except Exception as e:
        print(f"Error saving file {output_path}: {e}")


def process_pdfs(input_dir, output_dir):
    """
    Process all PDF files in the input directory and save the processed text in the output directory.
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.isdir(input_dir):
        logging.error(f"The input directory {input_dir} is not valid.")
        return

    for file_name in os.listdir(input_dir):
        if file_name.endswith('.pdf'):
            pdf_path = os.path.join(input_dir, file_name)
            output_path = os.path.join(output_dir, os.path.splitext(file_name)[0] + '.txt')

            print(f"Processing {file_name}...")

            # Extract text
            processed_text = extract_text_from_pdf(pdf_path)

            if processed_text:
                # Save text to file
                save_text_to_file(processed_text, output_path)

            else:
                print(f"No text extracted from {file_name}, skipping save.")


if __name__ == "__main__":
    import argparse

    # Argument parser for command-line usage
    parser = argparse.ArgumentParser(description="Convert PDFs to text while removing bold and center-aligned text.")
    parser.add_argument("input_dir", help="Directory containing PDF files.")
    parser.add_argument("output_dir", help="Directory to save processed text files.")
    args = parser.parse_args()

    # Process PDFs
    process_pdfs(args.input_dir, args.output_dir)
