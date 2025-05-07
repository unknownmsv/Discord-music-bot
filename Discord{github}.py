import discord
from discord.ext import commands
import os, yt_dlp, asyncio, openai, requests, json, time
from collections import defaultdict

# ----- Setup -----
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

DEVS = []
TOKEN = ''  # Bot Token

#----- varibale ------
user_timers = {}
#---- bot code -----
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


# ----- Developer Commands -----

@bot.command()
async def dev_send(ctx, *, msg):
    if ctx.author.id not in DEVS:
        await ctx.send("اجازه نداری.")
        return
    channel = discord.utils.get(ctx.guild.channels, name="server-news")
    if channel:
        await channel.send(msg)
        await ctx.send("فرستاده شد.")
    else:
        await ctx.send("چنل پیدا نشد.")

# ----- Music Commands -----
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
        await ctx.send("وصل شدم به چنل صوتی.")
    else:
        await ctx.send("اول وارد چنل صوتی شو.")

@bot.command()
async def play(ctx, url: str):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice:
        await ctx.send("اول با `!join` وارد چنل شو.")
        return

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'song.%(ext)s',
        'quiet': True,
    }

    await ctx.send("در حال دانلود...")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    for file in os.listdir("./"):
        if file.endswith((".mp3", ".m4a", ".webm")):
            os.rename(file, "song.mp3")
            break

    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: print("تموم شد."))
    await ctx.send("در حال پخش...")

@bot.command()
async def leave(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.disconnect()
        await ctx.send("خارج شدم.")
    else:
        await ctx.send("وصل نیستم.")

# ----- OpenAI GPT Command -----
@bot.command()
async def chat(ctx, *, prompt):
    try:
        openai.api_key = OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        reply = response['choices'][0]['message']['content']
        await ctx.send(reply)
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")
# -----Alarm Command-----
@bot.command()
async def alarm(ctx, time: int):
    user_id = ctx.author.id

    if user_id in user_timers:
        await ctx.send("⛔ شما در حال حاضر یک تایمر فعال دارید.")
        return

    user_timers[user_id] = True
    seconds = time * 60
    await ctx.send(f"⏳ تایمر {time} دقیقه‌ای برای شما شروع شد...")

    await asyncio.sleep(seconds)

    await ctx.send(f"⏰ {ctx.author.mention} تایمر شما تموم شد!")
    del user_timers[user_id]
#----- super alarm ------
@bot.command()
async def superAlarm(ctx, STimer: int):
  global Alarm
  user_id = ctx.author.id
  Alarm = True
  if Alarm == True:
    if user_id in user_timers:
      await ctx.send("⛔ شما در حال حاضر یک تایمر فعال دارید.")
      return
    
    seconds = STimer * 60
    await asyncio.sleep(seconds)
    supertimer = 0
    while supertimer < 5:
      await ctx.send(f"⏰ {ctx.author.mention} تایمر شما تموم شد!")
      supertimer += 1
      await asyncio.sleep(1)  # فاصله بین پیام‌ها تا اسپم نشه


# ----- Help Command -----
@bot.command()
async def helpme(ctx):
    await ctx.send(
        "**Public Commands:**\n"
        "`!join` – Join voice\n"
        "`!play <YouTube URL>` – Play\n"
        "`!leave` – Leave voice\n"
        "**Dev Commands:**\n"
        "`!dev_send <message>` – Send to #server-news"
    )

# ----- Run -----
bot.run(TOKEN)