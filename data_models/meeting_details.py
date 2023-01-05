from .meeting_status import Status
from .user_profile import UserProfile


class MeetingDetails:
    """JPG
        provides all the information needed to set a meeting

    """
    def __init__(
            self,
            destination_calendar: str = None,
            end_date: str = None,
            end_time: str = None,
            message: str = None,
            start_date: str = None,
            start_time: str = None,
            subject: str = None,
            meeting_details_str: str = None,
            start_dateTime_timex: str = None,
            end_dateTime_timex: str = None,
            attendee_name: str= None,
            attendee_email: str=None,
            status: Status = Status.FAILED


    ):
        self.destination_calendar = destination_calendar
        self.end_date = end_date
        self.end_time = end_time
        self.message = message
        self.start_date = start_date
        self.start_time = start_time
        self.subject = subject
        self.meeting_details_str = meeting_details_str
        self.start_dateTime_timex = start_dateTime_timex
        self.end_dateTime_timex = end_dateTime_timex
        self.attendee_name = attendee_name
        self.attendee_email= attendee_email
        self.status = status

