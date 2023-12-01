""" Main file for the desktop pet."""
import json
import sys
from os.path import join
import tkinter as tk
from src.pet import Pet, PetState

CONFIG_PATH = sys.argv[1] if len(sys.argv) >= 2 else "../assets/bonzi"

def configure_window(window):
    """Configure window settings."""
    window.config(highlightbackground='black')
    label = tk.Label(window, bd=0, bg='black')
    window.overrideredirect(True)
    window.wm_attributes('-transparentcolor', 'black')
    label.pack()

def load_config(config_path):
    """Load configuration from the given path."""
    with open(join(config_path, "config.json"), encoding="utf-8") as config_file:
        return json.load(config_file)

def validate_next_states(states):
    """Validate next states."""
    for state in states.values():
        for next_state in state.next_states.names:
            if next_state not in states:
                raise ValueError(f"Invalid next state '{next_state}' for '{state.state_name}'")

def create_event_func(event, pet):
    """Create an event function from the event object."""
    event_type_handlers = {
        "state_change": lambda e: pet.set_state(event["new_state"]),
        "chatgpt": lambda e: pet.start_chat(event["prompt"],
                                            event["listen_state"],
                                            event["response_state"],
                                            event["end_state"]),
    }
    return event_type_handlers.get(event["type"], lambda e: None)

def update(pet, label, window):
    """Update the pet's image and position."""
    frame = pet.next_frame()
    label.configure(image=frame)
    window.geometry(f'{pet.current_state.w}'
                    f'x{pet.current_state.h}'
                    f'+{pet.x + pet.current_state.ox}'
                    f'+{pet.y + pet.current_state.oy}')
    window.after(100, update, pet, label, window)

def main():
    """Main function."""
    window = tk.Tk()
    configure_window(window)
    config_obj = load_config(CONFIG_PATH)

    states = {state['state_name']: PetState(state, CONFIG_PATH) for state in config_obj["states"]}
    validate_next_states(states)

    pet = Pet(states, window)

    for event in config_obj["events"]:
        event_func = create_event_func(event, pet)
        if event["trigger"] == "click":
            window.bind("<Button-1>", event_func)

    window.after(1, update, pet, window)
    window.mainloop()

if __name__ == "__main__":
    main()
