import json
import re
from difflib import get_close_matches


def load_dataset(dataset_file: str) -> dict:
    with open(dataset_file, "r") as file:
        data: dict = json.load(file)
        return data


def find_best_response(user_prompt: str, intents: list[str]) -> str | None:
    matches: list = get_close_matches(user_prompt, intents, n=1, cutoff=0.4)
    return matches[0] if matches else None



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


def response_to_prompts(question: str, dataset: dict, user_prompt: str) -> str | None:
    for q in dataset["intents"]:
        if question in q["questions"]:
            if q["intent"] == "book_tickets_with_quantity":
                num_adults, num_children = extract_ticket_info(user_prompt)
                total_price = num_adults * 300 + num_children * 200

                # Format the response with extracted ticket details
                return q["responses"][0].format(
                    num_adults=num_adults,
                    num_children=num_children,
                    total_price=total_price
                )
            return q["responses"][0]


def chat_bot():
    dataset: dict = load_dataset("dataset.json")

    while True:
        user_prompt: str = input("You: ")
        if user_prompt.lower() == "quit":
            break

        # Find best matching question
        best_response: str | None = find_best_response(user_prompt, [q for intent in dataset["intents"] for q in
                                                                     intent["questions"]])

        if best_response:
            response: str = response_to_prompts(best_response, dataset, user_prompt)
            print(f"Bot: {response}")
        else:
            print("Sorry! No answers")


chat_bot()
