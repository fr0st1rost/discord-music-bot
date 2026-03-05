import discord
from discord.ext import commands
import yt_dlp
import asyncio

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

queues = {}

ytdl = yt_dlp.YoutubeDL({
    'format': 'bestaudio/best',
    'quiet': True
})

ffmpeg_options = {
    'options': '-vn'
}


@bot.event
async def on_ready():
    print(f'Бот запущен как {bot.user}')


async def play_next(ctx):
    if queues.get(ctx.guild.id):
        url = queues[ctx.guild.id].pop(0)

        source = await discord.FFmpegOpusAudio.from_probe(url, **ffmpeg_options)
        ctx.voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))


@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()


@bot.command()
async def play(ctx, *, query):

    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()

    info = ytdl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
    url = info['url']
    title = info['title']

    if ctx.voice_client.is_playing():
        queues.setdefault(ctx.guild.id, []).append(url)
        await ctx.send(f"Добавлено в очередь: {title}")
    else:
        source = await discord.FFmpegOpusAudio.from_probe(url, **ffmpeg_options)
        ctx.voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))
        await ctx.send(f"Сейчас играет: {title}")


@bot.command()
async def skip(ctx):
    ctx.voice_client.stop()


@bot.command()
async def pause(ctx):
    ctx.voice_client.pause()


@bot.command()
async def resume(ctx):
    ctx.voice_client.resume()


@bot.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()


import os
bot.run(os.getenv("TOKEN"))