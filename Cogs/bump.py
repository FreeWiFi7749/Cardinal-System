import discord
from discord.ext import commands
import pytz
from datetime import datetime, timedelta
import asyncio

class BumpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def set_timer_and_send_message(self, channel):
        now = datetime.now(pytz.utc) 
        twoh = timedelta(hours=2)
        goodtime = now + twoh 

        goodtime_epoch = int(goodtime.timestamp())
        save_timer_to_json(channel.id, goodtime)
        print(goodtime)
        embed_fir = discord.Embed(title="Bumpされました", description=f"<t:{int(goodtime_epoch)}:R> に再度bumpが可能になります\n<t:{int(goodtime_epoch)}>")
        #embed_fir.set_image(url="https://cdn.discordapp.com/attachments/1104493356781940766/1139546684779679856/IMG_2122.png")
        timer_message = await channel.send(embed=embed_fir)
    
        await asyncio.sleep(7200)

        role_id = 1180551674809557073
        role = discord.utils.get(channel.guild.roles, id=role_id)
        from datetime import time
        jst = pytz.timezone('Asia/Tokyo')
        current_datetime = datetime.now(jst)
        current_time = current_datetime.time()

        print(f"current_time の型: {type(current_time)}")

        if time(0, 0) <= current_time <= time(7, 0):
            mention_message = "深夜のためメンションは行われません。"
        else:
            mention_message = f"{role.mention} " if role else ""

        new_embed = discord.Embed(title="Bumpが可能になりました!", description="</bump:947088344167366698>を使おう!")
        new_embed.set_image(url="https://cdn.discordapp.com/attachments/1141551959627813006/1141583028687220746/IMB_wXLdj1.gif")
        await timer_message.delete()
        await channel.send(mention_message, embed=new_embed)
        return

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.type == discord.ChannelType.text:
            user_role_id = 1180551674809557073

            if isinstance(message.author, discord.Member):
                user_role = discord.utils.get(message.guild.roles, id=user_role_id)

                if user_role and user_role in message.author.roles:
                    for embed in message.embeds:
                        if embed.description and "表示順をアップしたよ" in embed.description:
                            await set_timer_and_send_message(message.channel)
def setup(bot):
    bot.add_cog(BumpCog(bot))