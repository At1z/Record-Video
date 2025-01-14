import os
import aspose.words as aw # type: ignore

def convert_docx_to_pdf(email, docx_path, pdf_path=None):
    """
    Convert a .docx file to a .pdf file using aspose.words
    """
    if not os.path.exists(docx_path):
        print(f"Error: The file '{docx_path}' does not exist.")
        return

    if pdf_path is None:
        pdf_path = os.path.splitext(docx_path)[0] + ".pdf"

    try:
        # Load the DOCX file
        doc = aw.Document(docx_path)
        
        # Save as PDF
        doc.save(pdf_path)
        print(f"PDF successfully created at: {pdf_path}")
    except Exception as e:
        print(f"Error occurred while converting: {e}")
