
from datatypes_date_time import Timex

import spacy
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions,PromptValidatorContext

from botbuilder.schema import InputHints

from botbuilder.core import MessageFactory
from botbuilder.dialogs import (
    WaterfallDialog,
    DialogTurnResult,
    WaterfallStepContext,
    ComponentDialog,
)
from calendar_api.calendar_api import GoogleAPI
from helpers.timex_helper import TimexResolutionHelper
from data_models.meeting_status import Status
from botbuilder.core import MessageFactory, UserState
from botbuilder.azure import CosmosDbStorage
from dialogs.user_info_dialog import UserInfoDialog
from .cancel_and_help_dialog import CancelAndHelpDialog
from data_models.meeting_details import MeetingDetails
from helpers.spacy_helper import SpacyHelper

class SetMeetingDialog(CancelAndHelpDialog):
    def __init__(self, dialog_id: str = None,user_state: UserState=None):
        super(SetMeetingDialog, self).__init__(dialog_id or SetMeetingDialog.__name__)

        self.user_state = user_state

        self.MEETING_DETAILS = "value-meetingDetails"
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(TextPrompt("start_date_step",SetMeetingDialog.start_date_validator))
        self.add_dialog(TextPrompt("start_time_step", SetMeetingDialog.start_time_validator))
        self.add_dialog(TextPrompt("end_time_step", SetMeetingDialog.end_time_validator))
        self.add_dialog(UserInfoDialog(UserInfoDialog.__name__,self.user_state))
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [


                    self.start_date_step,
                    self.start_time_step,
                    self.end_time_step,
                    self.meeting_resolver_step,
                    self.intermediate_step,
                    self.user_info_step,
                    self.final_step,
                ],
            )
        )

        self.initial_dialog_id = WaterfallDialog.__name__

    async def start_date_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        meeting_details= step_context.options
        if meeting_details.start_date is  None:


            message_text = "When would you like to set the meeting? give me a day or a date"
            reprompt_msg_text = "Please choose a date or a day during the weekdays"
            reprompt_msg = MessageFactory.text(
                reprompt_msg_text, reprompt_msg_text, InputHints.accepting_input
            )
            prompt_options = PromptOptions(
                prompt=MessageFactory.text(message_text,input_hint=InputHints.accepting_input)
                ,retry_prompt=reprompt_msg
            )
            return await step_context.prompt(
                "start_date_step", prompt_options
            )

        return  await step_context.next(meeting_details.start_date)

    async def start_time_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:

        meeting_details = step_context.options
        #capture if a start date was given
        meeting_details.start_date = step_context.result




        #check if  there is a start time
        if meeting_details.start_time is None:

            message_text = "when would you like to start the meeting"
            reprompt_msg_text = "Please choose starting hour between 8am and 12 am"
            reprompt_msg = MessageFactory.text(
                reprompt_msg_text, reprompt_msg_text, InputHints.accepting_input
            )
            prompt_options = PromptOptions(
                prompt=MessageFactory.text(message_text,input_hint=InputHints.accepting_input),
                retry_prompt=reprompt_msg
            )
            return await step_context.prompt(
                "start_time_step", prompt_options
            )
        return await step_context.next(meeting_details.start_time)


    async def end_time_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:

        meeting_details = step_context.options

        #capture the result start_time_step
        meeting_details.start_time=step_context.result

        if meeting_details.end_time is None:
            message_text = "when would you like to end the meeting"
            reprompt_msg_text = "Please choose a starting hour between 8am and 12 am"
            reprompt_msg = MessageFactory.text(
                reprompt_msg_text, reprompt_msg_text, InputHints.expecting_input
            )
            prompt_options = PromptOptions(
                prompt=MessageFactory.text(message_text,input_hint=InputHints.accepting_input),
                retry_prompt=reprompt_msg
            )
            return await step_context.prompt(
                "end_time_step", prompt_options
            )
        return await step_context.next(meeting_details.end_time)



    async def meeting_resolver_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        here we will call the google api.
        :param step_context:
        :return DialogTurnResult:
        """
        meeting_details = step_context.options

        # Capture the results of the previous step
        meeting_details.end_time = step_context.result
        # message_text = (
        #
        #     f"you requested to set a meeting that starts at {meeting_details.start_time} the day:  "
        #     f"{meeting_details.start_date} that ends at {meeting_details.end_time} please comfirm..."
        # )
        #
        # prompt_options = PromptOptions(
        # prompt=MessageFactory.text(message_text,input_hint=InputHints.accepting_input)
        #  )

        start= SpacyHelper.get_time_text(meeting_details.start_time)
        end=SpacyHelper.get_time_text(meeting_details.end_time)



        # this the core of this dialog
        # here we are trying to use timex resolution to extract all the entities needed from a string
        # the meeting string will allow the the timex helper to extract all the entities needed

        meeting_string=(f"from {start} to {end}  {meeting_details.start_date} ")
        print("meeting string")
        print(meeting_string)

        meeting_details.meeting_details_str=meeting_string

        timex_resolution = TimexResolutionHelper(meeting_details)
        try:
            meeting_details, status = timex_resolution.process()

            print(str(meeting_details.start_dateTime_timex) + "   " + str(meeting_details.end_dateTime_timex))
            print(status)
        except:
            status = Status.AMBIGUOUS

        if status == Status.BUSY:
            busy = timex_resolution.request_availability(meeting_details.start_date)
            message_text = f"Mr. Jean-Pierre have another meeting at this date-time. " \
                           f"Could you please choose another appointment from 8am to 12am during week days?"
            message_text += " keep in mind that "+busy

            prompt_options = PromptOptions(
                prompt=MessageFactory.text(message_text,input_hint=InputHints.accepting_input)
            )
            return await step_context.prompt(
                TextPrompt.__name__, prompt_options
            )
        elif status == Status.OUT_OF_WORKING_HOURS:
            message_text = f"Mr. Jean-Pierre isn't available at this time" \
                           f" meeting could be set from 8 to 12 during week days"
            prompt_options = PromptOptions(
                prompt=MessageFactory.text(message_text,input_hint=InputHints.accepting_input)
            )
            return await step_context.prompt(
                TextPrompt.__name__, prompt_options
            )
        elif status == Status.AMBIGUOUS:
            message_text = f"the date you just entered is very ambiguous and i couldn't resolve it alone" \
                           f"could you please enter a date using the following format from HH to HH the DD"
            prompt_options = PromptOptions(
                prompt=MessageFactory.text(message_text,input_hint=InputHints.accepting_input)
            )
            return await step_context.prompt(
                TextPrompt.__name__, prompt_options
            )
        elif status == Status.FAILED:
            message_text = f"Could you please choose an other appointment from 8am to 12am during week days?"
            prompt_options = PromptOptions(
                prompt=MessageFactory.text(message_text,input_hint=InputHints.accepting_input)
            )
            return await step_context.prompt(
                TextPrompt.__name__, prompt_options
            )
        elif status == Status.SUCCESS:

            #### add nlp
            message_text = f"mr. jean-pierr is free on  {meeting_details.start_date} from {meeting_details.start_time}" \
                           f" to {meeting_details.end_time}. i am going to book the meeting.would you like to confirm? if you would like to cancel say cancel"
            prompt_options = PromptOptions(
                prompt=MessageFactory.text(message_text,input_hint=InputHints.accepting_input)
            )
            return await step_context.prompt(
                TextPrompt.__name__, prompt_options
            )

    async def intermediate_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        meeting_details = step_context.options
        if meeting_details.status == Status.SUCCESS:
            return await step_context.next(meeting_details)
        else:
            meeting_details_reset =MeetingDetails()
            return await step_context.replace_dialog(SetMeetingDialog.__name__, options=meeting_details_reset)

    async def user_info_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        meeting_details = step_context.options
        print(f"set meeting dialog meeting status {meeting_details.status}")
        if meeting_details.status == Status.SUCCESS:

            return await step_context.begin_dialog(UserInfoDialog.__name__,options=meeting_details)
        else:

            message_text = "i didn't set up a meeting"

            prompt_options = PromptOptions(
                prompt=MessageFactory.text(message_text)
            )
            return await step_context.prompt(
                TextPrompt.__name__ + "1", prompt_options
            )





    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        Complete the interaction and end the dialog.
        :param step_context:
        :return DialogTurnResult:
        """

        meeting_details = step_context.options
        if meeting_details.status == Status.SUCCESS:
            timex_resolution = TimexResolutionHelper(meeting_details)
            timex_resolution.set_the_event_api(meeting_details)

        print("we are sending the infos back to the main dialog for cosmos db")
        print(f"we have meeting: {meeting_details.status}  {meeting_details.end_dateTime_timex}"
              f"{meeting_details.attendee_name}  {meeting_details.attendee_email}")
        print("before this step we could add an additional one to collect user information")
        return await step_context.end_dialog(meeting_details)

    @staticmethod
    async def start_date_validator(prompt_context: PromptValidatorContext) -> bool:
        validator = TimexResolutionHelper()
        is_valid=validator.start_date_validator(prompt_context.recognized.value)
        #todo add reprompt

        return is_valid

    @staticmethod
    async def start_time_validator(prompt_context: PromptValidatorContext) -> bool:
        validator = TimexResolutionHelper()
        is_valid = validator.start_time_validator(prompt_context.recognized.value)
        # todo add reprompt

        return is_valid

    @staticmethod
    async def end_time_validator(prompt_context: PromptValidatorContext) -> bool:
        validator = TimexResolutionHelper()
        is_valid = validator.end_time_validator(prompt_context.recognized.value)
        # todo add reprompt

        return is_valid