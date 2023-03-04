from mcstatus import JavaServer
from disnake.ext import commands
from datetime import datetime
import disnake

# Bot Data
server_title = "CSUF Minecraft World"
gabes_server = "172.88.97.100:25565"
token = ''
server_id = 1081056227158663258
ip = '172.88.97.100'
title_link = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
update_channel = 1081169737192583208
msg_cache = []

# Bot Dependencies 
command_sync_flags = commands.CommandSyncFlags.default()
command_sync_flags.sync_commands_debug = True
bot = commands.Bot(
    command_prefix='!',
    command_sync_flags=command_sync_flags,
    test_guilds=[server_id]
)
def getServer():
    return JavaServer.lookup("172.88.97.100:25565", timeout=6)
def writeId(msgid : int):
    with open('msg_chace.txt','a') as f:
        f.write(str(msgid) + '\n')
def createEmbed(version, player_count, ping, timestamp):
    return  {
      "type": "rich",
      "title": server_title,
      "description": "",
      "color": 0x3f8d2e,
      "fields": [
        {
          "name": "Server IP:",
          "value": ip
        },
        {
          "name": "Version:",
          "value": version
        },
        {
          "name": "Players:",
          "value": player_count
        },
        {
          "name": "Ping:",
          "value": f"Responded in {ping} ms"
        }
      ],
      "thumbnail": {
        "url": "https://pbs.twimg.com/media/FNda4prVkAIB9B7.png",
        "height": 400,
        "width": 400
      },
      "footer": {
        "text": f"Uploaded at {timestamp}"
      },
      "url": title_link
    }
def playerListEmbed(player_list, players_online, timestamp):
    players_str = ''
    for player in player_list:
        players_str += f'{player["name"]}\n'
    return {
      "type": "rich",
      "title": f"{server_title} - Player List",
      "description": "",
      "color": 0x3f8d2e,
      "fields": [
        {
          "name": f"🟢 Online - {players_online}",
          "value": "\u200B"
        },
        {
          "name": "Players:",
          "value": players_str
        }
      ],
      "thumbnail": {
        "url": "https://pbs.twimg.com/media/FNda4prVkAIB9B7.png",
        "height": 400,
        "width": 400
      },
      "footer": {
        "text": f"Posted {timestamp}"
      }
    }

# Bot commands
@bot.slash_command(description='Returns the status of the minecraft server')
async def status(inter, get_players: bool = commands.Param(default=False, choices=[True,False])):
    # Get Server
    server = getServer()
    status = server.status()
    # Generate status message
    embed = disnake.Embed.from_dict(createEmbed(status.raw["version"]["name"],str(status.raw['players']['online']) + '/' + str(status.raw['players']['max']),"{0:.3f}".format(status.latency),datetime.now().strftime("%I:%M %p")))
    channel = bot.get_channel(update_channel)
    # Send status message, store in cache
    messages = [(await channel.send(embed=embed)).id]
    # Check for player list embed, store in cache if necessary
    if get_players:
        if status.raw['players']['online'] > 0:
            player_list = status.raw["players"]["sample"]
            messages.append((await channel.send(embed=disnake.Embed.from_dict(playerListEmbed(player_list, str(status.raw['players']['online']) + '/' + str(status.raw['players']['max']), datetime.now().strftime("%I:%M %p"))))).id)
    # Clear old status messages
    with open('msg_cache.txt') as f:
        for line in f.readlines():
            prev_message = await channel.fetch_message(line[:-1])
            await prev_message.delete()
    # Cache new messages
    with open('msg_cache.txt', 'w') as f:
        for msgid in messages:
            f.write(str(msgid)+'\n')
    # Update user on status
    await inter.response.send_message(f'Done! Server status sent to <#{update_channel}>',ephemeral=True, delete_after=10)

@bot.event
async def on_ready():
    await bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.listening, name="/status commands!"))
    print("Bot is ready!")

# Most complicated part 
bot.run(token)
