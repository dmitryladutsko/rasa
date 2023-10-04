import random
from typing import *

from typing import Dict, Any

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


class ActionYourBalance(Action):
    def name(self) -> Text:
        return "action_your_balance"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        return [SlotSet("balance_value", str(random.randint(0, 99999)) + '$')]
