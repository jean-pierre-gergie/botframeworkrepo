from __future__ import print_function
import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from data_models.meeting_details import MeetingDetails
from helpers.google_api_helper import GoogleAPIHelper


class GoogleAPI:
    def __init__(self, meeting_details: MeetingDetails = None, candidates: [str] = None):
        self.creds = None
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
        self.service = None
        self.now = datetime.datetime.utcnow().isoformat() + 'Z'
        self.meeting_details = meeting_details
        self.events_result = None
        self.events = None
        self.candidates = candidates
        self.check_for_credentials()
    """ JPG 
        the constructor can be initiated using the  meetingdeatils so it can access the google calendar
        
    """
    def check_for_credentials(self):
        print(os.path.exists("calendar_api/credentials.json"))

        if os.path.exists("calendar_api/token.json"):
            self.creds = Credentials.from_authorized_user_file("calendar_api/token.json", self.SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "calendar_api/credentials.json", self.SCOPES)
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
            with open("calendar_api/token.json", 'w') as token:
                token.write(self.creds.to_json())
        try:
            self.service = build('calendar', 'v3', credentials=self.creds)
            self.now = datetime.datetime.utcnow().isoformat() + 'Z'
            # print("Google service is now built")
        except:
            pass
        """ JPG 
            this will provide a token valid for 7 days because it will provide a development token 

        """

    def upcoming_events(self):
        try:
            ### check for events....
            self.events_result = self.service.events().list(calendarId='primary', timeMin=self.now,
                                                            maxResults=10, singleEvents=True,
                                                            orderBy='startTime').execute()

            self.events = self.events_result.get('items', [])
            # print("self.events")
            # print(self.events)
            if not self.events:
                print('No upcoming events found.')
                return
            for event in self.events:
                # print (event)
                start = event['start'].get('dateTime')
                id = event["id"]
                print(id, start, event['summary'])
            return self.events




        except HttpError as error:
            print('An error occurred: %s' % error)

    """ JPG 
        list all the upcoming event starting the current day 

    """
    def set_an_event(self):
        try:

            google_api_helper = GoogleAPIHelper(meeting_details=self.meeting_details)
            event_body = google_api_helper.create_event_body()
            event_result = self.service.events().insert(calendarId='primary', body=event_body).execute()
            print('Event created: %s' % (event_result.get('htmlLink')))

        except HttpError as error:
            print('An error occurred: %s' % error)

    """ JPG 
            add an event to google calendar 

    """
    def check_availability(self):
        print("calling free/busy api")
        try:
            timeMin = self.candidates[0] + ':00:00+02:00'
            timeMax = self.candidates[1] + ':00:00+02:00'

            body = {
                "timeMin": timeMin,
                "timeMax": timeMax,
                "timeZone": "UTC+2",

                "items": [
                    {
                        "id": "primary"
                    }
                ]
            }
            event_result = self.service.freebusy().query(body=body).execute()
            print("busy at:")
            print(event_result['calendars'].get('primary').get('busy'))

            if event_result['calendars'].get('primary').get('busy') != []:
                is_available = False
            else:
                is_available = True

            return is_available, event_result['calendars'].get('primary').get('busy')
        except:
            return False, []

    """ JPG 
        
        Make use of Free/Busy method provided by th google API

    """


    def delete_event(self,event_id:str):
        self.service.events().delete(calendarId='primary', eventId=event_id).execute()

    """ JPG 
        
        delete an event from the google calendar

    """