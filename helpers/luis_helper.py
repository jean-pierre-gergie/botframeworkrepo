# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from enum import Enum
from typing import Dict
from botbuilder.ai.luis import LuisRecognizer
from botbuilder.core import IntentScore, TopIntent, TurnContext

from data_models.meeting_details import MeetingDetails
from data_models.task_content import TaskContent
from data_models.event_details import EventDetails

import json

class Intent(Enum):
    CALENDARCREATECALENDARENTRY = "Calendar_CreateCalendarEntry"
    TODOADDTODO = "ToDo_AddToDo"
    TODOSHOWTODO ="ToDo_ShowToDo"
    CALENDARCHECKAVAILABILITY="Calendar_CheckAvailability"
    CALENDARDELETECALENDARENTRY="Calendar_DeleteCalendarEntry"
    CANCEL = "Cancel"
    NONE_INTENT = "NoneIntent"


def top_intent(intents: Dict[Intent, dict]) -> TopIntent:
    max_intent = Intent.NONE_INTENT
    max_value = 0.0

    for intent, value in intents:
        intent_score = IntentScore(value)
        if intent_score.score > max_value:
            max_intent, max_value = intent, intent_score.score

    return TopIntent(max_intent, max_value)


class LuisHelper:
    @staticmethod
    async def execute_luis_query(
        luis_recognizer: LuisRecognizer, turn_context: TurnContext
    ) -> (Intent, object):
        """
        Returns an object with preformatted LUIS results for the bot's dialogs to consume.
        """
        result = None
        intent = None

        try:
            recognizer_result = await luis_recognizer.recognize(turn_context)

            intent = LuisRecognizer.top_intent(recognizer_result)

            print(intent)
            print("check for each entity")
            print(recognizer_result)

            if intent == Intent.CALENDARCREATECALENDARENTRY.value:
                result = MeetingDetails()



                ###### get the end time
                end_time_entities = recognizer_result.entities.get("$instance", {}).get(
                    "Calendar_EndTime", []
                )
                if len(end_time_entities) > 0:
                    result.end_time= end_time_entities[0]['text'].capitalize()
                    print("result.end_time "+result.end_time)



                ###### get the start time
                start_time_entities = recognizer_result.entities.get("$instance", {}).get(
                    "Calendar_StartTime", []
                )
                if len(start_time_entities) > 0:
                    result.start_time = start_time_entities[0]["text"].capitalize()
                    print("result.start_time " + result.start_time)

                ###### get the start date
                start_date_entities = recognizer_result.entities.get("$instance", {}).get(
                    "Calendar_StartDate", []
                )
                if len(start_date_entities) > 0:
                    result.start_date = start_date_entities[0]["text"].capitalize()
                    print("result.start_date " + result.start_date)

            if intent == Intent.TODOSHOWTODO.value:
                pass

            if intent == Intent.TODOADDTODO.value:
                # print("luis helper add to do ")
                result=TaskContent()

                _content =recognizer_result.entities.get("$instance", {}).get(
                    "ToDo_TaskContent", []
                )
                if len(_content)>0:
                    result.content=_content[0]["text"].capitalize()
                    print("task content  "+ result.content)

            if intent == Intent.CALENDARCHECKAVAILABILITY.value:
                result = MeetingDetails()

                start_date_entities = recognizer_result.entities.get("$instance", {}).get(
                    "Calendar_StartDate", []
                )
                if len(start_date_entities) > 0:
                    result.start_date = start_date_entities[0]["text"].capitalize()
                    print("result.start_date " + result.start_date)

            if intent == Intent.CALENDARDELETECALENDARENTRY.value:
                result=EventDetails()
                person_name=recognizer_result.entities.get("$instance", {}).get(
                    "personName", []
                )
                if person_name:
                    result.attendee =person_name[0]["text"].capitalize()
                    print("meeting attendee name"+result)






        except Exception as exception:
            print(exception)
        print("type of luis results")
        print(type(result))
        return intent, result
