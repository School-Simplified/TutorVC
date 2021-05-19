from discord.ext import commands, tasks
import discord
import logging
import json
import datetime
from peewee import _truncate_constraint_name
from core import database
from datetime import timedelta, datetime
import asyncio
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
    now = datetime.now()
    output = convert_time_to_seconds(time)
    if output == None:
        return None

    add = timedelta(seconds = int(output))
    now_plus_10 = now + add
    print(now_plus_10)

    return now_plus_10.strftime(r"%I:%M %p")

def showTotalMinutes(dateObj: datetime):
    now = datetime.now()

    deltaTime = now - dateObj

    seconds = deltaTime.seconds
    minutes = (seconds % 3600) // 60
    return minutes
    

class SkeletonCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def rename(self, ctx, *, name = None):
        database.db.connect(reuse_if_open=True)
        team = discord.utils.get(ctx.guild.roles, name='Academics Team')
        dj = discord.utils.get(ctx.guild.roles, name='DJ')
        member = ctx.guild.get_member(ctx.author.id)

        voice_state = member.voice

        if (team in ctx.author.roles or dj in ctx.author.roles):
            if voice_state == None:
                await ctx.send("You need to be in a voice channel you own to use this!")

            else:
                if member.voice.channel.category_id == categoryID:
                    query = database.VCChannelInfo.select().where(database.VCChannelInfo.authorID == ctx.author.id)

                    if query.exists():
                        q: database.VCChannelInfo = database.VCChannelInfo.select().where(database.VCChannelInfo.authorID == ctx.author.id).get()
                        
                        print(member.voice.channel.id)
                        print(q.ChannelID)
                        if member.voice.channel.id == int(q.ChannelID):
                            if name != None:
                                embed = discord.Embed(title = "ReNamed Channel", description = f"I have changed the channel's name to:\n**{name}**", color = discord.Colour.green())
                                
                                print(name)
                                await member.voice.channel.edit(name = name)
                                await ctx.send(embed = embed)

                                q.name = name
                                q.save()
                            else:
                                embed = discord.Embed(title = "ReNamed Channel", description = f"I have changed the channel's name to:\n**{name}**", color = discord.Colour.green())
                                
                                await member.voice.channel.edit(name = f"{member.display_name}'s Tutoring Channel")
                                await ctx.send(embed = embed)
                                q.name = f"{member.display_name}'s Tutoring Channel"
                                q.save()

                        else:
                            embed = discord.Embed(title = "Ownership Check Failed", description = f"You are not the owner of this voice channel, please ask the original owner <@{q.authorID}>, to rename it!", color = discord.Colour.red())
                            
                            await ctx.send(embed = embed)

                    else:
                        q = database.VCChannelInfo.select().where(database.VCChannelInfo.ChannelID == member.voice.channel.id)
                        embed = discord.Embed(title = "Ownership Check Failed", description = f"You are not the owner of this voice channel, please ask the original owner <@{q.authorID}>, to rename it!", color = discord.Colour.dark_red())
                            
                        await ctx.send(embed = embed)
                else:
                    embed = discord.Embed(title = "Unknown Channel", description = f"You are not the owner of this voice channel nor is this a valid channel. Please execute the command under a channel you own!", color = discord.Colour.red())
                            
                    await ctx.send(embed = embed)
        database.db.close()

    @commands.command()
    async def end(self, ctx):
        database.db.connect(reuse_if_open=True)
        team = discord.utils.get(ctx.guild.roles, name='Academics Team')
        member = ctx.guild.get_member(ctx.author.id)
        timestamp2 = datetime.now()

        voice_state = member.voice

        if team in ctx.author.roles:
            if voice_state == None:

                embed = discord.Embed(title = "Unknown Voice Channel", description = "You have to be in a voice channel you own in order to use this!", color = discord.Colour.dark_red())
                return await ctx.send(embed = embed)

            else:
                if voice_state.channel.id in presetChannels:
                    embed = discord.Embed(title = "UnAuthorized Channel Deletion", description = "You are not allowed to delete these channels!\n\n**Error Detection:**\n**1)** Detected Static Channels", color = discord.Colour.dark_red())
                    return await ctx.send(embed = embed)

                if member.voice.channel.category_id == categoryID:
                    query = database.VCChannelInfo.select().where((database.VCChannelInfo.authorID == ctx.author.id) & (database.VCChannelInfo.ChannelID == voice_state.channel.id))

                    if query.exists():
                        q: database.VCChannelInfo = database.VCChannelInfo.select().where((database.VCChannelInfo.authorID == ctx.author.id) & (database.VCChannelInfo.ChannelID == voice_state.channel.id)).get()
                        
                        tag: database.IgnoreThis = database.IgnoreThis.create(channelID = voice_state.channel.id, authorID = member.id)
                        tag.save()

                        day = showTotalMinutes(q.datetimeObj)

                        await asyncio.sleep(1)
                        await voice_state.channel.delete()
                        embed = discord.Embed(title = "Ended Session", description = "I have successfully ended the session!", color = discord.Colour.blue())
                        embed.add_field(name = "Time Spent", value = f"{member.mention} you have spent a total of `{day} minutes` in voice channel, **{q.name}**.")
                        await ctx.send(embed = embed)

                        q.delete_instance()

                        

                    else:
                        try:
                            q = database.VCChannelInfo.select().where(database.VCChannelInfo.ChannelID == voice_state.channel.id).get()
                        except:
                            embed = discord.Embed(title = "Ownership Check Failed", description = f"This isn't a tutoring channel! Please use the command on an actual tutoring channel!", color = discord.Colour.red())
                        else:
                            embed = discord.Embed(title = "Ownership Check Failed", description = f"You are not the owner of this voice channel, please ask the original owner <@{q.authorID}>, to end it!", color = discord.Colour.red())
                        finally:
                            await ctx.send(embed = embed)
                else:
                    embed = discord.Embed(title = "Unknown Channel", description = f"You are not the owner of this voice channel nor is this a valid channel. Please execute the command under a channel you own!", color = discord.Colour.red())
                            
                    await ctx.send(embed = embed)
        database.db.close()

    @commands.command()
    @commands.has_role(784202171825913856) #Acad Manager
    async def forceend(self, ctx, channel: discord.VoiceChannel):
        database.db.connect(reuse_if_open=True)
        team = discord.utils.get(ctx.guild.roles, name='Academics Manager')
        member = ctx.guild.get_member(ctx.author.id)
        timestamp2 = datetime.now()

        #voice_state = member.voice

        if team in ctx.author.roles:
            if channel.id in presetChannels:
                embed = discord.Embed(title = "UnAuthorized Channel Deletion", description = "You are not allowed to delete these channels!\n\n**Error Detection:**\n**1)** Detected Static Channels", color = discord.Colour.dark_red())
                return await ctx.send(embed = embed)

            if channel.category_id == categoryID:
                query = database.VCChannelInfo.select().where((database.VCChannelInfo.authorID == ctx.author.id) & (database.VCChannelInfo.ChannelID == channel.id))

                if query.exists():
                    q: database.VCChannelInfo = database.VCChannelInfo.select().where((database.VCChannelInfo.authorID == ctx.author.id) & (database.VCChannelInfo.ChannelID == channel.id)).get()

                    day = showTotalMinutes(q.datetimeObj)


                    for VCMember in channel.members:
                        if team in VCMember.roles:
                            tag: database.IgnoreThis = database.IgnoreThis.create(channelID = channel.id, authorID = VCMember.id)
                            tag.save()
                            print(f"Added: {VCMember.id}")
                            
                    
                    await channel.delete()
                    embed = discord.Embed(title = "Ended Session", description = "I have successfully ended the session!", color = discord.Colour.blue())
                    embed.add_field(name = "Time Spent", value = f"{member.mention} you have spent a total of `{day} minutes` in voice channel, **{q.name}**.")
                    await ctx.send(embed = embed)

                    q.delete_instance()

                else:
                    await channel.delete()
                    embed = discord.Embed(title = "Partial Completion", description = f"The database indicates there is no owner or data related to this voice channel but I have still deleted the channel!", color = discord.Colour.gold())
                        
                    await ctx.send(embed = embed)
                    
            else:
                embed = discord.Embed(title = "Unknown Channel", description = f"You are not the owner of this voice channel nor is this a valid channel. Please execute the command under a tutoring channel!", color = discord.Colour.red())
                        
                await ctx.send(embed = embed)
        database.db.close()

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(title = "Help Commands", description = "All avaliable commands under this bot!", color = discord.Colour.blue())
        embed.add_field(name = "Notion Page" ,value = f"**Notion Page:** [Help Page](https://www.notion.so/TutorVC-Guide-e28c70a5aa344a3db941b192442e664c \"Masa if you see this, ur short\")")
        embed.set_footer(text = "Ping Space for any questions or concerns.")
        await ctx.send(embed = embed)







        


def setup(bot):
    bot.add_cog(SkeletonCMD(bot))


