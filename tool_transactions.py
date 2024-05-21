'''
Standalone tool to process a bunch of paypal PDFs and output a CSV. Used for tracking expenses

Expects paypal PDFs to be housed in a "tools/transactions" folder
    
USAGE EXAMPLE:
	python tool_transactions.py
'''


import os
import fitz
import csv
import re
from datetime import datetime

def _ExtractTextFromPdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

def _ExtractPaypalData(text):
    # Regular expressions for the required fields
    text_parts = text.split('\n')
    
    for i, part in enumerate(text_parts):
        print(f'{i} - {part}')
    
    date = _SimplifyDate(text_parts[3])
    desc = _GetDescription(text_parts)
    amount = _SimplifyMonetaryAmount(_FindTextField('Gross amount', text_parts))
    trans_ID = 'Transaction ID : ' + _FindTextField('Transaction ID', text_parts)
    
    return [
        {
            'Date': date,
            'Description Note': desc,
            'Monetary Amount': amount,
            '': '',
            'Transaction ID': trans_ID
        }
    ]
    
def _FindTextField(field_name, text_parts):
    found_field = False
    for part in text_parts:
        if found_field:
            return part
        if part.strip() == field_name:
            found_field = True


def _GetDescription(text_parts):
    desc = ""
    found_desc = False
    name = ''
    for part in text_parts:
        if part == 'Amount details':
            return name + ' - ' + desc
        if found_desc:
            desc += part
        if not found_desc and part.startswith('Note to Clement Swennes'):
            name = part[8:]
            found_desc = True

def _SimplifyDate(date_string):
    input_format = "%B %d, %Y at %I:%M:%S %p"
    output_format = "%-m/%-d/%Y"
    parsed_date = datetime.strptime(date_string, input_format)
    simplified_date = f"{parsed_date.month}/{parsed_date.day}/{parsed_date.year}"
    return simplified_date
    
def _SimplifyMonetaryAmount(amount_string):
    # Remove any non-breaking spaces
    cleaned_string = amount_string.replace('\xa0', '')
    
    # Remove the currency symbol and any non-numeric characters except for - and .
    cleaned_string = cleaned_string.replace('$', '').replace('USD', '').strip()
    
    # Filter out unwanted characters
    simplified_amount = ''.join(char for char in cleaned_string if char.isdigit() or char in ['-', '.'])
    
    return simplified_amount

def _ProcessPaypalPdfs(folder_path):
    data = []
    for filename in os.listdir(folder_path):
        print(f'processing {filename}...')
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(folder_path, filename)
            text = _ExtractTextFromPdf(pdf_path)
            extracted_data = _ExtractPaypalData(text)
            data.extend(extracted_data)
    return data

def _WriteToCsv(data, csv_path):
    with open(csv_path, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['Date', 'Description Note', 'Monetary Amount', '', 'Transaction ID']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in data:
            writer.writerow(row)

def main():
    #folder_path = input("Enter the folder path containing PayPal PDFs: ")
    folder_path = "tools/transactions/"
    csv_output_path = "tools/csv_data.csv"
    
    paypal_data = _ProcessPaypalPdfs(folder_path)
    _WriteToCsv(paypal_data, csv_output_path)
    print(f"Data has been successfully written to {csv_output_path}")

if __name__ == "__main__":
    main()
