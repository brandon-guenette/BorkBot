import discord
import asyncio 
import json
import os
import requests
import time

discord_file = open('discord_token', 'r')
twitter_file = open('twitter_token', 'r')

discord_token = discord_file.readline()
twitter_token = twitter_file.readline()

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True

client = discord.Client(intents = intents)


games = {}

def auth():
    return twitter_token


def create_headers(twitter_token):
    headers = {"Authorization": "Bearer {}".format(twitter_token)}
    return headers

def create_url(keyword, api, max_results = 0):

    twitter_url = "https://api.twitter.com/2/"

    if api == 'search':
        search_url = twitter_url + 'tweets/search/recent' 
        query_params = {'query': keyword,
                    # 'start_time': start_date,
                    # 'end_time': end_date,
                    'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
                    'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
                    'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
                    'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
                    'next_token': {}}
        if max_results != 0:
            query_params['max_results'] = max_results
        return(search_url, query_params)

    elif api == 'userlookup':
        search_url = twitter_url + 'users/by/username/' + keyword
        return(search_url, [])
    
    elif api == 'recent':
        search_url = twitter_url + 'users/{}/tweets'.format(keyword)
        return(search_url, [])    


def connect_to_endpoint(url, headers, params = dict(), next_token = None):
    print(url)
    if next_token:
        params['next token'] = next_token
    response = requests.request("GET", url, headers = headers, params = params)
    print(response)
    print("Endpoint Response Code: " + str(response.status_code))
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

headers = create_headers(twitter_token)


"""
Discord bot code

"""

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
    
    
    else:
        cutmsg = message.content[3::]
        searchInfo = cutmsg.split(',')
        print(json.dumps(searchInfo, indent=4))
        keyword = searchInfo[0]
        if len(searchInfo) > 1:
            max_results = searchInfo[1]
            print(max_results)
        print(keyword)

        if message.content.startswith("!s "):
            api = 'search'
            url = create_url(keyword, api, max_results)
            json_response = connect_to_endpoint(url[0], headers, url[1])
            print(json.dumps(json_response, indent=4, sort_keys=True))
    
        if message.content.startswith("!u "):
            
# Get User ID

            api = 'userlookup'
            url = create_url(keyword, api)
            json_response = connect_to_endpoint(url[0], headers)
            id = json_response["data"]["id"]


            api = 'recent'
            url = create_url(id, api)
            urldict = dict()
            urldict["max_results"] = max_results
            json_response = connect_to_endpoint(url[0], headers, urldict)

            combinemessage = ''
            for tweet in json_response['data']:
                if tweet['text'].lower().find("just launched") >= 0:
                    print(tweet['text'])
                    combinemessage += f"{tweet['text']}\n"
                else:
                    combinemessage += f"{tweet['text']}\n"
            await message.channel.send(combinemessage.rstrip())





       



@client.event
async def on_reaction_add(reaction, user):
    if reaction.message.id in games:
        if user.id not in games[reaction.message.id]:
            games[reaction.message.id].append(user.id)


@client.event
async def on_reaction_remove(reaction, user):   
    if reaction.message.id in games:
        if user.id in games[reaction.message.id]:
            games[reaction.message.id].remove(user.id)


#TODO: Remember to keep user name in list if at least one of their reactions remain on the message



# @client.event
# async def on_voice_state_update(member, before, after):
#     if before.self_stream == True and after.self_stream == False:
#          async for guild in client.fetch_guilds(limit=150):
#             if guild.name == "Sensible Doggos":
#                 allchannels = await guild.fetch_channels()
#                 for channel in allchannels:
#                     if channel.name == "bot-land":
#                         await channel.send(f"{member.nick} Game over, time to do pushups")
                
                
        
#TODO fix this shit
# ty yaakov
while True:
    client.run(discord_token)
    client.run(twitter_token)
    time.sleep(3600)