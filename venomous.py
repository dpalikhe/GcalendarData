from __future__ import print_function

import datetime
import os.path
from time import strftime
from time import gmtime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dateutil import parser

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the total hours for each event color for the last 7 days')
        today = datetime.datetime.utcnow()
        days = datetime.timedelta(7)
        new_date = today - days
        new_date = new_date.isoformat() + 'Z'
        events_result = service.events().list(calendarId='primary', timeMin=new_date,
                                              timeMax=now, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No events found.')
            return

        # ColorID with their color name
        color_code={'1':"Lavender",'2':"Sage",'3':"Grape",'4':"Flamingo",'5':"Banana",
            '6':"Tangerine",'7':"Peacock",'8':"Graphite",'9':"Blueberry",'10':"Basil",'11':"Tomato"}
        total_hours={}
        # Prints events for the last 7 days
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            start = parser.parse(start)
            end = parser.parse(end)
            hours = end-start
            try:
                colorId=event['colorId']
            #API does not give colorId for default color
            except KeyError:
                colorId = '9'
            if hours < datetime.timedelta(days=1):
                if colorId not in total_hours.keys():
                    total_hours[colorId]=hours
                else:
                    total_hours[colorId]=hours+total_hours[colorId]
            # In case user wants to print all the events summary
            #print(hours,event['summary'], colorId)
        total_hours_event={}
        for each in total_hours.keys():
            total_hours[each]=str(total_hours[each])
            total_hours_event[color_code[each]]=total_hours[each]
        print (f"Total hours with colorID {total_hours}")
        print (f"Total hours with color name {total_hours_event}")

    except HttpError as error:
        print('An error occurred: %s' % error)
if __name__ == '__main__':
    main()
