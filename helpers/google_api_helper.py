from data_models.meeting_details import MeetingDetails




class GoogleAPIHelper:
    def __init__(self, meeting_details: MeetingDetails = None, candidate: [str] = None):
        self.meeting_details = meeting_details
        self.start_datetime = self.meeting_details.start_dateTime_timex +':00:00+02:00'
        self.end_datetime = self.meeting_details.end_dateTime_timex +':00:00+02:00'
        self.attendee_name = self.meeting_details.attendee_name
        self.attendee_email = self.meeting_details.attendee_email
        self.summary = "Meeting with " + self.attendee_name





    def create_event_body(self):
        event_body = {
            'summary': self.summary,
            'location': 'HEIA',
            'description': 'Meeting ',
            'start': {
                'dateTime': self.start_datetime,
                'timeZone': 'Europe/Zurich',
            },
            'end': {
                'dateTime': self.end_datetime,
                'timeZone': 'Europe/Zurich',
            },
            'attendees': [
                {'email': self.attendee_email},
            ],

        }
        return event_body
