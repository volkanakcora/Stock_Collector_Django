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
import matplotlib.pyplot as plt
import logging

def get_stock_prices(startDate, endDate, ticker):

    resultData = yf.download(ticker, startDate, endDate)
    resultData["Date"] = resultData.index
    resultData = resultData[["Open", "High", "Low", "Close", "Volume", "Date"]]
    resultData["ticker"] = ticker

    return resultData


def get_day_of_the_month():
    today = date.today()
    return today


def get_yesterday():
    today = get_day_of_the_month()
    yesterday = today - timedelta(days=2)
    return yesterday

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

def send_png_tg(fig, caption=''):
    try:
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
        response.raise_for_status()
        logging.info('Image sent to Telegram successfully.')
        
        return response.json()

    except requests.exceptions.RequestException as e:
        logging.error(f'Request error: {e}')
    except Exception as e:
        logging.error(f'Error sending image to Telegram: {e}')

    return None


def send_csv(message_to_you, caption=''):
    url = f'https://api.telegram.org/bot{TOKEN}/sendDocument'

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

