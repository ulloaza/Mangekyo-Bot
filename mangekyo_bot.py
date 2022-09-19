import os
import re
import discord
import requests
import traceback
import json
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# Notion stuff
notion_url = "https://api.notion.com/v1/pages"
database = os.getenv('DATABASE_TOKEN')
# Discord stuff
trig = '🦈'
disc_tok = os.getenv('DISCORD_TOKEN')
discName = os.getenv('USER')

# Env file template:
# # .env
# DATABASE_TOKEN=notion-db-token
# DISCORD_TOKEN=your-bot-token
# AUTH_KEY=notion-auth-token
# USER=your-username

# Notion Functions
def addEntry(url, title):
    data_to_be_written = {
        "parent": {
            "type": "database_id",
            "database_id": database
        },
        "properties": {
            "Name": {
                "title": [
                    { 
                        "type": "text", 
                        "text": 
                        {
                            "content": title
                        }
                    }
                ],
            },
            "URL": {
                "url": url
            },
        }
    }
    
    payload = json.dumps(data_to_be_written)
    print(payload)
    sendData(payload)


def sendData(payload):
    headers = {
        'Authorization': os.getenv('NOTION_AUTH_KEY'),
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", notion_url, headers=headers, data=payload)
    print(response.text)
    print(response.status_code)

# Init Bot
intents = discord.Intents.all()
intents.reactions = True
bot = commands.Bot(command_prefix='!', intents=intents)
@bot.event
async def on_ready():
    print(f'Mangekyo Sharingan activated!')

# Look for trigger reaction
@bot.event
async def on_reaction_add(reaction, user):
    if(str(reaction) == trig) and (str(user) == discName):

        # Get reply channelid
        reply = int(reaction.message.channel.id)
        if not reply:
            return
        channel = bot.get_channel(reply)
        
        # Check for SocialFeed vs regular message
        if (reaction.message.author.display_name == "SocialFeeds"):
            embed = reaction.message.embeds[0].to_dict()
            content = embed['url']
            if (re.match("twitter", content)):
                title = embed['description']
            else:
                title = embed['title']
            # Chop and fix socialfeed's urls
            url = re.sub("^https\:\/\/go-sf\.app\/\w+\/go\/", 'https://', content)
            url = re.sub("\?guild_id=\d+\&\#", '', url)
            
            # Send response then post to notion
            await channel.send('👈🤘🫰 Sharingan Copy Wheel! 👈🤘🫰\n\t\t\t\tCopied your jutsu to Notion!')
            try:
                addEntry(url, title)
            except:
                traceback.print_exc()
                await channel.send('Error sending entry to Notion!')
        # Look for 
        elif (reaction.message.embeds):
            content = reaction.message.content
            embed = reaction.message.embeds[0].to_dict()
            url = embed['url']
            title = content.split(" https")[0]

            # Send response then post to notion
            await channel.send('👈🤘🫰 Sharingan Copy Wheel! 👈🤘🫰\n\t\t\t\tCopied your jutsu to Notion!')
            try:
                addEntry(url, title)
            except:
                traceback.print_exc()
                await channel.send('Error sending entry to Notion!')
        else:
            reply = int(reaction.message.channel.id)
            if not reply:
                return
            channel = bot.get_channel(reply)
            await channel.send('Cannot upload this type of content :(')

bot.run(disc_tok)
