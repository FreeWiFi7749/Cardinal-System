from discord import app_commands
from discord.ext import commands
import discord
import paramiko
import json
import os
from dotenv import load_dotenv

load_dotenv()
VPS_IP = os.getenv('VPS_IP')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')

class VPSStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(description="Shows the status of a VPS")
    async def status(self, ctx):
        await ctx.send("情報を取得中です...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(VPS_IP, port=22, username=USERNAME, password=PASSWORD)

        # CPUモデル名を取得
        stdin, stdout, stderr = ssh.exec_command("lscpu | grep 'Model name'")
        cpu_model = stdout.read().decode().strip().split(":")[1].strip()

        # CPU使用率を取得
        stdin, stdout, stderr = ssh.exec_command("top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\\([0-9.]*\\)%* id.*/\\1/' | awk '{print 100 - $1\"%\"}'")
        cpu_usage = stdout.read().decode().strip()

        # メモリ使用量と全体のメモリ容量を取得
        stdin, stdout, stderr = ssh.exec_command("free -m | awk 'NR==2{printf \"Used: %.2f%% (%dMB of %dMB)\", $3*100/$2, $3, $2 }'")
        memory_info = stdout.read().decode().strip()



        # ディスク使用量を取得
        stdin, stdout, stderr = ssh.exec_command("df -h | awk '$NF==\"/\"{printf \"Used: %s (%s of %s)\", $5, $3, $2}'")
        disk_info = stdout.read().decode().strip()
        
        # ネットワーク使用率を取得
        stdin, stdout, stderr = ssh.exec_command("vnstat --json")
        network_data_json = stdout.read().decode().strip()
        network_data = json.loads(network_data_json)
        network_usage = network_data["interfaces"][0]["traffic"]["total"]["rx"]  # 受信量
        network_usage += network_data["interfaces"][0]["traffic"]["total"]["tx"]  # 送信量

        embed = discord.Embed(title="VPS Status")
        embed.add_field(name="CPU Model", value=f"{cpu_model}")
        embed.add_field(name="CPU Usage", value=f"{cpu_usage}")
        embed.add_field(name="Memory Info", value=f"{memory_info}")
        embed.add_field(name="Disk Info", value=f"{disk_info}")
        embed.add_field(name="Network Usage", value=f"{network_usage} KiB")

        await ctx.send(embed=embed)
        ssh.close()

async def setup(bot: commands.Bot):
    bot.add_cog(VPSStatus(bot))