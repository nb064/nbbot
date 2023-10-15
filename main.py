import discord, random as rand, os, asyncio, json
from discord.ext import commands
from os import environ
from dotenv import load_dotenv
from utilities import translate

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix='.', intents=intents)

sendWelcome = True

load_dotenv()

with open("resources/games.json", "r") as gamesRes:
    games = json.load(gamesRes)

#Starting up the bot
@client.event
async def on_ready():
    print('Logged on!')
    game = environ["GAME_ACTIVITY"]
    await client.change_presence(activity=discord.Game(name=game))

#Welcome message
@client.event
async def on_member_join(member):
    if sendWelcome:
        welcomeChannelName = environ["WELCOMECHANNEL"]
        rulesChannel = environ["RULESCHANNEL"]
        welcomeChannel = discord.utils.get(member.guild.channels, name=welcomeChannelName)
        await welcomeChannel.send(f"Hello, {member.mention}! Welcome to {member.guild.name}. Please be sure to read <#{rulesChannel}> before you start chatting!")

#Help Command
@client.slash_command(name = "help", description = "See all commands.")
async def help(ctx):
    embed=discord.Embed(title="NBBot Help", description="Here are all the commands for NBBot.", color=discord.Color.blue())
    embed.add_field(name="NBGames Content", value="game: Get information about a game by NBGames.\nplay: Play music from NBGames games!", inline=False)
    embed.add_field(name="Administration", value="ban: Bans a member.\nkick: Kicks a member.\nmute: Mutes a member.\nunmute: Unmutes a member\npurge: Clears an amount of messages in the channel.\nsend: I will send something!", inline=False)
    embed.add_field(name="Fun", value="8ball: Get an answer from the 8 Ball!\ncoinflip: Flip a coin!\njoke: I'll tell you a joke!\ntranslate: Translate a message!")
    embed.add_field(name="Math", value="add: Get the sum of two numbers.\nsubtract: Get the difference of two numbers.\nmultiply: Get the product of two numbers.\ndivide: Get the quotient of two numbers.")
    embed.add_field(name="Other", value="help: See all commands.\nmemberinfo: Gets info about a member.\nping: Get latency.\nrandom: Picks between 2 numbers.\nrepeat: I will repeat something!\nserverinfo: Get info about the server.", inline=False)
    await ctx.respond(embed=embed)

#Ping Command
@client.slash_command(name = "ping", description = "Get latency.")
async def ping(ctx):
    await ctx.respond(f"{ctx.author.mention}, pong! Latency is {0}ms".format(round(client.latency, 1)))

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
        await ctx.respond(f'{ctx.author.mention}, successfully cleared {str(number)} messages.', delete_after=3)
    else:
        #Throws error if author doesn't have permission.
        await ctx.respond(f"{ctx.author.mention}, you don't have permission to use this command.", delete_after=3)

#Random Command
@client.slash_command(name="random", description="Choose between 2 random numbers.")
async def random(ctx, number1, number2):
    #Try to use the two numbers and see if they can be used as an int
    try:
        #Respond to the user with a chosen number between number1 and number2 using the random module.
        await ctx.respond(f'{ctx.author.mention}, between {number1} and {number2}, I choose {str(rand.randrange(int(number1), int(number2)))}.')
    except ValueError:
        #Returns an error if one or both of the numbers are invalid.
        await ctx.respond(f'{ctx.author.mention}, please enter 2 valid numbers.', delete_after=3)
    
#Repeat command
@client.slash_command(name="repeat", description = "I will repeat something!")
async def repeat(ctx, message):
    await ctx.respond(message)

#Send command
@client.slash_command(name="send", description = "I will send something!")
async def repeat(ctx, message, channel: discord.TextChannel):
    if ctx.author.guild_permissions.administrator:
        await channel.send(message)
        await ctx.respond(f'{ctx.author.mention}, I sent your message!', delete_after=3)
    else:
        await ctx.respond(f"{ctx.author.mention}, you don't have permission to use this command. Please note that for safety reasons only admins can use this command.", delete_after=3)

#Play command
@client.slash_command(name="play", description="Play music from NBGames games!")
async def play(ctx, channel: discord.VoiceChannel, announce: bool):
    #Check if the bot is in a voice channel.
    inVoiceChannel = ctx.voice_client

    if inVoiceChannel:
        #Disconnect from the voice channel
        await inVoiceChannel.disconnect()
    
    #Connect to the voice channel
    vc = await channel.connect()
    await ctx.respond(f"{ctx.author.mention}, I'm connecting to play some music!")

    while vc.is_connected():
        channel = ctx.channel
        folder = "music"
        #Check the folder for music
        files = [f for f in os.listdir(folder) if f.endswith('.mp3')]
        fileToPlay = rand.choice(files)
        fileToPlay = os.path.join(folder, fileToPlay)
        #Play it
        vc.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source=fileToPlay))

        #Message the channel about which song is playing
        if announce:
            dir, filename = os.path.split(fileToPlay)
            songNum, extension = os.path.splitext(filename)
            songnames = f'{os.getcwd()}\\resources\\song_names.txt'
            allSongs = open(songnames).readlines()
            await channel.send(f'**Now Playing: {allSongs[int(songNum)]}**')

        #This will loop the music
        while vc.is_playing():
            await asyncio.sleep(3)
        
        continue

#Disconnect command
@client.slash_command(name="disconnect", description="Disconnect me from the voice channel.")
async def disconnect(ctx):
    vc = ctx.voice_client

    if vc:
        await vc.disconnect()
        await ctx.respond(f"{ctx.author.mention}, I've disconnected from the voice channel.", delete_after=3)
    else:
        await ctx.respond(f"{ctx.author.mention}, I'm not connected to a voice channel.", delete_after=3)

#Game Command
@client.slash_command(name="game", description="Get info on a game made by NBGames.")
async def game(ctx, gamename):
    #Convert the gamename string to be entirely lowercase. Best to do this so it's easier to use in an if statement.
    gamename = gamename.lower()

    if gamename in games:
        embed = discord.Embed(title=games[gamename]["title"], color=discord.Color.blue())
        embed.add_field(name="About", value=games[gamename]["about"], inline=False)
        embed.add_field(name="Release Date", value=games[gamename]["release_date"], inline=False)
        embed.add_field(name="More Info", value=games[gamename]["more_info"], inline=False)
        embed.set_thumbnail(url=games[gamename]["thumbnail"])
        await ctx.respond(embed=embed)
    else:
        await ctx.respond(f'{ctx.author.mention}, I do not understand which game you are talking about. Did you make a spelling error?', delete_after=3)

#Add command
@client.slash_command(name="add", description="Get the sum of two numbers.")
async def addition(ctx, num1, num2):
    try:
        await ctx.respond(f'{ctx.author.mention}, the sum of {num1} and {num2} is {int(num1) + int(num2)}.')
    except ValueError:
        await ctx.respond(f'{ctx.author.mention}, please enter valid numbers.', delete_after=3)

#Subtract command
@client.slash_command(name="subtract", description="Get the difference of two numbers.")
async def difference(ctx, num1, num2):
    try:
        await ctx.respond(f'{ctx.author.mention}, the difference of {num1} and {num2} is {int(num1) - int(num2)}.')
    except ValueError:
        await ctx.respond(f'{ctx.author.mention}, please enter valid numbers.', delete_after=3)

#Product command
@client.slash_command(name="multiply", description="Get the product of two numbers.")
async def product(ctx, num1, num2):
    try:
        await ctx.respond(f'{ctx.author.mention}, the product of {num1} and {num2} is {int(num1) * int(num2)}.')
    except ValueError:
        await ctx.respond(f'{ctx.author.mention}, please enter valid numbers.', delete_after=3)

#Divide command
@client.slash_command(name="divide", description="Get the quotient of two numbers.")
async def quotient(ctx, num1, num2):
    try:
        await ctx.respond(f'{ctx.author.mention}, the quotient of {num1} and {num2} is {int(num1) // int(num2)}.')
    except ValueError:
        await ctx.respond(f'{ctx.author.mention}, please enter valid numbers.', delete_after=3)

#8Ball Command
@client.slash_command(name="8ball", description="Get an answer from the 8 Ball!")
async def ball(ctx, question):
    answers = open(f'{os.getcwd()}\\resources\\8answers.txt').read().splitlines()
    await ctx.respond(f'{ctx.author.mention}, {rand.choice(answers)}')

#Coinflip command
@client.slash_command(name="coinflip", description="Flip a coin!")
async def coinflip(ctx, choice):
    ch = rand.randint(1,2)
    if choice == "h" or choice == "heads":
        if ch == 1:
            await ctx.respond(f'{ctx.author.mention}, the coin flips heads... You win...')
        else:
            await ctx.respond(f'{ctx.author.mention}, the coin flips tails! I win!')
    elif choice == "t" or choice == "tails":
        if ch == 1:
            await ctx.respond(f'{ctx.author.mention}, the coin flips heads! I win!')
        else:
            await ctx.respond(f'{ctx.author.mention}, the coin flips tails... You win...')
    else:
        await ctx.respond(f'{ctx.author.mention}, please choose a side (type "h" or "t").', delete_after=3)

#Joke command
@client.slash_command(name="joke", description="I'll tell you a joke!")
async def joke(ctx):
    jokes = open(f'{os.getcwd()}\\resources\\jokes.txt', encoding='utf-8').read().splitlines()
    await ctx.respond(f'{ctx.author.mention}, {rand.choice(jokes)}')

#Translate command
@client.slash_command(name="translate", description="Translate a message!")
async def trans(ctx, message, lang_code):
    m = translate.Translate(message, lang_code)
    await ctx.respond(f'{ctx.author.mention}, {m}')

#Memberinfo Command
@client.slash_command(name="memberinfo", description="Get info about a member.")
async def userinfo(ctx, member: discord.Member):
    embed=discord.Embed(title=f'{member}', description=f'{member.id}', color=discord.Color.blue())
    embed.set_thumbnail(url=member.display_avatar)
    embed.add_field(name="Registered On", value=f'{member.created_at.strftime("%A, %b %d, %Y")}', inline=True)
    embed.add_field(name="Joined On", value=f'{member.joined_at.strftime("%A, %b %d, %Y")}', inline=True)
    await ctx.respond(embed=embed)

#Serverinfo Command
@client.slash_command(name="serverinfo", description="Get info about the server.")
async def userinfo(ctx):
    embed=discord.Embed(title=f'{ctx.guild}', description=f'{ctx.guild.id}', color=discord.Color.blue())
    if(ctx.guild.icon):
        embed.set_thumbnail(url=ctx.guild.icon)
    embed.add_field(name="Created On", value=f'{ctx.guild.created_at.strftime("%A, %b %d, %Y")}', inline=True)
    embed.add_field(name="Owner", value=f'{ctx.guild.owner.mention}', inline=True)
    embed.add_field(name='\u200b', value='\u200b')
    embed.add_field(name="Member Count", value=f'{ctx.guild.member_count}', inline=True)
    embed.add_field(name="Notification Setting", value=f'{ctx.guild.default_notifications}', inline=True)
    embed.add_field(name="Large", value=f'{ctx.guild.large}', inline=True)
    await ctx.respond(embed=embed)

token = environ["TOKEN"]
client.run(token)