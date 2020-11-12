# bot.py
import os
import discord
import requests
import shutil

from discord.ext import commands, tasks
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
ids = [] # include CHANNEL IDs here

bot = commands.Bot("!")
client = discord.Client()

async def fetch_apod():
    print('fetching apod')
    apod_url = 'https://apod.nasa.gov/apod/'
    apod_html = requests.get(apod_url).text
    soup = BeautifulSoup(apod_html, 'html.parser')
    images = soup.findAll('img')
    for image in images:
        response = requests.get(apod_url + image['src'])
        if response.status_code == 200:
            with open('apod.png', 'wb') as f:
                f.write(response.content)

    b = soup.findAll('b')
    a = soup.findAll('a')
    
    important_info = []
    important_info.append(f'**{b[0].text.strip()}** \n')
    important_info.append(f'{apod_url} \n')
    
    return ''.join(important_info)

@tasks.loop(hours=24)
async def called_once_a_day():
    info = await fetch_apod()
    for id in ids:
        channel = bot.get_channel(id=id)
        await channel.send(info, file=discord.File('apod.png'))

@called_once_a_day.before_loop
async def before():
    await bot.wait_until_ready()

called_once_a_day.start()
bot.run(TOKEN)
