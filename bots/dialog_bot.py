from botbuilder.core import ActivityHandler, ConversationState, UserState, TurnContext
from botbuilder.dialogs import Dialog
from helpers.dialog_helper import DialogHelper
from botbuilder.azure import CosmosDbStorage
'''JPG
    this class inherits from the activity handler class
    an activity is a message or a pic or an attachment  taveling between the bot and any member added to the channel
    : ConverationState keeps track of the conversation so no confusion will happen 
    : UserState keeps track of what user information is already acquired by the bot
    : Dialog is the initial dialog that will be initiated in the stack in this case MainDialog
    

'''
class DialogBot(ActivityHandler):
    def __init__(
        self,
        conversation_state: ConversationState,
        user_state: UserState,
        dialog: Dialog,

    ):
        if conversation_state is None:
            raise Exception(
                "[DialogBot]: Missing parameter. conversation_state is required"
            )
        if user_state is None:
            raise Exception("[DialogBot]: Missing parameter. user_state is required")
        if dialog is None:
            raise Exception("[DialogBot]: Missing parameter. dialog is required")

        self.conversation_state = conversation_state
        self.user_state = user_state
        self.dialog = dialog

    '''JPG
       on turn method represent when the turn is given to the user or to the bot 
       on each change of turn we will save the conversation state and user state
    '''
    async def on_turn(self, turn_context: TurnContext):
        await super().on_turn(turn_context)

        # Save any state changes that might have occurred during the turn.
        await self.conversation_state.save_changes(turn_context, False)
        await self.user_state.save_changes(turn_context, False)

    async def on_message_activity(self, turn_context: TurnContext):
        await DialogHelper.run_dialog(
            self.dialog,
            turn_context,
            self.conversation_state.create_property("DialogState"),

        )

    '''JPG
           when a message is received the dialog helper will initiate a dialog with the respective parameters
    '''