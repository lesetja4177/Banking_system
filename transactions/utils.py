import dropbox
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from io import BytesIO
import os
from dotenv import load_dotenv
load_dotenv()

# Put your Dropbox access token here
DROPBOX_ACCESS_TOKEN = os.environ.get("DROPBOX_ACCESS_TOKEN")
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

def generate_receipt(user, transfer):
    # 1. Create PDF in memory (no local file needed)
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>Platinum Non-Resident Account</b>", styles["Title"]))
    elements.append(Paragraph("Transaction Receipt", styles["Heading2"]))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("<b>Customer Details</b>", styles["Heading3"]))
    user_data = [["Username:", user.username], ["Email:", user.email]]
    user_table = Table(user_data, colWidths=[150, 300])
    elements.append(user_table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("<b>Transaction Details</b>", styles["Heading3"]))
    transaction_data = [
        ["Amount:", f"${transfer.amount}"],
        ["Bank Name:", transfer.bank_name],
        ["Account Number:", transfer.account_number],
        ["Date:", str(transfer.created_at)],
        ["Status:", "Completed"],
    ]
    table = Table(transaction_data, colWidths=[150, 300])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Expected Delivery: Within 2-3 working days", styles["Normal"]))
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("Thank you for using Platinum Non-Resident Online checking Account.", styles["Italic"]))

    doc.build(elements)
    buffer.seek(0)  # Go to start of the PDF

    # 2. Upload to Dropbox App folder
    dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
    dropbox_path = f"/Apps/Save_Receipts/receipt_{transfer.id}.pdf"
    dbx.files_upload(buffer.read(), dropbox_path, mode=dropbox.files.WriteMode("overwrite"))

    # 3. Create a shareable link
    shared_link_metadata = dbx.sharing_create_shared_link_with_settings(dropbox_path)
    return shared_link_metadata.url  # This is the link you can give to admin or user