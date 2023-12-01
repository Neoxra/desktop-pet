"""Pet Module"""
import tkinter as tk
from os.path import join
from src.util import WeightedRandomMap, openai_query, speak

def read_frames(impath):
    """Read frames from the given image path."""
    frames = []
    i = 0
    while True:
        try:
            new_frame = tk.PhotoImage(file=join(impath), format=f'gif -index {i}')
            frames.append(new_frame)
        except Exception as e:
            print(f"Error loading frames: {e}")
            break
        i += 1
    return frames

class PetState:
    """Represents a state of the pet."""
    def __init__(self, json_obj, impath):
        self.name = json_obj['state_name']
        self.frames = read_frames(join(impath, json_obj['file_name']))
        self.dimensions = json_obj['dims']
        self.move = json_obj.get('move', (0, 0))
        self.next_states = WeightedRandomMap(json_obj['transitions_to'])

    def get_dimensions(self):
        """Get the dimensions of the state."""
        return self.dimensions

    def get_move(self):
        """Get the movement deltas for the state."""
        return self.move


class Pet:
    """Represents the virtual pet."""
    def __init__(self, states, window):
        self.states = states
        self.window = window
        self.current_state = list(states.values())[0]
        self.__current_frame = 0
        self.x, self.y = 45, 800

    def next_frame(self):
        """Get the next frame of the pet."""
        output = self.current_state.frames[self.__current_frame]
        self.__current_frame += 1
        if self.__current_frame == len(self.current_state.frames):
            self.__state_change()
        self.x, self.y = (
            self.x + self.current_state.dx), (self.y + self.current_state.dy)
        return output

    def __state_change(self):
        """Change to the next state."""
        self.set_state(self.current_state.next_states.get_rand())

    def set_state(self, name: str):
        """Set the state of the pet."""
        self.current_state = self.states[name]
        self.__current_frame = 0

    def start_chat(self, prompt: str, listen_state: str, response_state: str, end_state: str):
        """Start a chat with the pet."""
        self.set_state(listen_state)
        query = tk.simpledialog.askstring("ChatGPT Input",
                                            "What do you want to ask Bonzi?", 
                                            parent=self.window)
        response = openai_query(prompt % query)
        self.set_state(response_state)
        speak(response, lambda: self.set_state(end_state))
