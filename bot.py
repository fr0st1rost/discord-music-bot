import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

queues = {}

ytdl = yt_dlp.YoutubeDL({
    'format': 'bestaudio/best',
    'quiet': True
})

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}


@bot.event
async def on_ready():
    print(f'Бот запущен как {bot.user}')


async def play_next(ctx):
    if queues.get(ctx.guild.id):
        url, title = queues[ctx.guild.id].pop(0)

        source = discord.FFmpegPCMAudio(url, **ffmpeg_options)

        ctx.voice_client.play(
            source,
            after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)
        )

        await ctx.send(f"🎵 Сейчас играет: **{title}**")


@bot.command()
async def play(ctx, *, query):

    if not ctx.author.voice:
        await ctx.send("❌ Зайди в голосовой канал")
        return

    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()

    info = ytdl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]

    url = info['url']
    title = info['title']

    if ctx.voice_client.is_playing():

        queues.setdefault(ctx.guild.id, []).append((url, title))

        await ctx.send(f"➕ Добавлено в очередь: **{title}**")

    else:

        source = discord.FFmpegPCMAudio(url, **ffmpeg_options)

        ctx.voice_client.play(
            source,
            after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)
        )

        await ctx.send(f"🎵 Сейчас играет: **{title}**")


@bot.command()
async def skip(ctx):

    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭ Пропущено")


@bot.command()
async def pause(ctx):

    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸ Пауза")


@bot.command()
async def resume(ctx):

    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶ Продолжаю")


@bot.command()
async def queue(ctx):

    if ctx.guild.id not in queues or len(queues[ctx.guild.id]) == 0:
        await ctx.send("📭 Очередь пустая")
        return

    message = "📜 Очередь:\n"

    for i, song in enumerate(queues[ctx.guild.id], start=1):
        message += f"{i}. {song[1]}\n"

    await ctx.send(message)


@bot.command()
async def leave(ctx):

    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Отключился")


bot.run(os.getenv("TOKEN"))