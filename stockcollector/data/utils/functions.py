from django.conf import settings
import yfinance as yf
from datetime import date, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import io
from email.mime.image import MIMEImage
import requests
from io import BytesIO

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
    yesterday = today - timedelta(days=2)
    return yesterday

#Outdated, just keeping it here maybe we can use it another time again
def send_email(self, message_to_you, receipt):

    message = MIMEMultipart()
    message["From"] = settings.SENDER
    message["To"] = receipt
    message["Subject"] = "Analytics Report"

    csv_content = message_to_you.to_csv(index=False)

    attachment = MIMEText(csv_content, _subtype="csv")
    attachment.add_header(
        "content-disposition", "attachment", filename="analytics_report.csv"
    )
    message.attach(attachment)

    with smtplib.SMTP("108.177.15.109", 587) as server:
        server.starttls()
        server.login(settings.SENDER, settings.SENDER_PASSWORD)
        server.sendmail(settings.SENDER, receipt, message.as_bytes())

    print("Email sent successfully.")

#keeping here maybe we use it in the future, but it's outdated
def send_image(self, plt, receipt):
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")  
    buffer.seek(0)
    plt.close()

    message = MIMEMultipart()
    message["From"] = settings.SENDER
    message["To"] = receipt
    message["Subject"] = "Stock Price Graphs"

    image = MIMEImage(buffer.read(), _subtype="png")
    image.add_header(
        "Content-Disposition", "attachment", filename="stock_price_graphs.png"
    )
    message.attach(image)

    with smtplib.SMTP("108.177.15.109", 587) as server:
        server.starttls()
        server.login(settings.SENDER, settings.SENDER_PASSWORD)
        server.sendmail(settings.SENDER, receipt, message.as_bytes())

    print("Email with stock price graphs sent successfully.")


 

TOKEN = '7480981898:AAGPeGGhwoCwr0_sVilgCIfW7KNRIPsUaaQ'
CHAT_ID = '-1002197644920'

def send_message(message):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }
    response = requests.post(url, json=payload)
    return response.json()


def send_png(fig, caption=''):
    url = f'https://api.telegram.org/bot{TOKEN}/sendPhoto'

    buffer = BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)

    files = {
        'photo': ('plot.png', buffer, 'image/png')
    }

    payload = {
        'chat_id': CHAT_ID,
        'caption': caption
    }

    response = requests.post(url, params=payload, files=files)

    buffer.close()

    return response.json()


def send_csv(message_to_you, caption=''):
    url = f'https://api.telegram.org/bot{TOKEN}/sendDocument'

    # convert the DataFrame to CSv
    csv_content = message_to_you.to_csv(index=False)

    files = {
        'document': ('data.csv', csv_content.encode('utf-8'))
    }

    payload = {
        'chat_id': CHAT_ID,
        'caption': caption
    }

    response = requests.post(url, params=payload, files=files)
    return response.json()

