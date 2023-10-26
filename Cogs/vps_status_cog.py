from discord import app_commands
import discord
import paramiko
import json

class VPSStatus(app_commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Shows the status of a VPS")
    async def vps_status(self, ctx: app_commands.CommandContext):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('VPS_IP', port=22, username='USERNAME', password='PASSWORD')

        # CPUモデル名を取得
        stdin, stdout, stderr = ssh.exec_command("lscpu | grep 'Model name'")
        cpu_model = stdout.read().decode().strip().split(":")[1].strip()

        # CPU使用率を取得
        stdin, stdout, stderr = ssh.exec_command("top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\\([0-9.]*\\)%* id.*/\\1/' | awk '{print 100 - $1\"%\"}'")
        cpu_usage = stdout.read().decode().strip()

        # メモリ使用量を取得
        stdin, stdout, stderr = ssh.exec_command("free -m | awk 'NR==2{printf \"%.2f%%\", $3*100/$2 }'")
        memory_usage = stdout.read().decode().strip()

        # ディスク使用量を取得
        stdin, stdout, stderr = ssh.exec_command("df -h | awk '$NF==\"/\"{printf \"%s\", $5}'")
        disk_usage = stdout.read().decode().strip()
        
        # ネットワーク使用率を取得
        stdin, stdout, stderr = ssh.exec_command("vnstat --json")
        network_data_json = stdout.read().decode().strip()
        network_data = json.loads(network_data_json)
        network_usage = network_data["interfaces"][0]["traffic"]["total"]["rx"]  # 受信量
        network_usage += network_data["interfaces"][0]["traffic"]["total"]["tx"]  # 送信量

        embed.add_field(name="Network Usage", value=f"{network_usage} KiB")

        embed = discord.Embed(title="VPS Status")
        embed.add_field(name="CPU Model", value=f"{cpu_model}")
        embed.add_field(name="CPU Usage", value=f"{cpu_usage}")
        embed.add_field(name="Memory Usage", value=f"{memory_usage}")
        embed.add_field(name="Disk Usage", value=f"{disk_usage}")
        embed.add_field(name="Network Usage", value=f"{network_usage}")

        await ctx.send(embed=embed)
        ssh.close()

def setup(bot):
    bot.add_cog(VPSStatus(bot))