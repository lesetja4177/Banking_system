import dropbox
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()

DROPBOX_ACCESS_TOKEN = os.environ.get("DROPBOX_ACCESS_TOKEN")
if not DROPBOX_ACCESS_TOKEN:
    raise Exception("DROPBOX_ACCESS_TOKEN not set in environment variables")

dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

def generate_receipt(user, transfer):
    # 1. Create PDF in memory
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
        ["Bank Name:", transfer.bank_name or "N/A"],
        ["Account Number:", transfer.account_number or "N/A"],
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
    elements.append(Paragraph("Thank you for using Platinum Non-Resident Online Checking Account.", styles["Italic"]))

    doc.build(elements)
    buffer.seek(0)

    # 2. Upload to Dropbox
    dropbox_path = f"/Apps/Save_Receipts/receipt_{transfer.id}.pdf"
    try:
        dbx.files_upload(buffer.read(), dropbox_path, mode=dropbox.files.WriteMode("overwrite"))
    except dropbox.exceptions.ApiError as e:
        print("Dropbox upload error:", e)
        return None

    # 3. Create or get a shared link
    try:
        links = dbx.sharing_list_shared_links(path=dropbox_path, direct_only=True).links
        if links:
            return links[0].url
        shared_link_metadata = dbx.sharing_create_shared_link_with_settings(dropbox_path)
        return shared_link_metadata.url
    except Exception as e:
        print("Dropbox shared link error:", e)
        return None