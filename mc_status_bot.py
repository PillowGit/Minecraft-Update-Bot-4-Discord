from mcstatus import JavaServer
from disnake.ext import commands
from datetime import datetime
import disnake

# Bot Data
server_title = "CSUF Minecraft World"
gabes_server = "172.88.97.100:25565"
token = ''
guild_id = 1081056227158663258
title_link = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
update_channel = 1081169737192583208
owner_id = 407963398207176715
admin_roles = [1081060733804085258]
log_file = 'msg_cache.txt'
ip = '172.88.97.100'

# Bot Dependencies 
presence = disnake.Game(name='/status & /servermap')
command_sync_flags = commands.CommandSyncFlags.default()
command_sync_flags.sync_commands_debug = True
bot = commands.Bot(command_prefix=disnake.ext.commands.when_mentioned, command_sync_flags=command_sync_flags, test_guilds=[guild_id], activity=presence)
def getServer():
    return JavaServer.lookup("172.88.97.100:25565", timeout=6)
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

# Retrieve minecraft status
@bot.slash_command(description='Returns the status of the minecraft server!')
async def status(inter, get_players: bool = commands.Param(default=False, choices=[True,False])):
    succesful = True
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
        if str(status.raw['players']['online']) != '0':
            player_list = status.raw["players"]["sample"]
            messages.append((await channel.send(embed=disnake.Embed.from_dict(playerListEmbed(player_list, str(status.raw['players']['online']) + '/' + str(status.raw['players']['max']), datetime.now().strftime("%I:%M %p"))))).id)
    # Clear old status messages
    with open(log_file) as f:
        try:
            for line in f.readlines():
                prev_message = await channel.fetch_message(line[:-1])
                await prev_message.delete()
        except disnake.errors.NotFound:
            succesful = False
            await inter.response.send_message(f'<@{owner_id}> bot has detected log file corruption -> Error type data loss')
        except disnake.errors.HTTPException:
            succesful = False
            await inter.response.send_message(f'<@{owner_id}> bot has detected log file corruption -> Error type snowflake')
    # Cache new messages
    if succesful:
        with open(log_file, 'w') as f:
            for msgid in messages:
                f.write(str(msgid)+'\n')
        # Update user on status
        await inter.response.send_message(f'Done! Server status sent to <#{update_channel}>\n\n*this message self destructs in 10 seconds*',ephemeral=True, delete_after=10)

# Link to dynamic map
@bot.slash_command(description='Get a link to a 3D map of our minecraft world!')
async def servermap(inter):
    await inter.response.send_message(f'Here\'s a link to our dynamic map! Powered by dynmap\n{title_link}\n*This message will __not__ self destruct*', ephemeral=True)

# Remote corruption clearing
@bot.slash_command(description='(Admin only) Cleans cache')
async def clean(inter):
    search_result = [(int(x.id) in admin_roles) for x in inter.author.roles]
    if any(search_result):
        open(log_file, 'w').close()
        await inter.response.send_message('Cache cleared ✅', ephemeral=True, delete_after=10)
    else:
        await inter.response.send_message('You do not have permission to use this command', ephemeral=True, delete_after=6)

# Returns internal cache
@bot.slash_command(description='(Admin only) Returns important data')
async def seecache(inter):
    search_result = [(int(x.id) in admin_roles) for x in inter.author.roles]
    if any(search_result):
        with open(log_file) as f:
            cache = f.read()
            result = 'Cache is empty' if cache is None or cache is '' else f'```{cache}```'
            await inter.response.send_message(result, ephemeral=True)
    else:
        await inter.response.send_message('You do not have permission to use this command', ephemeral=True, delete_after=6)

# Adds a message id to the cache
@bot.slash_command(description='(Admin only) Manually insert ids to cache')
async def insert(inter, ids: str):
    search_result = [(int(x.id) in admin_roles) for x in inter.author.roles]
    if any(search_result):
        with open(log_file, 'a') as f:
            data = ids.split(' ')
            for entry in data:
                f.write(str(entry)+'\n')
            await inter.response.send_message(f'Added the following data to the cache:\n{data}', ephemeral=True)
    else:
        await inter.response.send_message('You do not have permission to use this command', ephemeral=True, delete_after=6)

@bot.event
async def on_ready():
    print("Bot is ready!")

# Most complicated part 
bot.run(token)
