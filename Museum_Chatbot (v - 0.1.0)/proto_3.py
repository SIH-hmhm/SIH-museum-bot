import json
import re
from difflib import get_close_matches
from datetime import datetime

def handle_date_time() -> dict:
    now = datetime.now()
    date = now.strftime("%d %B, %Y")  # e.g., "14 September, 2024"
    time = now.strftime("%I:%M:%S %p")  # e.g., "03:45:30 PM"
    return {"date": date, "time": time}


def load_dataset(dataset_file: str) -> dict:
    with open(dataset_file, "r") as file:
        data: dict = json.load(file)
        return data


def find_best_response(user_prompt: str, intents: list[str]) -> str | None:
    matches: list = get_close_matches(user_prompt.lower(), [intent.lower() for intent in intents], n=1, cutoff=0.4)
    if matches:
        return matches[0]
    return None



def extract_ticket_info(user_prompt: str) -> tuple[int, int]:
    adult_tickets = 0
    children_tickets = 0

    # Regular expressions to find numbers of adults and children in the prompt
    adult_match = re.search(r'(\d+)\s*adult', user_prompt, re.IGNORECASE)
    children_match = re.search(r'(\d+)\s*child', user_prompt, re.IGNORECASE)

    if adult_match:
        adult_tickets = int(adult_match.group(1))

    if children_match:
        children_tickets = int(children_match.group(1))

    return adult_tickets, children_tickets


def response_to_prompts(intent: str, dataset: dict, user_prompt: str) -> str | None:
    for q in dataset["intents"]:
        if q["intent"] == intent:
            if intent == "book_tickets_with_quantity":
                num_adults, num_children = extract_ticket_info(user_prompt)
                total_price = num_adults * 300 + num_children * 200
                return q["responses"][0].format(
                    num_adults=num_adults,
                    num_children=num_children,
                    total_price=total_price
                )
            elif intent == "date_time":
                params = handle_date_time()
                # Handle multiple responses
                responses = []
                for response in q["responses"]:
                    formatted_response = response.format(date=params["date"], time=params["time"])
                    responses.append(formatted_response)
                return " ".join(responses)  # Join responses into a single string
            else:
                return q["responses"][0]
    return "Sorry! No answers"



def chat_bot():
    dataset: dict = load_dataset("dataset.json")

    while True:
        user_prompt: str = input("You: ")
        if user_prompt.lower() == "quit":
            break

        # Find best matching question
        best_response: str | None = find_best_response(user_prompt, [q for intent in dataset["intents"] for q in intent["questions"]])

        if best_response:
            intent = next((q["intent"] for q in dataset["intents"] if best_response in q["questions"]), None)
            response: str = response_to_prompts(intent, dataset, user_prompt)
            print(f"Bot: {response}")
        else:
            print("Sorry! No answers")



chat_bot()
