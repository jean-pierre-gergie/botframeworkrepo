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




class DeleteMeetingDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None):
        super(DeleteMeetingDialog, self).__init__(dialog_id or DeleteMeetingDialog.__name__)

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__+"6",
                [

                    self.person_name_step,
                    self.intermediate_step,
                    self.final_step,


                ],
            )
        )
        self.initial_dialog_id = WaterfallDialog.__name__+"6"

    async def person_name_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:

        event_details=step_context.options
        if event_details.attendee is None:
            message_text = "what is the name of the person you want to cancel the meeting with"
            prompt_options = PromptOptions(
                prompt=MessageFactory.text(message_text,input_hint=InputHints.accepting_input)
            )
            return await step_context.prompt(
                TextPrompt.__name__, prompt_options
            )
        return await step_context.next(event_details.attendee)

    async def intermediate_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        event_details = step_context.options
        event_details.attendee = step_context.result

        timex =TimexResolutionHelper()
        timex.delete_event(event_details.attendee)
        #todo return the response of the api call to here for now valid is hard coded
        valid =True
        if valid:
            message_text = "I deleted the meeting with "+str(event_details.attendee)
            prompt_options = PromptOptions(
                prompt=MessageFactory.text(message_text,input_hint=InputHints.accepting_input)
            )
            return await step_context.prompt(
                TextPrompt.__name__, prompt_options
            )

        else:
            message_text = "I failed to delete the meeting"
            prompt_options = PromptOptions(
                prompt=MessageFactory.text(message_text,input_hint=InputHints.accepting_input)
            )
            return await step_context.prompt(
                TextPrompt.__name__, prompt_options
            )

    async def final_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        return await step_context.end_dialog()







