import re

from recognizers_date_time import recognize_datetime, Culture
from data_models.meeting_details import MeetingDetails
from data_models.meeting_status import Status
from datatypes_timex_expression import TimexRangeResolver, TimexCreator, Constants,Timex
from calendar_api.calendar_api import GoogleAPI
import datetime
import jellyfish



class TimexResolutionHelper:
    def __init__(self, meeting_details: MeetingDetails=None):
        self.meeting_details = meeting_details
        self.status = Status.FAILED


    def delete_event(self,person_name:str):

        api=GoogleAPI()

        events = api.upcoming_events()
        confidence = 10
        title = "Meeting with " + person_name
        for event in events:

            if jellyfish.levenshtein_distance(event['summary'],title)<confidence:
                confidence=jellyfish.levenshtein_distance(event['summary'],title)
                event_id = event['id']
        api.delete_event(event_id)



    def request_availability(self,start_date:str=None):

        if start_date is None:
            start_date=(datetime.datetime.now()).strftime("%A")

        start_timex, end_timex, type = self.get_timex_expressions(start_date)
        candidates=[]
        if type == 'date':
            candidates.append(start_timex)
            candidates.append(end_timex)
            is_available,busy = self.check_google_calendar_availability(candidates)

            if not is_available:

                prompt=f'On {start_date}, mr. Jean-Pierre is busy'
                for range in busy:
                    start = range['start']
                    end =range['end']

                    start=datetime.datetime.fromisoformat(start)
                    end =datetime.datetime.fromisoformat(end)


                    prompt +=' from ' + start.strftime("%H:%M") +" to " + end.strftime("%H:%M")+', '

                print(prompt)
                return prompt
            if is_available:
                prompt = f' mr. Jean-Pierre is free from 8 to 12 on {start_date}'
                print(prompt)
                return prompt


    def process(self):


        start_timex,end_timex,type = self.get_timex_expressions(self.meeting_details.meeting_details_str)



        print("Top")
        print(start_timex)
        print(end_timex)
        print(type)
        if start_timex is not None and end_timex is not None:
            # check availibility on google
            candidates=[]
            candidates.append(start_timex)
            candidates.append(end_timex)
            is_available,busy = self.check_google_calendar_availability(candidates)

            if is_available:
                self.meeting_details.start_dateTime_timex = start_timex
                self.meeting_details.end_dateTime_timex = end_timex
                # self.set_the_event_api( self.meeting_details)
                self.status = Status.SUCCESS
                self.meeting_details.status = Status.SUCCESS
            else:
                self.meeting_details.start_dateTime_timex = None
                self.meeting_details.end_dateTime_timex = None
                self.status = Status.BUSY  # not available
                print("busy at this time")

        elif start_timex is None or end_timex is None:
            self.meeting_details.start_dateTime_timex = None
            self.meeting_details.end_dateTime_timex = None
            self.status = Status.FAILED

        return self.meeting_details, self.status

    def get_timex_expressions(self, details_str: str) -> bool:
        print()
        results = recognize_datetime(details_str, Culture.English)
        distinct_expressions = []
        type = ''
        start_values = []
        end_values = []

        for result in results:
            print(result.resolution)
            for value in result.resolution["values"]:
                if value['type'] == 'datetimerange':
                    print("datetime range")
                    type = 'datetimerange'
                elif value['type'] == 'timerange':
                    print("time range")
                    type = 'timerange'
                elif value['type'] == 'time':
                    print('time')
                    type = 'time'
                elif value['type'] == 'date':
                    print('date')
                    type = 'date'

                if "timex" in value:
                    if value["timex"] not in distinct_expressions:
                        distinct_expressions.append(value["timex"])
        print(distinct_expressions)

        distinct_timex_expressions = []
        # remove the ()
        for expression in distinct_expressions:
            values = str(expression).split(",")
            for i in range(len(values)):
                values[i] = re.sub('[()]', '', values[i])
            distinct_timex_expressions.append(values)

        print('distinct_timex_expressions: ')
        print(distinct_timex_expressions)

        # split into start time and end time
        if type == 'timerange' or type == 'datetimerange':
            # extract starting and ending time

            for expression in distinct_timex_expressions:
                start_values.append(expression[0])
                end_values.append(expression[1])
            print("start values")
            print(start_values)
            print("end values")
            print(end_values)

            # apply constraint
            if len(start_values) > 1:
                start_values = self.apply_constraint(start_values)
                print(start_values)
            if len(end_values) > 1:
                end_values = self.apply_constraint(end_values)
                print(end_values)

            return start_values, end_values, type

        if type == 'date':
            print("type = date")
            for expression in distinct_timex_expressions:
                start_values.append(expression[0])
            print("start values")
            print(start_values)
            if len(start_values) == 1:
                start_values = self.apply_constraint(start_values)
                end_values = start_values + ',PT5H'
                end_values = Timex(end_values).timex_value()
                end_values = end_values + 'T13'
                print(" availability timex:")
                print(start_values)
                print(end_values)
            return start_values, end_values, type

    def recognize_date_time(self,details_str: str):
        results = recognize_datetime(
            details_str, Culture.English
        )
        distinct_timex_expressions = []

        for result in results:
            for value in result.resolution["values"]:
                if "timex" in value:
                    if value["timex"] not in distinct_timex_expressions:
                        distinct_timex_expressions.append(value["timex"])
        # print(distinct_timex_expressions)
        return distinct_timex_expressions, len(distinct_timex_expressions) > 1

    def apply_constraint(self, candidates: [str]):
        resolutions = TimexRangeResolver.evaluate(
            candidates,
            [TimexCreator.week_from_today(), TimexCreator.WORKINGHOUR],
        )
        for resolution in resolutions:
            return resolution.timex_value()

    def check_google_calendar_availability(self, candidates: [str]):
        api = GoogleAPI(candidates=candidates)
        return api.check_availability()

    def set_the_event_api(self,meeting_details:MeetingDetails):
        api = GoogleAPI(meeting_details=meeting_details)
        api.set_an_event()
        print("event is now present on calendar")

    def start_date_validator(self,text:str):
        print("validating date")
        try:
            results,_ =self.recognize_date_time(text)
            print(results)
            reference_date = datetime.datetime.now()
            day =Timex(results[0]).to_natural_language(reference_date)
            day=day.upper()

            if day in {
            'MONDAY',
            'TUESDAY',
            'WEDNESDAY',
            'THURSDAY',
            'FRIDAY'}:
                print("week day")
                return True
            elif day in{
                'SATURDAY',
                'SUNDAY'
            }:
                return False

            else:


                split = re.split("-", str(results[0]))
                day = datetime.date(2022, int(split[1]), int(split[2]))
                print(day)
                if day.weekday() < 5:
                    print("Date is Weekday")
                    return True
                else:  # 5 Sat, 6 Sun
                    print("Date is Weekend")
                    return False
        except:
            return False

    def start_time_validator(self,text:str):
        results, _ = self.recognize_date_time(text+"o'clock")
        # print(results)
        resolutions = TimexRangeResolver.evaluate(
            results,
            [ TimexCreator.MORNING,],
        )
        for resolution in resolutions:
            print(resolution.timex_value())
        if len(resolutions)==1:
            # print("True")
            return True
        else:
            # print("false")
            return False

    def end_time_validator(self, text: str):
        results, _ = self.recognize_date_time(text + "o'clock")
        print("endtime")
        print(results)
        resolutions = TimexRangeResolver.evaluate(
            results,
            [TimexCreator.WORKINGHOUR, ],
        )
        for resolution in resolutions:
            print("endtime resolution")
            print(resolution.timex_value())
        print("lenght of resolution end time")
        print(len(resolutions))
        if len(resolutions) == 1:
            print("True")
            return True
        else:
            print("false")
            return False

