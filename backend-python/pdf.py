import os
import aspose.words as aw # type: ignore
from senderToEmail import send_file_via_email

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
        doc = aw.Document(docx_path)
        doc.save(pdf_path)
        print(f"PDF successfully created at: {pdf_path}")
    # Send the PDF via email if email provided
        ##if email:
        ##    send_file_via_email(
        ##        recipient_email=email,
        ##        file_path=pdf_path,
        ##        subject="Here is your PDF from video-presentation",
        ##        body="It's contains two file summarization and mian PDF."
        ##    )
            
    except Exception as e:
        print(f"Error occurred while converting: {e}")