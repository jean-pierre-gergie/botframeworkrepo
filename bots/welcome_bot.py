from typing import List
from botbuilder.core import (
    ConversationState,
    MessageFactory,
    UserState,
    TurnContext,
)
from botbuilder.dialogs import Dialog
from botbuilder.schema import ChannelAccount

from bots.dialog_bot import DialogBot



class DialogAndWelcomeBot(DialogBot):

    """

        inherits from DialogBot

    """

    def __init__(
        self,
        conversation_state: ConversationState,
        user_state: UserState,
        dialog: Dialog,

    ):
        super(DialogAndWelcomeBot, self).__init__(
            conversation_state, user_state, dialog
        )

    async def on_members_added_activity(
        self, members_added: List[ChannelAccount], turn_context: TurnContext
    ):
        for member in members_added:
            print("connected: new member added...")
            # Greet anyone that was not the target (recipient) of this message.
            # if member.id != turn_context.activity.recipient.id:
            #     await turn_context.send_activity(
            #         MessageFactory.text(f"Hello "
            #             f"Mr. Jean-Pierre isn't available at the moment."
            #             f"I am Sasha his assistant. How can I help you?"
            #         )
            #     )
