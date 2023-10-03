from typing import Any, Dict, List, Text
import os
import openai
import requests
import io
import pandas as pd
import random
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class Simple_Google_sheet_or_ChatGPT_Action(Action):

    def name(self) -> Text:
        return "simple_google_sheet_or_chatgpt_action"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_text = tracker.latest_message.get('text')
        intent = tracker.latest_message.get('intent').get('name')
        entities = tracker.latest_message.get('entities')
        
        answer = self.get_answers_from_sheets(intent, entities, user_text)

        dispatcher.utter_message('Bot: ' + answer)
        return []
    
    def get_answers_from_sheets(self, intent: Text, entities: List[Dict[Text, Any]], user_text: Text) -> Text:
        sheet_url = "https://docs.google.com/spreadsheets/d/1ejQ9Z9y0S2p_JY3ipKjl7MTWKtbMOnH8Ve5XfvxSrj4/gviz/tq?tqx=out:csv&sheet=Sheet1"

        try:
            s = requests.get(sheet_url).content
            proxy_df = pd.read_csv(io.StringIO(s.decode('utf-8')))
            
            # Extrait la valeur d'entité du premier élément dans la liste des entités
            entity_value = entities[0]['value'] if entities else None
            print(f"Valeur d'entité : {entity_value}")
            
            # Convertit l'intention en minuscules pour la comparaison (évite les problèmes de casse)
            intent_lower = intent.lower()

            # Filtrer par l'intent et l'entité
            filtered_df = proxy_df[(proxy_df['Intent'].str.lower() == intent_lower) & (proxy_df['Entity'] == entity_value)]

            if not filtered_df.empty:
                answers = filtered_df['Answer'].tolist()
                print(f"Message d'entité : {answers}")
                return random.choice(answers)

            # return self.get_default_fallback_response()
            return self.get_answers_from_chatgpt(user_text)
            
        except Exception as e:
            print(f"Erreur lors de l'accès à Google Sheets : {e}")
            # return self.get_default_fallback_response()
            return self.get_answers_from_chatgpt(user_text)


    def get_answers_from_chatgpt(self, user_text: Text) -> Text:
        # Utilisez votre clé d'API OpenAI ici
        openai.api_key = "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"

        # Ajoutez un préfixe en français pour spécifier la langue
        prompt = "En français : " + user_text
        
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5,
        ).choices[0].text

        return response

    def get_default_fallback_response(self) -> Text:
        fallback_responses = ["Je ne comprends pas. Pouvez-vous reformuler votre question?", "Désolé, je ne peux pas répondre à ça pour le moment."]
        return random.choice(fallback_responses)



