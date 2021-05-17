from discord.ext import commands, tasks
import discord
import logging
import json
import datetime
from peewee import _truncate_constraint_name
from core import database
from datetime import timedelta, datetime
import asyncio
from pytz import timezone
tz = timezone('EST')
#from main import vc

#Variables
channel_id = 843637802293788692
categoryID = 776988961087422515

staticChannels = [784556875487248394, 784556893799448626]
presetChannels = [843637802293788692, 784556875487248394, 784556893799448626]
time_convert = {"s": 1, "m": 60, "h": 3600, "d": 86400}



def convert_time_to_seconds(time):
    try:
        value = int(time[:-1]) * time_convert[time[-1]]
    except:
        value = time
    finally:
        if value < 60:
            return None
        else:
            return value
    

def showFutureTime(time):
    now = datetime.now(tz)
    output = convert_time_to_seconds(time)
    if output == None:
        return None

    add = timedelta(seconds = int(output))
    now_plus_10 = now + add
    print(now_plus_10)

    return now_plus_10.strftime(r"%I:%M %p")

def showTotalMinutes(dateObj: datetime):
    now = datetime.now(tz)

    deltaTime = now - dateObj

    seconds = deltaTime.seconds
    minutes = (seconds % 3600) // 60
    return minutes
    

class SkeletonCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        database.db.connect(reuse_if_open=True)
        lobbyStart = await self.bot.fetch_channel(784556875487248394)

        if after.channel == None and not member.bot:
            acadChannel = await self.bot.fetch_channel(channel_id)
            team = discord.utils.get(member.guild.roles, name='Academics Team')
            query = database.VCChannelInfo.select().where((database.VCChannelInfo.authorID == member.id) & (database.VCChannelInfo.ChannelID == before.channel.id))

            ignoreQuery = database.IgnoreThis.select().where((database.IgnoreThis.authorID == member.id) & (database.IgnoreThis.channelID == before.channel.id))

            if ignoreQuery.exists():
                iq: database.IgnoreThis = database.IgnoreThis.select().where((database.IgnoreThis.authorID == member.id) & (database.IgnoreThis.channelID == before.channel.id)).get()
                iq.delete_instance()
                return print("Ignore Channel")

            if query.exists() and team in member.roles and before.channel.category.id == categoryID:
                query = database.VCChannelInfo.select().where((database.VCChannelInfo.authorID == member.id) & (database.VCChannelInfo.ChannelID == before.channel.id)).get()

                print(query.ChannelID)
                print(before.channel.id)
                if query.ChannelID == str(before.channel.id):
                    embed = discord.Embed(title = "WARNING: Voice Channel is about to be deleted!", description = "If the tutoring session has ended, **you can ignore this!**\n\nIf it hasn't ended, please make sure you return to the channel in **2** Minutes, otherwise the channel will automatically be deleted!", color= discord.Colour.red())

                    await acadChannel.send(content = member.mention, embed = embed)
                    await asyncio.sleep(120)

                    print(before.channel)
                    if member in before.channel.members:
                        return print("returned")
                    else:
                        day = showTotalMinutes(query.datetimeObj)
                        #value = divmod(deltaTime.total_seconds(), 60)

                        try:
                            await before.channel.delete()
                        except Exception as e:
                            print(f"Error Deleting Channel:\n{e}")
                        else:
                            embed = discord.Embed(title = f"{member.display_name} Total Voice Minutes", description = f"{member.mention} you have spent a total of `{day} minutes` in voice channel, **{query.name}**.", color = discord.Colour.gold())
                            embed.set_footer(text = "The voice channel has been deleted!")
                            await acadChannel.send(content = member.mention, embed = embed) 
                        finally:
                            query.delete_instance() 
                        

                else:
                    print("no")
            #database.db.close()




        elif after.channel != None and after.channel == lobbyStart and not member.bot:
            team = discord.utils.get(member.guild.roles, name='Academics Team')
            acadChannel = await self.bot.fetch_channel(channel_id)

            if team in member.roles:
                category = discord.utils.get(member.guild.categories, id = categoryID)

                if len(category.voice_channels) >= 12:
                    embed = discord.Embed(title = "Max Channel Allowance", description = "I'm sorry! This category has reached its full capacity at **12** voice channels!\n\n**Please wait until a tutoring session ends before creating a new voice channel!**", color = discord.Colour.red())
                    await member.move_to(None, reason = "Max Channel Allowance")
                    return await acadChannel.send(content = member.mention, embed = embed)


                query = database.VCChannelInfo.select().where(database.VCChannelInfo.authorID == member.id)
                if query.exists():
                    embed = discord.Embed(title = "Maximum Channel Ownership Allowance", description = "I'm sorry! You already have an active tutoring voice channel and thus you can't create anymore channels.\n\n**If you would like to remove the channel without waiting the 2 minutes, use `+end`!**", color = discord.Colour.red())
                    await member.move_to(None, reason = "Maximum Channel Ownership Allowance")
                    return await acadChannel.send(content = member.mention, embed = embed)

                def check(m):
                    return m.content is not None and m.channel == acadChannel and m.author is not self.bot.user and m.author == member

                embed = discord.Embed(title = "Tutoring Voice Channel Creation", description = "Hey there! I see you've attempted to create a voice channel, please remember that if you disconnect from the voice channel. You will have **2** minutes to rejoin in order to prevent losing the channel!\n *But anyway, I have just created you're own channel!*", color = discord.Colour.green())
                embed.set_footer(text = "If you have any questions, DM or Ping Space!")

                

                voice_client: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild= member.guild)
                audio_source = discord.FFmpegPCMAudio('confirm.mp3')

                voice_client.play(audio_source)
                await asyncio.sleep(2)

                await acadChannel.send(content = member.mention, embed = embed)


                channel = await category.create_voice_channel(f"{member.display_name}'s Tutoring Channel", user_limit = 2)
                tag: database.VCChannelInfo = database.VCChannelInfo.create(ChannelID = channel.id, name = f"{member.display_name}'s Tutoring Channel", authorID = member.id, used = True, datetimeObj = datetime.now(tz))
                tag.save()

                pos = len(category.voice_channels) - 1
                print(pos)
                #await channel.edit(position = pos)
                await member.move_to(channel, reason = "Response Code: OK -> Moving to VC | Created Tutor Channel")

            else:
                voice_client: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild= member.guild)
                audio_source = discord.FFmpegPCMAudio('no.mp3')
                await asyncio.sleep(1)

                voice_client.play(audio_source)
                await asyncio.sleep(2)
                await member.move_to(None, reason = "Not an academics member")
        database.db.close()
        


def setup(bot):
    bot.add_cog(SkeletonCMD(bot))


