import discord, random as rand, os, asyncio, json
from discord.ext import commands
from os import environ
from dotenv import load_dotenv
from datetime import datetime
from datetime import timedelta
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from pathlib import Path
import difflib

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix='.', intents=intents)

sendWelcome = True
sendDMs = True
start_time = datetime.now()

#XP Settings
xpCooldowns = {}
xpCooldown = 60

load_dotenv()

with open("resources/games.json", "r") as gamesRes:
    games = json.load(gamesRes)

xpfile = Path("resources/xp.json")

if xpfile.exists():
    with xpfile.open("r") as f:
        xp_data = json.load(f)
else:
    xp_data = {}


#Starting up the bot
@client.event
async def on_ready():
    print('Logged on!')
    game = environ["GAME_ACTIVITY"]
    await client.change_presence(status=environ["ACTIVITY"], activity=discord.Game(name=game))

#Circular Avatar Function
async def circular_avatar(member: discord.Member, size: int) -> Image.Image:
    data = BytesIO(await member.display_avatar.read())
    avatar = Image.open(data).convert("RGBA").resize((size, size))

    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)

    output = Image.new("RGBA", (size, size))
    output.paste(avatar, (0, 0), mask)

    return output

#Welcome message
@client.event
async def on_member_join(member: discord.Member):
    if sendWelcome:
        welcomeChannelName = environ["WELCOMECHANNEL"]
        rulesChannel = environ["RULESCHANNEL"]
        welcomeChannel = discord.utils.get(member.guild.channels, name=welcomeChannelName)

        if welcomeChannel is None:
            return

        #load welcome base image
        welcomeImage = Image.open("./baseimages/welcome.png").convert("RGBA")

        #Get circular pfp
        circle_pfp = await circular_avatar(member, 145)

        #Paste onto welcome
        welcomeImage.paste(circle_pfp, (253, 59), circle_pfp)

        image_bytes = BytesIO()
        welcomeImage.save(image_bytes, format="PNG")
        image_bytes.seek(0)

        await welcomeChannel.send(content=f"Hello, {member.mention}! Welcome to {member.guild.name}. Please be sure to read <#{rulesChannel}> before you start chatting!", file=discord.File(fp=image_bytes, filename="welcome.png"))

#Help Command
@client.slash_command(name = "help", description = "See all commands.")
async def help(ctx):
    embed=discord.Embed(title="nbbot Help", description="Here are all the commands for nbbot.", color=discord.Color.blue())
    embed.add_field(name="nbgames Content", value="bug: Report a bug directly to nbgames.\ngame: Get information about a game by nbgames.\nplay: Play music from nbgames' games!", inline=False)
    embed.add_field(name="Administration", value="ban: Bans a member.\nkick: Kicks a member.\nmute: Mutes a member.\nunmute: Unmutes a member\npurge: Clears an amount of messages in the channel.\nsend: I will send something!\nslowmode: Set the slowmode delay of this channel.\ntimeout: Times out a member.", inline=False)
    embed.add_field(name="Fun", value="8ball: Get an answer from the 8 Ball!\ncoinflip: Flip a coin!\njerry: Become Jerry!\njoke: I'll tell you a joke!\nlevel: Check your level stats.\nrate: I will rate an item!\ntouchgrass: Advise someone to touch grass!\nzamn: ZAMN!")
    embed.add_field(name="Math", value="add: Get the sum of two numbers.\nsubtract: Get the difference of two numbers.\nmultiply: Get the product of two numbers.\ndivide: Get the quotient of two numbers.")
    embed.add_field(name="Other", value="avatar: Grabs a member's avatar.\nhelp: See all commands.\nmemberinfo: Gets info about a member.\nping: Get latency.\nrandom: Picks between 2 numbers.\nrepeat: I will repeat something!\nserverinfo: Get info about the server.\nuptime: How long has nbbot been up for?", inline=False)
    await ctx.respond(embed=embed)

#Ping Command
@client.slash_command(name = "ping", description = "Get latency.")
async def ping(ctx):
    await ctx.respond(f"{ctx.author.mention}, pong! Latency is {0}ms.".format(round(client.latency, 1)))

#Ban Command
@client.slash_command(name = "ban", description = "Ban a member.")
async def ban(ctx, member: discord.Member, reason:str):

    #First, check if the member is higher than the bot.
    if member.top_role >= ctx.guild.me.top_role:
        #Throws error if bot can't ban the specified member.
        await ctx.respond(f"{ctx.author.mention}, I don't have the ability to ban this member.", delete_after=3, ephemeral=True)
        return

    #Checks if the author has permission to ban members.
    if ctx.author.guild_permissions.ban_members:
        await member.ban(reason=reason)
        await ctx.respond(f"{ctx.author.mention}, banned @{member.mention} successfully for {reason}.", delete_after=3, ephemeral=True)
    else:
        #Throws error if author doesn't have permission.
        await ctx.respond(f"{ctx.author.mention}, you don't have permission to use this command.", delete_after=3, ephemeral=True)

#Kick Command
@client.slash_command(name = "kick", description = "Kick a member.")
async def kick(ctx, member: discord.Member, reason: str):

    #First, check if the member is higher than the bot.
    if member.top_role >= ctx.guild.me.top_role:
        #Throws error if bot can't kick the specified member.
        await ctx.respond(f"{ctx.author.mention}, I don't have the ability to kick this member.", delete_after=3, ephemeral=True)
        return

    #Checks if the author has permission to kick members.
    if ctx.author.guild_permissions.kick_members:
        await member.kick(reason=reason)
        await ctx.respond(f"{ctx.author.mention}, kicked @{member.mention} successfully for {reason}.", delete_after=3, ephemeral=True)
    else:
        #Throws error if author doesn't have permission.
        await ctx.respond(f"{ctx.author.mention}, you don't have permission to use this command.", delete_after=3, ephemeral=True)

#Mute Command
@client.slash_command(name="mute", description = "Mute a member.")
async def mute(ctx, member: discord.Member, reason: str):

    #First, check if the member is higher than the bot.
    if member.top_role >= ctx.guild.me.top_role:
        #Throws error if bot can't mute the specified member.
        await ctx.respond(f"{ctx.author.mention}, I don't have the ability to mute this member.", delete_after=3, ephemeral=True)
        return

    #Checks if the author has permission to mute members.
    if ctx.author.guild_permissions.moderate_members:
        #Checks the mentioned user for the ability to send messages.
        if ctx.channel.permissions_for(member).send_messages:
            await ctx.channel.set_permissions(member, send_messages=False)
            await ctx.respond(f"{ctx.author.mention}, muted {member.mention} successfully for {reason}.", delete_after=3, ephemeral=True)

            if sendDMs:
                try:
                    await member.send(content=f"{member.mention}, you have been muted in {ctx.guild.name} for the following reason: **{reason}**")
                except discord.Forbidden:
                    pass
        else:
            #Sends error message if the user is already muted/can't send messages.
            await ctx.respond(f"{ctx.author.mention}, {member.mention} is already muted.", delete_after=3, ephemeral=True)
    else:
        #Throws error if author doesn't have permission.
        await ctx.respond(f"{ctx.author.mention}, you don't have permission to use this command.", delete_after=3, ephemeral=True)

#Unmute Command
@client.slash_command(name="unmute", description = "Unmute a member.")
async def mute(ctx, member: discord.Member):
    #Checks if the author has permission to mute members.
    if ctx.author.guild_permissions.moderate_members:
        #Checks the mentioned user for the ability to send messages.
        if not ctx.channel.permissions_for(member).send_messages:
            await ctx.channel.set_permissions(member, send_messages=True)
            await ctx.respond(f"{ctx.author.mention}, unmuted {member.mention} successfully.", delete_after=3, ephemeral=True)
        else:
            #Sends error message if the user isn't muted/can send messages.
            await ctx.respond(f"{ctx.author.mention}, {member.mention} isn't muted.", delete_after=3, ephemeral=True)
    else:
        #Throws error if author doesn't have permission.
        await ctx.respond(f"{ctx.author.mention}, you don't have permission to use this command.", delete_after=3, ephemeral=True)

#Timeout command
@client.slash_command(name="timeout", description = "Timeout a member.")
async def timeout(ctx, member: discord.Member, minutes: int, reason: str):

    #First, check if the member is higher than the bot.
    if member.top_role >= ctx.guild.me.top_role:
        #Throws error if bot can't timeout the specified member.
        await ctx.respond(f"{ctx.author.mention}, I don't have the ability to timeout this member.", delete_after=3, ephemeral=True)
        return
    
    #Checks if the author has permission to timeout members.
    if ctx.author.guild_permissions.moderate_members:
        until = discord.utils.utcnow() + timedelta(minutes=minutes)
        await member.timeout(until, reason=reason)
        await ctx.respond(f'{ctx.author.mention}, timed out {member.mention} for {minutes} minutes successfully for {reason}.', delete_after=3, ephemeral=True)

        if sendDMs:
            try:
                await member.send(content=f"{member.mention}, you have been timed out in {ctx.guild.name} for {minutes} minutes for the following reason: **{reason}**")
            except discord.Forbidden:
                pass
    else:
        #Throws error if author doesn't have permission.
        await ctx.respond(f"{ctx.author.mention}, you don't have permission to use this command.", delete_after=3, ephemeral=True)

#Purge Command
@client.slash_command(name = "purge", description="Purge the messages of a channel.")
async def purge(ctx, number):
    if ctx.author.guild_permissions.manage_messages:
        #Convert the value number to an actual int
        try:
            number = int(number)
        except ValueError:
            await ctx.respond(f'{ctx.author.mention}, enter a valid number.', delete_after=3, ephemeral=True)
        await ctx.channel.purge(limit=number)
        await ctx.respond(f'{ctx.author.mention}, successfully cleared {str(number)} messages.', delete_after=3, ephemeral=True)
    else:
        #Throws error if author doesn't have permission.
        await ctx.respond(f"{ctx.author.mention}, you don't have permission to use this command.", delete_after=3, ephemeral=True)

#Slowmode command
@client.slash_command(name="slowmode", description="Set the slowmode delay of this channel.")
async def slowmode(ctx, seconds: int):
    if ctx.author.guild_permissions.manage_channels:
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.respond(f"{ctx.author.mention}, slowmode for this channel has been set to {seconds} seconds.", delete_after=3, ephemeral=True)
    else:
        #Throws error if author doesn't have permission.
        await ctx.respond(f"{ctx.author.mention}, you don't have permission to use this command.", delete_after=3, ephemeral=True)

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
async def repeat(ctx, message: str, channel: discord.TextChannel):
    if ctx.author.guild_permissions.administrator:
        await channel.send(message)
        await ctx.respond(f'{ctx.author.mention}, I sent your message!', delete_after=3, ephemeral=True)
    else:
        await ctx.respond(f"{ctx.author.mention}, you don't have permission to use this command. Please note that for safety reasons only admins can use this command.", delete_after=3, ephemeral=True)

#Play command
@client.slash_command(name="play", description="Play music from NBGames games!")
async def play(ctx, channel: discord.VoiceChannel, announce: bool):
    if ctx.author.voice is None:
        await ctx.respond(f"{ctx.author.mention}, you need to be connected to a voice channel to use this command.", delete_after=3, ephemeral=True)
    else:
        #Check if the bot is in a voice channel.
        inVoiceChannel = ctx.voice_client

        if inVoiceChannel:
            #Disconnect from the voice channel
            await inVoiceChannel.disconnect()
        
        #Connect to the voice channel
        vc = await channel.connect()
        await ctx.respond(f"{ctx.author.mention}, I'm connecting to play some music!")

        while vc.is_connected():
            if ctx.author.voice is None:
            #Disconnect from the voice channel
                await ctx.voice_client.disconnect()
                break
            
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
        await ctx.respond(f"{ctx.author.mention}, I'm not connected to a voice channel.", delete_after=3, ephemeral=True)

#Game Command
@client.slash_command(name="game", description="Get info on a game made by NBGames.")
async def game(ctx, gamename):
    #Convert the gamename string to be entirely lowercase. Best to do this so it's easier to use in an if statement.
    gamename = gamename.lower()

        # Exact match
    if gamename in games:
        g = games[gamename]
    else:
        # Try to find a close match
        close_matches = difflib.get_close_matches(gamename, games.keys(), n=1, cutoff=0.6)
        if close_matches:
            g = games[close_matches[0]]
        else:
            return await ctx.respond(f"{ctx.author.mention}, I do not understand which game you are talking about. Did you make a spelling error?", delete_after=3, ephemeral=True)

    embed = discord.Embed(title=g["title"], color=discord.Color.blue())
    embed.add_field(name="About", value=g["about"], inline=False)
    embed.add_field(name="Release Date", value=g["release_date"], inline=False)
    embed.add_field(name="More Info", value=f'Download the latest version [here]({g["more_info"]}).', inline=False)
    embed.set_thumbnail(url=g["thumbnail"])
    await ctx.respond(embed=embed)

#Bug command
@client.slash_command(name="bug", description="Sends a bug report directly to NBGames.")
async def bug(ctx, gamename: str, description: str):
    BUG_FILE = Path("resources/bugreports.json")

    report = {
        "user": f"{ctx.author.name}",
        "user_id": ctx.author.id,
        "gamename": gamename,
        "bug": description,
        "time": datetime.utcnow().isoformat()
    }

    with BUG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(report) + "\n")

    await ctx.respond(f"{ctx.author.mention}, your bug has been reported. Thank you!", delete_after=3, ephemeral=True)

#Add command
@client.slash_command(name="add", description="Get the sum of two numbers.")
async def addition(ctx, num1, num2):
    try:
        await ctx.respond(f'{ctx.author.mention}, the sum of {num1} and {num2} is {int(num1) + int(num2)}.')
    except ValueError:
        await ctx.respond(f'{ctx.author.mention}, please enter valid numbers.', delete_after=3, ephemeral=True)

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

#Rate command
@client.slash_command(name="rate", description="I'll rate something!")
async def rate(ctx, item: str):
    rating = rand.randint(1, 10)
    responses = open(f'{os.getcwd()}\\resources\\ratingresponses.txt', encoding='utf-8').read().splitlines()

    await ctx.respond(f'{ctx.author.mention}, I rate {item} a {rating}/10. {rand.choice(responses)}')

#Rate command
@client.slash_command(name="touchgrass", description="Tell someone to touch grass!")
async def touchgrass(ctx, member: discord.Member):
    await ctx.respond(f'{member.mention}, you have been advised to go touch grass. 🌱')

#Avatar command
@client.slash_command(name="avatar", description="Grabs a member's avatar.")
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author

    embed = discord.Embed(title=f"{member.name}'s Avatar", color=discord.Color.blue())
    embed.set_image(url=member.display_avatar.url)

    await ctx.respond(embed=embed)

#Memberinfo Command
@client.slash_command(name="memberinfo", description="Get info about a member.")
async def userinfo(ctx, member: discord.Member):
    embed=discord.Embed(title=f'{member.name}', description=f'{member.id}', color=discord.Color.blue())
    embed.set_thumbnail(url=member.display_avatar)
    embed.add_field(name="Registered On", value=f'{member.created_at.strftime("%A, %b %d, %Y")}', inline=True)
    embed.add_field(name="Joined On", value=f'{member.joined_at.strftime("%A, %b %d, %Y")}', inline=True)
    embed.add_field(name='\u200b', value='\u200b') #Line Break
    embed.add_field(name="User Activity", value=f'{member.activity}', inline=True)
    embed.add_field(name="Highest Role", value=f'{member.top_role}', inline=True)
    await ctx.respond(embed=embed)

#Serverinfo Command
@client.slash_command(name="serverinfo", description="Get info about the server.")
async def userinfo(ctx):
    embed=discord.Embed(title=f'{ctx.guild}', description=f'{ctx.guild.id}', color=discord.Color.blue())
    if(ctx.guild.icon):
        embed.set_thumbnail(url=ctx.guild.icon)
    embed.add_field(name="Created On", value=f'{ctx.guild.created_at.strftime("%A, %b %d, %Y")}', inline=True)
    embed.add_field(name="Owner", value=f'{ctx.guild.owner.mention}', inline=True)
    embed.add_field(name="System Channel", value=f'{ctx.guild.system_channel.mention}', inline=True)
    embed.add_field(name="Default Role", value=f'{ctx.guild.default_role}', inline=True)
    embed.add_field(name="Member Count", value=f'{ctx.guild.member_count}', inline=True)
    embed.add_field(name="Notification Setting", value=f'{ctx.guild.default_notifications.name.replace("_", " ").title()}', inline=True)
    await ctx.respond(embed=embed)

#Jerry image command
@client.slash_command(name="jerry", description="Become Jerry!")
async def jerry(ctx, member: discord.Member = None):
    jerry = Image.open("./baseimages/jerry.png")

    #Grab user profile picture and load it
    member = member or ctx.author
    data = BytesIO(await member.display_avatar.read())
    pfp = Image.open(data)

    #Resize pfp
    pfp = pfp.resize((50, 50))

    jerry.paste(pfp, (120, 30))
    
    image_bytes = BytesIO()
    jerry.save(image_bytes, format="PNG")
    image_bytes.seek(0) 

    await ctx.respond(file=discord.File(fp=image_bytes, filename="jerry.png"))

#ZAMN!
@client.slash_command(name="zamn", description="ZAMN!")
async def zamn(ctx, member: discord.Member = None):
    zamn = Image.open("./baseimages/zamn.png")

    #Grab user profile picture and load it
    member = member or ctx.author
    data = BytesIO(await member.display_avatar.read())
    pfp = Image.open(data)

    #Resize pfp
    pfp = pfp.resize((251, 359))

    zamn.paste(pfp, (255, 72))
    
    image_bytes = BytesIO()
    zamn.save(image_bytes, format="PNG")
    image_bytes.seek(0) 

    await ctx.respond(file=discord.File(fp=image_bytes, filename="zamn.png"))

@client.slash_command(name="uptime", description="How long has nbbot been up for?")
async def uptime(ctx):
    current = datetime.now()
    elapsed = current - start_time
    await ctx.respond(f'{ctx.author.mention}, nbbot has been up for {elapsed.days} days, {elapsed.seconds // 3600} hours, {(elapsed.seconds % 3600) // 60} minutes, and {elapsed.seconds % 60} seconds.')

#Level command
@client.slash_command(name="level", description="Check your level stats.")
async def level(ctx, member: discord.Member = None):
    member = member or ctx.author
    guild_id = str(ctx.guild.id)
    user_id = str(member.id)

    if guild_id not in xp_data or user_id not in xp_data[guild_id]:
        return await ctx.respond(f"{member.mention} has no XP yet.", ephemeral=True)

    XPdata = xp_data[guild_id][user_id]

    #Make image
    levelBase = Image.open("./baseimages/levelbase.png").convert("RGBA")

    #Load Circular pfp
    circle_pfp = await circular_avatar(member, 145)

    #Paste onto base
    levelBase.paste(circle_pfp, (167, 139), circle_pfp)

    #Load Font
    font_path = Path("resources") / "PowerrSemiBold.ttf"
    font = ImageFont.truetype(str(font_path), 40)
    draw_image = ImageDraw.Draw(levelBase)

    #Draw Text Elements
    draw_image.text((240, 87), f"{member.name}'s Stats", anchor="mm", fill="#00a651", font=font, stroke_width=3, stroke_fill="black")
    draw_image.text((240, 331), f"Level: {XPdata['level']}", anchor="mm" , fill="#00a651", font=font, stroke_width=3, stroke_fill="black")
    draw_image.text((240, 390), f"XP: {XPdata['xp']} / {XPdata['level'] * 100}", anchor="mm", fill="#00a651", font=font, stroke_width=3, stroke_fill="black")

    #Save Image
    image_bytes = BytesIO()
    levelBase.save(image_bytes, format="PNG")
    image_bytes.seek(0) 

    await ctx.respond(file=discord.File(fp=image_bytes, filename="level.png"))

#Message sending logic
@client.event
async def on_message(ctx):
    #Ignore bot messages
    if ctx.author.bot:
        return

    #Ignore DMs
    if not ctx.guild:
        return
    
    #XP system
    user_id = str(ctx.author.id)
    guild_id = str(ctx.guild.id)

    now = datetime.utcnow().timestamp()
    last_xp = xpCooldowns.get(user_id, 0)

    if now - last_xp >= xpCooldown:
        xpCooldowns[user_id] = now

        if guild_id not in xp_data:
            xp_data[guild_id] = {}

        if user_id not in xp_data[guild_id]:
            xp_data[guild_id][user_id] = {"xp": 0, "level": 1}

        gained = rand.randint(5, 15)
        xp_data[guild_id][user_id]["xp"] += gained

        #Level check
        current_xp = xp_data[guild_id][user_id]["xp"]
        current_level = xp_data[guild_id][user_id]["level"]

        xp_needed = current_level * 100

        if current_xp >= xp_needed:
            xp_data[guild_id][user_id]["level"] += 1
            xp_data[guild_id][user_id]["xp"] = 0

            await ctx.channel.send(f"{ctx.author.mention}, you have leveled up to **Level {current_level + 1}**! 🎉")

        #Save
        with xpfile.open("w") as f:
            json.dump(xp_data, f, indent=4)

    #Send message if pinged
    if client.user.mentioned_in(ctx):
        await ctx.channel.send(f'Hello {ctx.author.mention}, how can I assist you?')

    await client.process_commands(ctx)

token = environ["TOKEN"]
client.run(token)