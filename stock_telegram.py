import asyncio
import telegram

TOKEN = "7480981898:AAGPeGGhwoCwr0_sVilgCIfW7KNRIPsUaaQ"
chat_id = '-1002197644920'
# Channel ID Sample: -880066564

bot = telegram.Bot(token=TOKEN)

async def send_message(text, chat_id):
    await bot.send_message(text=text, chat_id=chat_id)

async def main():
    # Sending a message
    await send_message(text='Hi Sujit!, How are you?', chat_id=chat_id)

if __name__ == '__main__':
    asyncio.run(main())
