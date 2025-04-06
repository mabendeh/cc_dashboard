
import pandas as pd
import numpy as np
from datetime import datetime
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import smtplib
from email.message import EmailMessage
import os

# Simulate your data
dates = pd.date_range(start='2025-03-01', end='2025-03-31', freq='D')
data = {
    'Date': np.tile(dates, 3),
    'Shift': np.repeat(['Shift 1', 'Shift 2', 'Shift 3'], len(dates)),
    'Output': np.random.randint(800, 1200, len(dates)*3),
    'Scrap': np.random.randint(20, 50, len(dates)*3),
    'FPY': np.random.uniform(0.85, 0.99, len(dates)*3),
    'OEE': np.random.uniform(0.65, 0.9, len(dates)*3),
    'Defect Type': np.random.choice(['Weld Fail', 'Crack', 'Missing Tab', 'Bent Pin'], len(dates)*3)
}
df = pd.DataFrame(data)
df['Date'] = pd.to_datetime(df['Date'])

# Filter by today's date
today = pd.to_datetime(datetime.today().date())
df_today = df[df['Date'] == today]
if df_today.empty:
    df_today = df[df['Date'] == df['Date'].max()]

# Generate KPIs
total_output = df_today['Output'].sum()
total_scrap = df_today['Scrap'].sum()
avg_fpy = df_today['FPY'].mean()
avg_oee = df_today['OEE'].mean()
defect_top = df_today['Defect Type'].value_counts().idxmax()

# Generate AI insights
summary = []
if avg_fpy < 0.9:
    summary.append("FPY dropped below 90%. Investigate welding.")
if avg_oee < 0.75:
    summary.append("OEE is below optimal. Check for downtime causes.")
if total_scrap > 300:
    summary.append(f"High scrap detected. Top defect: {defect_top}.")
if not summary:
    summary.append("All KPIs are within healthy range.")

# Generate PDF
buffer = BytesIO()
pdf = canvas.Canvas(buffer, pagesize=letter)
pdf.setTitle("CC Line Auto Report")

pdf.setFont("Helvetica-Bold", 14)
pdf.drawString(1 * inch, 10.5 * inch, f"CC Line Daily Report - {today.strftime('%Y-%m-%d')}")
pdf.setFont("Helvetica", 10)
pdf.drawString(1 * inch, 10.1 * inch, f"Total Output: {total_output:,}")
pdf.drawString(1 * inch, 9.9 * inch, f"Scrap Rate: {(total_scrap / total_output):.2%}")
pdf.drawString(1 * inch, 9.7 * inch, f"Average FPY: {avg_fpy:.2%}")
pdf.drawString(1 * inch, 9.5 * inch, f"Average OEE: {avg_oee:.2%}")

pdf.setFont("Helvetica-Bold", 12)
pdf.drawString(1 * inch, 9.2 * inch, "AI Insights:")
pdf.setFont("Helvetica", 10)
y = 9.0 * inch
for line in summary:
    pdf.drawString(1 * inch, y, line)
    y -= 0.2 * inch

pdf.save()
buffer.seek(0)

# Send Email
def send_email():
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    recipient = os.getenv("EMAIL_TO")

    msg = EmailMessage()
    msg['Subject'] = f"CC Line Daily Report - {today.strftime('%Y-%m-%d')}"
    msg['From'] = sender
    msg['To'] = recipient
    msg.set_content("Attached is the automated CC Line daily performance report.")

    msg.add_attachment(buffer.read(), maintype='application', subtype='pdf', filename='cc_line_report.pdf')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)

if __name__ == "__main__":
    send_email()
    print("✅ Email with PDF report sent.")
