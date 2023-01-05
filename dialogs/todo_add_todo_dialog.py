
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions
from botbuilder.schema import InputHints

from botbuilder.core import MessageFactory
from botbuilder.dialogs import (
    WaterfallDialog,
    DialogTurnResult,
    WaterfallStepContext,
    ComponentDialog,
)

from botbuilder.core import MessageFactory, UserState
from .cancel_and_help_dialog import CancelAndHelpDialog
from notion_api.notion_api_helper import Notion
import asyncio

class AddToDoDialog(CancelAndHelpDialog):
    def __init__(self,dialog_id:str = None):
        super(AddToDoDialog, self).__init__(dialog_id or AddToDoDialog.__name__)
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__+"4",
                [
                    self.get_content_step,
                    self.confirm,
                    self.final_step,
                ],
            )
        )
        self.initial_dialog_id = WaterfallDialog.__name__+"4"

    async def get_content_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        task_content=step_context.options

        if task_content.content is None:
            message_text = "I understand you want to add a task. what should be the title of this task?"
            prompt_options = PromptOptions(
                prompt=MessageFactory.text(message_text,input_hint=InputHints.accepting_input)
            )
            return await step_context.prompt(
                TextPrompt.__name__, prompt_options
            )

        return await step_context.next(task_content.content)

    async def confirm(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        task_content =step_context.options
        task_content.content = step_context.result
        print("here we will call notion API")
        ### add notion api to add to do list
        message_text = "I will remind Mr. Jean-Pierre to "+task_content.content + ". is it ok?"
        prompt_options = PromptOptions(
            prompt=MessageFactory.text(message_text,input_hint=InputHints.accepting_input)
        )
        return await step_context.prompt(
            TextPrompt.__name__, prompt_options
        )

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        print("here we will call notion API")
        task_content = step_context.options
        content=str(task_content.content)
        api=Notion()
        await api.create_task(content)

        return await step_context.end_dialog()
