import discord
from discord.ext import commands
import random as rand
from os import environ
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix='.', intents=intents)

load_dotenv()

@client.event
async def on_ready():
    print('Logged on!')
    game = environ["GAME_ACTIVITY"]
    await client.change_presence(activity=discord.Game(name=game))

#Help Command
@client.slash_command(name = "help", description = "See all commands.")
async def help(ctx):
    embed=discord.Embed(title="NBBot Help", description="Here are all the commands for NBBot.", color=discord.Color.blue())
    embed.add_field(name="NBGames Content", value="game: Get information about a game by NBGames.", inline=False)
    embed.add_field(name="Administration", value="ban: Bans a member.\nkick: Kicks a member.\nmute: Mutes a member.\nunmute: Unmutes a member\npurge: Clears an amount of messages in the channel.", inline=False)
    embed.add_field(name="Other", value="help: See all commands.\nmemberinfo: Gets info about a member.\nping: Get latency.\nrandom: Picks between 2 numbers.", inline=False)
    await ctx.respond(embed=embed)

#Ping Command
@client.slash_command(name = "ping", description = "Get latency.")
async def ping(ctx):
    await ctx.respond(f"{ctx.author.mention}, pong! Latency is {client.latency}")

#Ban Command
@client.slash_command(name = "ban", description = "Ban a member.")
async def ban(ctx, member: discord.Member, reason = None):
    #Checks if the author has permission to ban members.
    if ctx.author.guild_permissions.ban_members:
        await member.ban(reason=reason)
        await ctx.respond(f"{ctx.author.mention}, banned @{member.mention} successfully for {reason}.", delete_after=3)
    else:
        #Throws error if author doesn't have permission.
        await ctx.respond(f"{ctx.author.mention}, you don't have permission to use this command.", delete_after=3)

#Kick Command
@client.slash_command(name = "kick", description = "Kick a member.")
async def kick(ctx, member: discord.Member, reason = None):
    #Checks if the author has permission to kick members.
    if ctx.author.guild_permissions.kick_members:
        await member.kick(reason=reason)
        await ctx.respond(f"{ctx.author.mention}, kicked @{member.mention} successfully for {reason}.", delete_after=3)
    else:
        #Throws error if author doesn't have permission.
        await ctx.respond(f"{ctx.author.mention}, you don't have permission to use this command.", delete_after=3)

#Mute Command
@client.slash_command(name="mute", description = "Mute a member.")
async def mute(ctx, member: discord.Member, reason = None):
    #Checks if the author has permission to mute members.
    if ctx.author.guild_permissions.manage_roles:
        #Checks the mentioned user for the ability to send messages.
        if ctx.channel.permissions_for(member).send_messages:
            await ctx.channel.set_permissions(member, send_messages=False)
            await ctx.respond(f"{ctx.author.mention}, muted {member.mention} successfully for {reason}.", delete_after=3)
        else:
            #Sends error message if the user is already muted/can't send messages.
            await ctx.respond(f"{ctx.author.mention}, {member.mention} is already muted.", delete_after=3)
    else:
        #Throws error if author doesn't have permission.
        await ctx.respond(f"{ctx.author.mention}, you don't have permission to use this command.", delete_after=3)

#Unmute Command
@client.slash_command(name="unmute", description = "Unmute a member.")
async def mute(ctx, member: discord.Member):
    #Checks if the author has permission to mute members.
    if ctx.author.guild_permissions.manage_roles:
        #Checks the mentioned user for the ability to send messages.
        if not ctx.channel.permissions_for(member).send_messages:
            await ctx.channel.set_permissions(member, send_messages=True)
            await ctx.respond(f"{ctx.author.mention}, unmuted {member.mention} successfully.", delete_after=3)
        else:
            #Sends error message if the user isn't muted/can send messages.
            await ctx.respond(f"{ctx.author.mention}, {member.mention} isn't muted.", delete_after=3)
    else:
        #Throws error if author doesn't have permission.
        await ctx.respond(f"{ctx.author.mention}, you don't have permission to use this command.", delete_after=3)

#Purge Command
@client.slash_command(name = "purge", description="Purge the messages of a channel.")
async def purge(ctx, number):
    if ctx.author.guild_permissions.manage_messages:
        #Convert the value number to an actual int
        try:
            number = int(number)
        except ValueError:
            await ctx.respond(f'{ctx.author.mention}, enter a valid number.', delete_after=3)
        await ctx.channel.purge(limit=number)
        await ctx.respond(f'{ctx.author.mention}, successfully cleared ' + str(number) + ' messages.', delete_after=3)
    else:
        #Throws error if author doesn't have permission.
        await ctx.respond(f"{ctx.author.mention}, you don't have permission to use this command.", delete_after=3)

#Random Command
@client.slash_command(name="random", description="Choose between 2 random numbers.")
async def random(ctx, number1, number2):
    #Try to use the two numbers and see if they can be used as an int
    try:
        #Respond to the user with a chosen number between number1 and number2 using the random module.
        await ctx.respond(f"{ctx.author.mention}, between {number1} and {number2}, I choose " + str(rand.randrange(int(number1), int(number2))) + ".")
    except ValueError:
        #Returns an error if one or both of the numbers are invalid.
        await ctx.respond(f'{ctx.author.mention}, please enter 2 valid numbers.', delete_after=3)

#Game Command
@client.slash_command(name="game", description="Get info on a game made by NBGames.")
async def game(ctx, gamename):
    #Create embed
    embed=discord.Embed(title="", color=discord.Color.blue())
    if gamename == "JumpHouse: Moving Again" or gamename == "JumpHouse Moving Again" or gamename == "JumpHouse 2" or gamename == "jumphouse moving again" or gamename == "jumphouse 2":
        embed.title = "*JumpHouse: Moving Again*"
        embed.add_field(name="About", value="Collect boxes and move to houses!", inline=False)
        embed.add_field(name="Release Date", value="2023", inline=False)
        embed.add_field(name="More Info", value="Check out more [here](https://nb-dev.wixsite.com/nbgames/jumphouse-moving-again)", inline=False)
        embed.set_thumbnail(url="https://static.wixstatic.com/media/0b14ca_1d259fc34e7e4d4fb4718d3be6318db4~mv2.png/v1/fill/w_233,h_233,al_c,q_95,enc_auto/jh2-splash2.png")
    if gamename == "Rolling" or gamename == "rolling":
        embed.title = "*Rolling*"
        embed.add_field(name="About", value="Roll through obstacle courses.", inline=False)
        embed.add_field(name="Release Date", value="February 28, 2022", inline=False)
        embed.add_field(name="More Info", value="Check out more [here](https://nb-dev.wixsite.com/nbgames/rolling)\nDownload the latest version [here](https://nb064.itch.io/rolling)", inline=False)
        embed.set_thumbnail(url="https://static.wixstatic.com/media/0b14ca_f4407379470c45098b444b680e6aac5e~mv2.png/v1/fill/w_233,h_233,al_c,q_95,enc_auto/DefaultBall.png")
    if gamename == "God Clickers" or gamename == "god clickers":
        embed.title = "*God Clickers*"
        embed.add_field(name="About", value="Click Away!", inline=False)
        embed.add_field(name="Release Date", value="June 23, 2021", inline=False)
        embed.add_field(name="More Info", value="Check out more [here](https://nb-dev.wixsite.com/nbgames/god-clickers)\nDownload the latest version [here](https://nb064.itch.io/god-clickers)", inline=False)
        embed.set_thumbnail(url="https://static.wixstatic.com/media/0b14ca_06006dccd763477caa95cd181dab8b06~mv2.png/v1/fill/w_233,h_233,al_c,q_95,enc_auto/icon.png")
    await ctx.respond(embed=embed)

#Userinfo Command
@client.slash_command(name="memberinfo", description="Get info about a member.")
async def userinfo(ctx, member: discord.Member):
    embed=discord.Embed(title=f'{member}', description=f'{member.id}', color=discord.Color.blue())
    embed.add_field(name="Registered On", value=f'{member.created_at}', inline=True)
    embed.add_field(name="Joined On", value=f'{member.joined_at}', inline=True)
    embed.set_thumbnail(url=member.display_avatar)
    await ctx.respond(embed=embed)

token = environ["TOKEN"]
client.run(token)