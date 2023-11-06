import os
import discord
from discord.ext import tasks, commands
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import datetime
from dotenv import load_dotenv

load_dotenv()

class CalendarCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.service = self.setup_google_calendar_api()
        self.check_events.start()

    def setup_google_calendar_api(self):
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        service = build('calendar', 'v3', credentials=creds)
        return service

    @commands.command(name='add-event')
    async def add_event(self, ctx, summary, description, start_time, end_time):
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': 'Asia/Tokyo',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'Asia/Tokyo',
            },
        }
        event = self.service.events().insert(calendarId='primary', body=event).execute()
        await ctx.send(f"イベントを作成しました: {event.get('htmlLink')}")

    @tasks.loop(minutes=1)
    async def check_events(self):
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = self.service.events().list(calendarId='primary', timeMin=now,
                                                   maxResults=10, singleEvents=True,
                                                   orderBy='startTime').execute()
        events = events_result.get('items', [])
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            start_dt = datetime.datetime.fromisoformat(start)
            if start_dt < datetime.datetime.utcnow() + datetime.timedelta(minutes=1):
                channel_id = int(os.getenv('GOOGLE_CALENDAR_CHANNEL_ID'))
                channel = self.bot.get_channel(channel_id)
                message = f"リマインダー: {event['summary']} は {start} に始まります。"
                await channel.send(message)

    @check_events.before_loop
    async def before_check_events(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(CalendarCog(bot))