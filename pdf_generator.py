from db import connect_db
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle
import os

pdfmetrics.registerFont(TTFont("NotoSans", "fonts/NotoSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("NotoSans-Bold", "fonts/NotoSans-Bold.ttf"))

def generate_pdf(invoice_id, filename, paid=True):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.name, c.email, c.phone, c.address, i.date
        FROM invoice i
        JOIN customer c ON i.customer_id = c.id
        WHERE i.id = ?
    """, (invoice_id,))
    result = cursor.fetchone()

    if not result:
        raise ValueError(f"No invoice found with ID {invoice_id}")

    name, email, phone, address, invoice_date = result

    cursor.execute("""
        SELECT code, unit, quantity, price
        FROM invoice_item
        WHERE invoice_id = ?
    """, (invoice_id,))
    items = cursor.fetchall()

    if not os.path.exists("invoices"):
        os.makedirs("invoices")
    filepath = os.path.join("invoices", filename)

    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    margin = 40
    y = height - 40

    # Header: Company and Invoice Info
    if os.path.exists("images/company_logo.png"):
        c.drawImage("images/company_logo.png", margin, y - 50, width=120, preserveAspectRatio=True)
    c.setFont("NotoSans-Bold", 24)
    c.drawString(margin + 150, y - 20, "INVOICE")

    c.setFont("NotoSans", 10)
    c.drawString(margin + 150, y - 40, f"Invoice Number: #{invoice_id}")
    c.drawString(margin + 150, y - 55, f"Invoice Date: {invoice_date.strftime('%d/%m/%Y')}")

    y -= 90

    # FROM / TO Sections
    c.setFont("NotoSans-Bold", 11)
    c.drawString(margin, y, "FROM")
    c.drawString(width / 2, y, "TO")
    c.setFont("NotoSans", 10)
    c.drawString(margin, y - 15, "Your Company Name")
    c.drawString(margin, y - 30, "Your Company Address Line")
    c.drawString(margin, y - 45, "Phone: 123-456-7890")

    c.drawString(width / 2, y - 15, name)
    c.drawString(width / 2, y - 30, address)
    c.drawString(width / 2, y - 45, f"Phone: {phone}")

    y -= 80

    # Items Table
    data = [["Item", "Unit", "Qty", "Price (₹)", "Total (₹)"]]
    total_amount = 0
    for code, unit, qty, price in items:
        line_total = qty * price
        total_amount += line_total
        data.append([
            str(code), str(unit), str(qty),
            f"{price:.2f}", f"{line_total:.2f}"
        ])

    table = Table(data, colWidths=[100, 60, 40, 80, 80])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'NotoSans-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('BOX', (0, 0), (-1, -1), 0.3, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.3, colors.black),
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT')
    ]))
    table.wrapOn(c, width, height)
    table_height = 20 * len(data)
    table.drawOn(c, margin, y - table_height)

    y -= (table_height + 40)

    # Grand Total
    c.setFont("NotoSans-Bold", 12)
    c.drawString(width - 200, y, "Grand Total:")
    c.drawString(width - 100, y, f"₹{total_amount:.2f}")
    y -= 30

    # Payment QR
    if os.path.exists("images/upi_qr.png"):
        c.drawImage("images/upi_qr.png", margin, y - 100, width=100, height=100)

    # Paid/Unpaid stamp beside QR
    stamp_path = "images/paid_stamp.png" if paid else "images/unpaid_stamp.png"
    if os.path.exists(stamp_path):
        c.drawImage(stamp_path, margin + 120, y - 90, width=80, preserveAspectRatio=True)

    # Signature
    if os.path.exists("images/signature.png"):
        c.drawImage("images/signature.png", width - 160, y - 90, width=100, preserveAspectRatio=True)
        c.setFont("NotoSans", 9)
        c.drawString(width - 160, y - 105, "images/Authorized Signatory")

    c.save()
    return filepath
