

class EventDetails:
    """JPG
        needed for deleting an event
        for future implementation we could add a date so we could delete a meeting at a specific day

    """
    def __init__(self,
                 summary:str=None,
                 id:str=None,
                 attendee:str=None):
        self.summary= summary
        self.id =id
        self.attendee=attendee