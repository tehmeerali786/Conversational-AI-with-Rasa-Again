# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List
from datetime import datetime, timedelta

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []


def text_date_to_int(text_date):
    if text_date == "today":
        return 0
    if text_date == "tomorrow":
        return 1
    if text_date == "yesterday":
        return -1


    # in other case
    return None



weekday_mapping = ["Monday", "Tuesday", "Wednessday", "Thursday", "Friday", "Saturday", "Sunday"]


def weekday_to_text(weekday):
    return weekday_mapping[weekday]


class ActionQueryTime(Action):
    def name(self) -> Text:
        return "action_query_time"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        current_time = datetime.now().strftime("It's %H:%M %p.")
        dispatcher.utter_message(text=current_time)

        return []


class ActionQueryDate(Action):
    def name(self) -> Text:
        return "action_query_date"

    def run(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        text_date = tracker.get_slot("date") or "today"

        int_date = text_date_to_int(text_date)
        if int_date is not None:
            delta = timedelta(days=int_date)
            if int_date is not None:
                delta = timedelta(days=int_date)
                current_date = datetime.now()

                target_date = current_date + delta

                dispatcher.utter_message(text=target_date.strftime("It's %B %d, %Y."))

            else:
                dispatcher.utter_message(text="The system currently doesn't support date query for '{}'".format(text_date))

            return []


class ActionQueryWeekday(Action):
    def name(self) -> Text:
        return "action_query_weekday"

    def run(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        text_date = tracker.get_slot("date") or "today"

        int_date = text_date_to_int(text_date)
        if int_date is not None:
            delta = timedelta(days=int_date)
            current_date = datetime.now()

            target_date = current_date + delta

            dispatcher.utter_message(text=weekday_to_text(target_date.weekday()))

        else:
            dispatcher.utter_message(text="The system currently doesn't support day of week query for '{}'".format(text_date))

        return []
