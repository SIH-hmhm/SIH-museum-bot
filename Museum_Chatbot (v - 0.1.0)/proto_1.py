import json
from difflib import get_close_matches


def load_dataset(dataset_file: str) -> dict:
    with open(dataset_file, "r") as file:
        data: dict = json.load(file)
        return data


def find_best_response(user_prompt: str, intents: list[str]) -> str | None:
    matches: list = get_close_matches(user_prompt, intents, n=1, cutoff=0.6)
    return matches[0] if matches else None


def response_to_prompts(question: str, dataset: dict) -> str | None:
    for q in dataset["intents"]:
        if question in q["questions"]:
            return q["responses"][0]


def chat_bot():
    dataset: dict = load_dataset("dataset.json")

    while True:
        user_prompt: str = input("You: ")
        if user_prompt.lower() == "quit":
            break


        best_response: str | None = find_best_response(user_prompt, [q for intent in dataset["intents"] for q in intent["questions"]])

        if best_response:
            response: str = response_to_prompts(best_response, dataset)
            print(f"Bot: {response}")
        else:
            print("Sorry! No answers")


chat_bot()
