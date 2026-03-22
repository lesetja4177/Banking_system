import dropbox
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from io import BytesIO

# Put your Dropbox access token here
DROPBOX_ACCESS_TOKEN = "sl.u.AGYSC3zJeSE0BDDHuzTHjgCyWzhrLkSHYkuaIpowsLs6MM0F7xOQhpGNywaK0b971DZ2sJl7Y481wdyhqv-vKc1KpNeJy11-3AvPnBlViVhPXLb6fZYqul1SgHAoIpjCibhtzAdxlKr0JIP9aqPhiSdmGGdypOITD9DXW24nzJsKzfGE76Vj9E9DfhLlo9nQmPdT1FlK_CM17_xluOf85GOA1T61iA6bW0R3oh0VcC8Wp9AYwdM7Ju8ce4TxDntSBevkl1VBK-5eSv9bRdpvg8KmoO0TFGBT8q3t20sl0ADQUIwMAyesU5DHE1G7xbxPSoJI7qX0gjxAaq2Y66zvs5Bu3KLgifziPmg2v-Hcw5mR5I2beMAgJPIvumtSATgT9OvuGfSuhkDgiuC2wYK84XSeEG7tq291ucp2e0tz5JdJsnywqUjvlLbRDPNSnLqX2oEKsUjsW4cBuuD-JjHDh_cOITa_DKuFtSszvWbtzMbeJ_Hi-cezqh8lLjbVO5PLMQJEA_gNH-ATx9qDaMgOJpaqqFOq3Qg6vpSubIFJWWolw3B4uycdfp7TxDQxiCSi6UGpY8WxyWyWg5x2P5Xs9d7xtyWVqEAzAxK4SSeIjvGsBnkVbAcKCwFiyl2SL7hpDZgLCHKBS7-DQ3EadfcvhM6PeocP45fwc8u_kSQ7OQIXjAurlax1YfMwo4vu7IjpTnUPPM48d6cygdZu6_cyzhITvP38Rysgq-0TbBGOcOtYyhxECu1LK0YKn0TzgmFh8_zp_x8Nbaqr04q7uZ6ZobdIPhD-z35sVn9Qm5GIvU4AlcoQzGdjbySgVEXnsPCDTjXboKRRzBdyqG0B2Zbr0nzJZfRf7yNlWfYdnoN8G2gf2HvozBhimbOpvsfzwBHWfKtXbPDk3Iw5t5fp5R9elglRDR-AnNL-aKEPdfAeMhPGj3yVt7oYZi4frPrt12tZ6Jzx3rSUlkOPLkTYiFfU7DAebJukxg8mwkftzQa1lDHkoYRZMz6CAqI9nMsq2BsDwJ-Dw870foOEr3Bpvj1ac4NDTK775S3ih8sBJo8fFjtB7-tLU--mftI71iSTdGsiYpa0YY5PPRJQ-yqdBogRbMvK2uezobO4e8Q4iS8PvyGFjm8gpt2Y-_P3zebnsa9-LW3vKRuBpQ5w1l-1P-T2kkqvRtuGLdw8AaYrSpYDHUtGClaDYXnYqd3sJEwcLN6Ujx1Nn4aXAn1aprHdxrV9Jeixx-woJ17s67Lk5EwWN0QVJk8A75schKjOHi8h3YLPhWN7nrIJFfEPF_DaN7hHe0mAAPEFwiLQW19htTvEd0LCWGh8XKP9-d6g5mEVebe4ikRfegQG7hqMwfGwVftiocLAQLoJlFNGC-MIMNq-ClMBsqmUyvucLRjJJtKmCybls6TdGN_gQLlEjvmIgwIp-k9yzAe6W_uS72SunGkSVQuIZLdXUNKys8yqP3uWBtl_G6c"

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