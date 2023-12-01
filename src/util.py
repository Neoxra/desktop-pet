""" Utility functions for the bot. """
import random
import os
import threading
import pyttsx3
from dotenv import load_dotenv
import openai

def normalize(lst):
    """Normalize a list to make its values sum to 1."""
    magnitude = sum(lst)
    return [v / magnitude for v in lst]

def make_cumulative(lst):
    """Convert a list into a cumulative distribution (a die)."""
    accumulated = 0
    for i in range(len(lst)):
        temp = lst[i]
        lst[i] = accumulated
        accumulated += temp
    return lst

class WeightedRandomMap:
    """Represents a weighted random map."""
    def __init__(self, lst):
        """Initialize with a list of objects containing 'name' and 'probability'."""
        self.names = [obj["name"] for obj in lst]
        self.probabilities = normalize([obj["probability"] for obj in lst])
        self.cumulative_distribution = make_cumulative(self.probabilities)
        assert len(self.names) == len(self.cumulative_distribution)

    def get_rand(self):
        """Get a random value based on the weighted probabilities."""
        val = random.random()
        for i, p in enumerate(self.cumulative_distribution):
            if p > val:
                return self.names[i - 1]
        return self.names[-1]

def openai_query(message):
    """Query OpenAI GPT-3 for a completion."""
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.Completion.create(model="text-davinci-003",
                                        prompt=message,
                                        temperature=.9,
                                        max_tokens=40)
    return response["choices"][0]["text"]

def speak(message, callback):
    """Speak the given message using text-to-speech."""
    engine = pyttsx3.init()
    engine.setProperty("pitch", 300)
    engine.say(message)

    def run_and_callback():
        """Run the text-to-speech engine and call the provided callback."""
        engine.runAndWait()
        callback()

    threading.Thread(target=run_and_callback).start()
