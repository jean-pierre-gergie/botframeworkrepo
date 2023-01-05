from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)

from botbuilder.ai.luis import LuisApplication, LuisPredictionOptions, LuisRecognizer
from helpers.luis_helper import LuisHelper, Intent
from botbuilder.core import MessageFactory, UserState
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.core import MessageFactory, TurnContext
from botbuilder.schema import ActivityTypes, InputHints
from dialogs.set_meeting_dialog import SetMeetingDialog
from botbuilder.azure import CosmosDbStorage
from data_models.meeting_details import MeetingDetails
from botbuilder.ai.qna import QnAMaker,QnAMakerEndpoint,QnAMakerOptions
from dialogs.todo_add_todo_dialog import AddToDoDialog
from dialogs.delete_meeting_dialog import DeleteMeetingDialog
from notion_api.notion_api_helper import Notion
from helpers.timex_helper import TimexResolutionHelper

from gpt3_api.gpt3_api_helper import GPT3

class MainDialog(ComponentDialog):
    def __init__(
            self, user_state: UserState, cosmos_db:CosmosDbStorage
    ):
        super(MainDialog, self).__init__(MainDialog.__name__)


        # luis_calendar configuration

        luis_app = LuisApplication("20424826-14a4-4eb0-adc9-89176d0454b6",
                                   "fba24928d2a7467ea532a030cef94f04",
                                   "https://avatarbotjpg3-authoring.cognitiveservices.azure.com/")
        luis_option = LuisPredictionOptions(include_all_intents=True, include_instance_data=True)
        self.LuisReg = LuisRecognizer(luis_app, luis_option, True)
        #QnA configuration
#
        self.qna_endpoint = QnAMakerEndpoint(
            '9066f654-d452-4797-8d64-4d08f5800702',
            '2d7ec4e1-9fda-4f8a-ac14-a83b223a5519',
            'https://qnaavatarbot.azurewebsites.net/qnamaker',

        )
        # we increased the score threshold so the  GPT3 API will be called more frequently

        self.qna_options=QnAMakerOptions(score_threshold=0.80)


        self.qna_maker = QnAMaker(self.qna_endpoint,options=self.qna_options)

        self.cosmos_db= cosmos_db

        self.user_state = user_state

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(SetMeetingDialog(SetMeetingDialog.__name__,self.user_state))
        self.add_dialog(AddToDoDialog(AddToDoDialog.__name__))
        self.add_dialog(DeleteMeetingDialog(DeleteMeetingDialog.__name__))
        self.add_dialog(
            WaterfallDialog(
                "WFDialog",
                [self.initial_step,
                 self.intent_detection_step,
                 self.final_step]
            )
        )


        self.initial_dialog_id = "WFDialog"

    async def initial_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:

        # store_item = await self.cosmos_db.read(["user"])
        # if "user" not in store_item:
        #     db_meeting_details = MeetingDetails()
        # else:
        #     db_meeting_details = store_item["user"]

        # prompt_message = MessageFactory.text(
        #                 f"Hello "
        #                 f"Mr. Jean-Pierre isn't available at the moment."
        #                 f"I am Sasha his assistant. How can I help you?"
        #             )
        return await step_context.next([])

    async def intent_detection_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:

        intent, luis_result = await LuisHelper.execute_luis_query(
            self.LuisReg, step_context.context
        )
        print(intent)
        if intent ==Intent.TODOSHOWTODO.value:
            print("showing to do list ")
            api =Notion()
            await api.query_db()
            str = await  api.get_string()
            message_text = "I will list the To DO list of Mr. Jean-Pierre: "+ str
            prompt_options = PromptOptions(
                prompt=MessageFactory.text(message_text,input_hint=InputHints.done),
            )
            return await step_context.prompt(
                TextPrompt.__name__, prompt_options
            )

            # create notion api here or enter a dialog

        elif intent == Intent.TODOADDTODO.value :
            print("entering add to do dialog")
            return await step_context.begin_dialog(AddToDoDialog.__name__,options=luis_result)


        elif intent == Intent.CALENDARCREATECALENDARENTRY.value and luis_result:
            print("entering calendar dialog")
            return await step_context.begin_dialog(SetMeetingDialog.__name__,options=luis_result)

        elif intent == Intent.CALENDARCHECKAVAILABILITY.value and luis_result:
            timex =TimexResolutionHelper()
            message_text=timex.request_availability(luis_result.start_date)
            prompt_options = PromptOptions(
                prompt=MessageFactory.text(message_text,input_hint=InputHints.accepting_input)
            )
            return await step_context.prompt(
                TextPrompt.__name__, prompt_options
            )
        elif intent == Intent.CALENDARDELETECALENDARENTRY.value:
            print("entering delete meeting dialog")
            return await step_context.begin_dialog(DeleteMeetingDialog.__name__,options=luis_result)
            #todo make a dialog to capture the name of the person and delete the meeting
        else:
            print("entering QnA")
            response = await self.qna_maker.get_answers(step_context.context)

            if response and len(response) > 0 :
                prompt_options = PromptOptions(
                    prompt=MessageFactory.text(response[0].answer,input_hint=InputHints.accepting_input)
                )
                return await step_context.prompt(
                    TextPrompt.__name__, prompt_options
                )
            else:
                try:
                    print("calling gpt3")
                    # print(step_context.context)
                    # print(step_context.context.activity.text)

                    activity=step_context.context.activity.text

                    message_text = await GPT3.gpt3(activity)

                    prompt_options = PromptOptions(
                        prompt=MessageFactory.text(message_text)
                    )
                    return await step_context.prompt(
                        TextPrompt.__name__, prompt_options
                    )
                    # message_text = "I have no response"
                    #
                    # prompt_options = PromptOptions(
                    #     prompt=MessageFactory.text(message_text,input_hint=InputHints.done)
                    # )
                    # return await step_context.prompt(
                    #     TextPrompt.__name__, prompt_options
                    # )
                except:
                    message_text = "I have no response"

                    prompt_options = PromptOptions(
                        prompt=MessageFactory.text(message_text,input_hint=InputHints.done)
                    )
                    return await step_context.prompt(
                        TextPrompt.__name__, prompt_options
                    )


    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:

        # if step_context.result is not None:
        #     meeting_details = step_context.result
        #     msg_txt = f" Please Confirm, I have set a meeting that starts at {meeting_details.start_time} the day:  "
        #     f"{meeting_details.start_date} that ends at {meeting_details.end_time}"
        #     message = MessageFactory.text(msg_txt, msg_txt, InputHints.ignoring_input)
        #     collectionStore={ "user": meeting_details}
        #     await self.cosmos_db.write(collectionStore)
        #     await step_context.context.send_activity(message)
        #
        # return await step_context.end_dialog()

        return await step_context.replace_dialog(MainDialog.__name__)