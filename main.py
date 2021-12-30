#   Import libraries
import os
import re
import random
import discord
import youtube_dl
import urllib.request
from dotenv import load_dotenv
from discord.ext import commands

#   YouTube stuff
youtube_search_url = "https://www.youtube.com/results?search_query="
youtube_song_url = "https://www.youtube.com/watch?v="

ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'song.mp3',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

#   Search for and download a song
def download(query):
    html = urllib.request.urlopen(youtube_search_url + query.replace(" ","+"))
    ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    url = youtube_song_url + ids[0]
    print(url)
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            os.remove("song.mp3")
        except:
            pass
        song = ydl.extract_info(url, download=True)
        return song['title']    

#   Get a random roast from file `roasts.txt`
def random_roast():
    return random.choice(list(open('roasts.txt')))

#   Load token from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#   Create the bot
bot = commands.Bot(command_prefix='sudo ', case_insensitive=True)

#   Ready message
@bot.event
async def on_ready():
    print("Bot is online.")

#   Kick command
@bot.command()
@commands.has_permissions(kick_members=True)    #   Check if user has `kick_members` permission 
async def kick(ctx, member: discord.Member, *, reason=None):
    if reason == None:
        reason = "No reason given."
    await member.send(f"You have been kicked from {ctx.guild}.\nReason: ``{reason}``")  #   Send a DM to the user that is being kicked
    await member.kick(reason=reason)    #   Kick that little piece of shit

#   Ban command
@bot.command()
@commands.has_permissions(ban_members=True)    #   Check if user has `ban_members` permission 
async def ban(ctx, member: discord.Member, *, reason=None):
    if reason == None:
        reason = "No reason given."
    await member.send(f"You have been banned from {ctx.guild}.\nReason: ``{reason}``")  #   Send a DM to the user that is being banned
    await member.ban(reason=reason)    #   Ban that little piece of shit

#   Play command, still work in progress
@bot.command()
async def play(ctx, *, query):
    try:
        print(str(query))
        channel = ctx.author.voice.channel
        try:
            await channel.connect()
        except:
            pass
        guild = ctx.guild
        voice_client: discord.VoiceClient = discord.utils.get(bot.voice_clients, guild=guild)
        song = download(query=query)
        audio_source = discord.FFmpegPCMAudio(source="song.mp3")
        await ctx.send(f"``Playing: {song}``")
        if not voice_client.is_playing():
            voice_client.play(audio_source, after=None)
    except Exception as e:
        print(e)

#   Roast command
@bot.command()
async def roast(ctx, member: discord.Member):
    if not member.bot:
        await ctx.send(f"{member.mention} {random_roast()}")
    else:
        await ctx.send(f"{ctx.author.mention} How dare you? ")

#   Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):  #   Missing Permissions error
        await ctx.send(f"``{ctx.author.name} is not in the sudoers file. This incident will be reported.``")    #   Publicly announce that that user tried to do something they shouldn't (very naughty)...

if __name__ == "__main__":
    bot.run(TOKEN)  #   Run the bot I guess?
