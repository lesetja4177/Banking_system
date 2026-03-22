from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import os


def generate_receipt(user, transfer):

    file_name = f"receipt_{transfer.id}.pdf"
    file_path = os.path.join("media", file_name)

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()

    elements = []

    # ===============================
    # HEADER
    # ===============================
    elements.append(Paragraph("<b>VSavings</b>", styles["Title"]))
    elements.append(Paragraph("Transaction Receipt", styles["Heading2"]))
    elements.append(Spacer(1, 20))

    # ===============================
    # USER INFO
    # ===============================
    elements.append(Paragraph("<b>Customer Details</b>", styles["Heading3"]))

    user_data = [
        ["Username:", user.username],
        ["Email:", user.email],
    ]

    user_table = Table(user_data, colWidths=[150, 300])
    elements.append(user_table)
    elements.append(Spacer(1, 20))

    # ===============================
    # TRANSACTION DETAILS
    # ===============================
    elements.append(Paragraph("<b>Transaction Details</b>", styles["Heading3"]))

    transaction_data = [
        ["Amount:", f"₦{transfer.amount}"],
        ["Bank Name:", transfer.bank_name],
        ["Account Number:", transfer.account_number],
        ["Date:", str(transfer.created_at)],
        ["Status:", "Completed"],
    ]

    table = Table(transaction_data, colWidths=[150, 300])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    # ===============================
    # DELIVERY INFO
    # ===============================
    elements.append(Paragraph(
        "Expected Delivery: Within 2-3 working days",
        styles["Normal"]
    ))

    elements.append(Spacer(1, 30))

    # ===============================
    # FOOTER
    # ===============================
    elements.append(Paragraph(
        "Thank you for using VSavings.",
        styles["Italic"]
    ))

    # BUILD PDF
    doc.build(elements)

    return file_path