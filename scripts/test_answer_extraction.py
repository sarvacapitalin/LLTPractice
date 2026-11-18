from scripts.test_cell_extractor import extract_pdf_cells

def inspect_answers(pdf_path, cid, total, missing_snos=None):
    if missing_snos is None:
        missing_snos = {}
    pages = extract_pdf_cells(pdf_path, cid)
    
    # Let's inspect page by page
    # In each page, questions appear in order of appearance in the stream or by X coordinate
    # Let's see how questions and their rows are organized.
    print(f'=== Answers for {pdf_path} ===')
    
inspect_answers('road-signs-english.pdf', 299, 94)
