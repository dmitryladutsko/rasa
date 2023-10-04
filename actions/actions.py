import random
import string
from typing import *

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from actions.redis_service import RedisService


class ActionYourBalance(Action):
    """Action to check users balance"""
    def name(self) -> Text:
        return "action_your_balance"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        return [SlotSet("balance_value", str(random.randint(0, 99999)) + '$')]


class ActionGeneratePassword(Action):
    """Action to generate an OTP password for user"""
    def name(self) -> Text:
        return "action_generate_password"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_otp = ''.join(random.choices(string.digits, k=6))
        dispatcher.utter_message(text=f"Your OTP is {user_otp}")
        user_email = tracker.get_slot("user_email")

        connection = RedisService(user_email, user_otp)

        if connection.client:
            await connection.store_password()

        return []


class ActionCheckAuth(Action):
    """Action to check if the user is authenticated or not"""
    def name(self) -> Text:
        return "action_check_auth"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_email = tracker.get_slot("user_email")
        user_pass = tracker.get_slot("user_pass")

        connection = RedisService(user_email, user_pass)

        if connection.client:
            if await connection.check_user():
                dispatcher.utter_message(text="Successfully authenticated!")
            else:
                dispatcher.utter_message(text="Authorization failed!")

            return [SlotSet(key="is_authenticated", value=connection.check_user())]
