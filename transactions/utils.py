import dropbox
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from io import BytesIO

# Put your Dropbox access token here
DROPBOX_ACCESS_TOKEN = "sl.u.AGZgnIbPVCqZg4BI9S5fx2XhOPnXfBZNwtZMSmmedSxTCoWHXJSjYlW_ka5tdavoF0rOfiz7qSRWvAfZycdm20mVItHl_tFuQVst3v3Kcj0s71WIOo_PP-nSteWRbztQgCens7IxtaCibbr7qJbjRkL9KD0LPfDTE6q55dYjG39f0ZMFvta4qGD6JgRUcGpmkBdoQrZh0VskJaEp4sRWqPHaVomh5OT9dYszVxP8PWbDiUZaXBXGAufC2ef7UmylQpnshp0wuF53eknofGMusFHdaqrikZGIc3GjjKxm10EcyddSWrzg836BubJhM9ScBhgTH-JGZQ1rW9eRcAMiSxm9-uLf8nS0jZ9xN4izecEBm6tMqwAE_xnr_LXjEsn9RcosghfLR4A47pZYi3eFuL3xDiVyM72maxRIKnHUMf1UodP9TFpdng2UKiKQt5eVIo_OOiLgOh6k9dZCAnCT4WyMYhxD9nx3sovXfyqC0hhlUkRuT68HhtLZnQ_6LAEYE4jCJiO519KStbqyMX7oa9NK-FHCzwgrrtMhdvz_BSuNdMKj7XwzzS6kldLvtOoLz89Ot92yUSgZnOaYxh820dfmJzloCyI1jp7q99R9_JG6Np86YAuns1yiyhud8zQU3GYuiW49PelgDIZGzs_jVt_Y46gpdIawdIGaOaXhYb7qwEg6Q5waPODAq47m2C1HdaTbyeZiVsINcSa-lshJ_a_X0MRakvCBQHPGMqV_eNP-q9ScVk4uGtaItk8jlV7GxbRN8UbuNEtXCWFkosNSFTPwsrgklSkQ7nTTbZqMs8i_UMRhT5GMYE-juB-ZLLzQdx18nKZ1b7Xp3eECgnoEFAx6UCmhMjWASg9ruReA817e904Jz1ZsnsKdfY3S6wRjOIyjHSWMnWid8dPz-gYHx2xykp_uRvf-tKGV0JZUJnL8-Py37rXsMi4KtzIzfLVJDiF1fmJFpGb3oJiBUk9Lid1epzkPWJ0ThL8WMgfnfTnwTO0iNS5yX8Gnf18xrcPFK2zDNkzL-gII5N62_vipVqRSIayNZUpsqSh-eN3Qw6JGI7IzCdQXxW9qjzJWkTUFYs35U9km24HzDGGKnWeqbfQ-c45v-uFwMBBdwKifjJ3JdXCE_3tWWe9zSVP0pAuPLMnRUWvI-Ykjdr_tBqIbAPcsuUsQEMi8aJlpH9jzAmPxRsVSsancMf4k8nWTp0qccgyn62DTHS83OdzgtOj3PIJwjMhYzSZQE1h2oref6Ce4ID4yMOnsdKoJ1Y5MF9ZeXaOIH3byKE0JdZjJmdRZKP45qN-gTScc6sIuJDnO76afl3JK0UosGPmcFtTe-ht7BWRsQd8n_0urcYBfMcq0JZBX2nOVPvFgyilTvkJaqoyP7kFXkdw1dGX7N_Ex-wKW0utAJzCYsvUaU6d1vc8VTglKrE9edaG2jH3HWXQ9XQu2FLf4dvsGiXp-M0CG4GKyEXw"

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