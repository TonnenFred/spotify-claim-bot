import discord
from discord.ext import commands
import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

# --- Setup ---
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

# Spotify API Setup
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

# In-Memory Database (for dev/testing)
user_collections = {}

# --- Funktionen ---
def get_random_artist():
    random_letter = random.choice("abcdefghijklmnopqrstuvwxyz")
    results = sp.search(q=f"artist:{random_letter}", type="artist", limit=50)
    if results['artists']['items']:
        return random.choice(results['artists']['items'])
    return None

# --- Discord Commands ---
@bot.command()
async def claim(ctx):
    artist = get_random_artist()
    if artist:
        name = artist['name']
        url = artist['external_urls']['spotify']
        user_id = str(ctx.author.id)

        user_collections.setdefault(user_id, []).append(name)

        await ctx.send(f"{ctx.author.mention} hat **{name}** geclaimt!\n🎧 {url}")
    else:
        await ctx.send("Kein Artist gefunden. Versuche es erneut.")

@bot.command()
async def mycollection(ctx):
    user_id = str(ctx.author.id)
    collection = user_collections.get(user_id, [])
    if collection:
        await ctx.send(f"🎶 Deine Sammlung:\n" + "\n".join(f"- {artist}" for artist in collection))
    else:
        await ctx.send("Du hast noch keine Artists geclaimt.")

# --- Main ---
if __name__ == "__main__":
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    if not DISCORD_TOKEN or not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        print("❌ Bitte setze die Umgebungsvariablen: DISCORD_TOKEN, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET")
    else:
        bot.run(DISCORD_TOKEN)
