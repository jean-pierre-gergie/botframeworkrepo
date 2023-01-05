import asyncio
from botbuilder.schema import InputHints
from datatypes_timex_expression import Timex
from botbuilder.core import MessageFactory,UserState
from botbuilder.dialogs import WaterfallDialog, DialogTurnResult, WaterfallStepContext
from botbuilder.dialogs.prompts import (
    DateTimePrompt,
    TextPrompt,
    PromptValidatorContext,
    PromptOptions,
    DateTimeResolution,
)
from botbuilder.dialogs import (
    WaterfallDialog,
    DialogTurnResult,
    WaterfallStepContext,
    ComponentDialog,
)
from data_models.user_profile import UserProfile
from email_validation_api.email_validator import EmailValidator
from .cancel_and_help_dialog import CancelAndHelpDialog


class UserInfoDialog(CancelAndHelpDialog):
    def __init__(self,dialog_id:str=None, user_state: UserState=None):

        super(UserInfoDialog,self).__init__(
            dialog_id or UserInfoDialog.__name__
        )
        print("__name__ = " + __name__)
        self.user_profile_accessor = user_state.create_property("UserProfile")
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(TextPrompt(TextPrompt.__name__+"1",UserInfoDialog.email_validator))
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__+"3",
                [self.name_step,
                 self.email_step,
                 self.confirm,
                 self.dismiss
                 ]
            )
        )
        self.initial_dialog_id = WaterfallDialog.__name__ + "3"

    async def name_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:

        message_text="Since you confirmed the meeting, i will need additional " \
                     "information," \
                     "Can you please enter your name?"
        prompt_options = PromptOptions(
            prompt=MessageFactory.text(message_text)
        )
        return await step_context.prompt(
            TextPrompt.__name__, prompt_options
        )
    async def email_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:

        step_context.values["name"] = step_context.result

        message_text="I will also need your email "
        prompt_options = PromptOptions(
            prompt=MessageFactory.text(message_text,input_hint=InputHints.canvas_input)
        )
        return await step_context.prompt(
            TextPrompt.__name__+"1", prompt_options
        )
    async def confirm(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        meeting_details =step_context.options

        step_context.values["email"] = step_context.result

        user_profile = step_context.options
        user_profile.name=step_context.values["name"]
        user_profile.email=step_context.values["email"]
        meeting_details.attendee_name=user_profile.name
        meeting_details.attendee_email = user_profile.email

        print(f"user information {meeting_details.attendee_name}     {meeting_details.attendee_email}")

        message_text = " i have all the information i need. thanks"
        prompt_options = PromptOptions(
            prompt=MessageFactory.text(message_text,input_hint=InputHints.accepting_input)
        )
        return await step_context.prompt(
            TextPrompt.__name__, prompt_options
        )

    async def dismiss(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        meeting_details = step_context.options
        return await step_context.end_dialog(meeting_details)


    @staticmethod
    async def email_validator(prompt_context: PromptValidatorContext) -> bool:
        validator =EmailValidator(prompt_context.recognized.value)
        task = asyncio.create_task(validator.check_validity())
        is_valid = await task

        # is_valid =True
        return is_valid


