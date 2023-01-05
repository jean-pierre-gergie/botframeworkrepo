from botbuilder.core import StatePropertyAccessor, TurnContext
from botbuilder.dialogs import Dialog, DialogSet, DialogTurnStatus


class DialogHelper:
    @staticmethod
    async def run_dialog(
        dialog: Dialog, turn_context: TurnContext, accessor: StatePropertyAccessor,
    ):
        dialog_set = DialogSet(accessor)
        dialog_set.add(dialog)
        # here we can use CosmosDB to check if there is a user already or something similar

        dialog_context = await dialog_set.create_context(turn_context)
        results = await dialog_context.continue_dialog()
        if results.status == DialogTurnStatus.Empty:
            await dialog_context.begin_dialog(dialog.id)
