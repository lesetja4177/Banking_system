import dropbox
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from io import BytesIO

# Put your Dropbox access token here
DROPBOX_ACCESS_TOKEN = "sl.u.AGZLI12yYK61Wnj7dT2ss3b3jTS_Vp4Ye0xIpJZ-_BmKJb7hgcnFLHAE609-6prX7_7DggcvUAGsnEAZmLt9yp8KkJYqARDPWzIqi68Nhe83_oMj6ASjMLHixHiI2GtChnJ_aKQE7z2o3arLjErbZuFB1j7fUDF-aj9QsinLhtsNzmLM1QzKTwi6grbMJ5jQMArBStI9EGhwL6H71Wun5gv_7ZFvNHFHnzbBQKE6y-ysb-FpfiQZQGYuhx1KaZin09LvPpQoIg-i99dsJoIq0wm4VWXMN3R0lddFpkf5VbMGjxCCpIL58mItjqmcmu6VJ8w-fEkVCiGSwyr0_3zjQ_G2ov6kmbeiccAXcD9a-vrR0RPjMJM6DUywQ1i_IGYzk0kTr5OLMg5k0HE9ZP4nRLliHrqFluKNEHBxXdkDKo76MyY3VCt4XFZmp1nFSe5nowYP7xBWB5MLu2PxL1CBZmqvPeABzDkAgsOBKve06NhEdRC5JtodG_38PNSJVSliZCvv5H6oo36zvvsiycqbc5LQlu3nQAyo_Qx4iKEpykQcPQPiVLVjWRa4qMs63b7FuciHT-UfK9CqJJ0ZTO0ozbGQJNwF0Nq85ZTRMtCQwXzlO_ujvtZnlPFUIOIZnP88DyIU1xjbsGgdGhLoPUbGLzGrVSxtE3MMEPTR_X8iZt3YTrNAI2lHXFH0PTfw7cnjhgws4fCa4uPHXULoonpyGze5qUIqW5kbEcRe6ngR0QnJpWALeW3CYPtnpvseEJlpdc1RXilIE7RGxR23FhZxhuED_-o-pyPnbzFk1oJ7-JbNuLRTlFCTBzWOL6Q85GrPnM2s_4W42YZ0vpW3C9mIU2G500bNXJwQfktY_XnsswpNWKR_rewwIpuo6R96hVEDqkuzVo8S208d_vWsIUH2PUnnHwK8GgGq1LY3WTc3eNT7g4Wd4GCre-8PrcHZvle0CpYoRnGpeI7chZRRzBvBLpy8gftJUWMCr7PI6LPdhwoyAeODbnGbzCeVpHrB9uVsor-yMWP8bpyoBENlKg9Fb2xq9o8wPileWIf9yL1aQAvpJqKyq5qBgzAwzsdernwTz6fxH7ypSywMrXlzigGaP4VWsBJYwiRTiDh_g_zejtn7DyamvvE-uxNrceT2-6YniK4_YYV5Lb69QxOdaKBkVmjC_DW0O_havQNd56zOBMwQNEUXbjOKa606JEHBCjzflFbytMKSrJr-l7sCGkeBJp0v-OmyahrUS8-ssXRN5Vm4xcPSyhM2GrsUARimahMybXM7MMk3kfxlpVlFIHg5xxhHDEfRpHoL4Px6ncb7N-vOmv0LSXEeAzwy36KJ8w_BzJKFaHLhEVa6wZWPCLnvNF5ZDU1cOGcvX2P70qOgvOH1oakUPuFQzmIREQCzpzxT4rPZDKDW66rdjP-scdYh2GfGd7gkxBpxq0G7qiH3RM0UQzCc_0uY-jgY8HBioIs9WiM"

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
        ["Amount:", f"₦{transfer.amount}"],
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