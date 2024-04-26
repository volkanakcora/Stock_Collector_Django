from django.conf import settings
import yfinance as yf
from datetime import date, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import io
from email.mime.image import MIMEImage

def get_stock_prices(startDate, endDate, ticker):
    # downloading the data of the ticker value between
    # the start and end dates
    resultData = yf.download(ticker, startDate, endDate)
    # Setting date as index
    resultData["Date"] = resultData.index
    # Giving column names
    resultData = resultData[["Open", "High", "Low", "Close", "Volume", "Date"]]
    resultData["ticker"] = ticker
    # Resetting the index values
    # resultData.reset_index(drop=True, inplace=True)
    # getting the first 5 rows of the data
    return resultData


def get_day_of_the_month():
    today = date.today()
    return today


def get_yesterday():
    today = get_day_of_the_month()
    # Yesterday date
    yesterday = today - timedelta(days=1)
    return yesterday


def send_email(self, message_to_you, receipt):

    # Create a message
    message = MIMEMultipart()
    message["From"] = settings.SENDER
    message["To"] = receipt
    message["Subject"] = "Analytics Report"

    # Convert the DataFrame to CSV as a string
    csv_content = message_to_you.to_csv(index=False)

    # Attach the CSV content to the email
    attachment = MIMEText(csv_content, _subtype="csv")
    attachment.add_header(
        "content-disposition", "attachment", filename="analytics_report.csv"
    )
    message.attach(attachment)

    # Connect to the SMTP server and send the email
    with smtplib.SMTP("108.177.15.109", 587) as server:
        server.starttls()
        server.login(settings.SENDER, settings.SENDER_PASSWORD)
        server.sendmail(settings.SENDER, receipt, message.as_bytes())

    print("Email sent successfully.")


def send_image(self, plt, receipt):
    # Save the figure as an image in memory (BytesIO)
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")  # You can use other formats like 'jpg' or 'pdf'
    buffer.seek(0)
    plt.close()

    # Create a message
    message = MIMEMultipart()
    message["From"] = settings.SENDER
    message["To"] = receipt
    message["Subject"] = "Stock Price Graphs"

    # Attach the graph image to the email
    image = MIMEImage(buffer.read(), _subtype="png")
    image.add_header(
        "Content-Disposition", "attachment", filename="stock_price_graphs.png"
    )
    message.attach(image)

    # Connect to the SMTP server and send the email
    with smtplib.SMTP("108.177.15.109", 587) as server:
        server.starttls()
        server.login(settings.SENDER, settings.SENDER_PASSWORD)
        server.sendmail(settings.SENDER, receipt, message.as_bytes())

    print("Email with stock price graphs sent successfully.")
