import random
import string
from typing import *

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from actions.redis_service import RedisService


class ActionYourBalance(Action):
    """Action to check users balance"""
    def name(self) -> Text:
        return "action_your_balance"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        return [SlotSet("slot_balance_value", str(random.randint(0, 99999)) + '$')]


class ActionGeneratePassword(Action):
    """Action to generate an OTP password for user"""
    def name(self) -> Text:
        return "action_ask_form_user_credentials_slot_user_password"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        fails = tracker.get_slot("slot_number_of_fails")
        fails: int = 0 if fails is None else int(fails)

        if not fails:
            user_otp = ''.join(random.choices(string.digits, k=6))
            dispatcher.utter_message(text=f"Your OTP is {user_otp}")
            dispatcher.utter_message(text=f"Enter your OTP:")
            user_email = tracker.get_slot("slot_user_email")

            connection = RedisService()
            if connection.client:
                connection.store_password(user_email, user_otp)

        return []


class ValidateUserCredentialsForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_form_user_credentials"

    def validate_slot_user_password(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        user_email = tracker.get_slot("slot_user_email")
        user_password = slot_value
        fails = tracker.get_slot("slot_number_of_fails")
        fails: int = 0 if not fails else int(fails)

        connection = RedisService()
        result: bool = connection.check_user(user_email, user_password)

        if result:
            dispatcher.utter_message(text="Successfully authenticated!")
            requested_slot = None
        else:
            dispatcher.utter_message(text="Authentication failed!")
            fails += 1
            slot_value = None
            requested_slot = "slot_user_password"

            if fails > 2:
                dispatcher.utter_message(text="You have used all 3 attempts!")
                connection.delete_password(user_email)
                fails = 0
                action_generate_password = ActionGeneratePassword()
                action_generate_password.run(
                    dispatcher=dispatcher,
                    tracker=tracker,
                    domain=domain
                )

            else:
                dispatcher.utter_message(text=f"Only {3 - fails} attempts left!")
                dispatcher.utter_message(text="Enter the correct password:")

        return {"slot_user_password": slot_value,
                "slot_number_of_fails": fails,
                "requested_slot": requested_slot,
                "slot_is_authenticated": result}
