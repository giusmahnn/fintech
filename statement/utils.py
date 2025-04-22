from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from decimal import Decimal


def generate_pdf_statement(account, transactions, start_date, end_date):
    response = HttpResponse(content_type='application/pdf')
    filename = f"{account.user.get_full_name().replace(' ', '_')}_statement.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'


    pdf = canvas.Canvas(response, pagesize=letter)
    pdf.setTitle(f"Account Statement - {account.account_number}")

    # Header
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, 770, "Account Statement")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, 755, f"Account Number: {account.account_number}")
    pdf.drawString(50, 740, f"Account Holder: {account.user.get_full_name()}")
    pdf.drawString(50, 725, f"Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    pdf.drawString(50, 710, f"Currency: {account.currency}")
    
    # Table Headers
    pdf.setFont("Helvetica-Bold", 9)
    headers = ["Date", "Type", "Flow", "Amount", "Narration"]
    x_positions = [50, 120, 200, 270, 340]
    for i, h in enumerate(headers):
        pdf.drawString(x_positions[i], 690, h)

    y = 670
    pdf.setFont("Helvetica", 9)
    for txn in transactions:
        pdf.drawString(x_positions[0], y, txn.date.strftime('%Y-%m-%d'))
        pdf.drawString(x_positions[1], y, txn.transaction_type.capitalize())
        pdf.drawString(x_positions[2], y, txn.transaction_flow.capitalize())
        pdf.drawString(x_positions[3], y, f"{Decimal(txn.amount):,.2f}")
        pdf.drawString(x_positions[4], y, txn.narration[:40] if txn.narration else "-")
        y -= 15
        if y < 50:
            pdf.showPage()
            y = 750

    pdf.save()
    return response