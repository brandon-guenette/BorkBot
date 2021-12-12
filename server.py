import discord
import asyncio 

file = open('token', 'r')

token = file.readline()

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents = intents)


games = {}


@client.event
async def on_message(message):
    if message.content.startswith('!e '):
        parts = message.content.split()
        game = parts[1]
        minutes_util_game = float(parts[2])
        sentMessage = await message.channel.send(f'**{message.author.name}** is starting a game of **{game}** in **{minutes_util_game}** minutes. If you would like to join, react to this message.')
        games[sentMessage.id] = []
        await asyncio.sleep(minutes_util_game*60)
        await message.channel.send(f'**{message.author.name}\'s** game is beginning now.\n {" ".join([f"<@{user_id}>" for user_id in games[sentMessage.id]])}')
        games.pop(sentMessage.id)
        



@client.event
async def on_reaction_add(reaction, user):
    if reaction.message.id in games:
        if user.id not in games[reaction.message.id]:
            games[reaction.message.id].append(user.id)
            print(games)


@client.event
async def on_reaction_remove(reaction, user):   
    if reaction.message.id in games:
        if user.id in games[reaction.message.id]:
            games[reaction.message.id].remove(user.id)
            print(games)


#TODO: Remember to keep user name in list if at least one of their reactions remain on the message





# @client.event
# async def on_voice_state_update(member, before, after):
#     print(before.
#     print(after)
#     if not member.nick:
#         print(member.name)
#     else:
#         print(member.nick)
   

# ty yaakov





client.run(token)