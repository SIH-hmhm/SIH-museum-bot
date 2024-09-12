class Chatbot:
    def __init__(self):
        pass
        
    def message(self, prompt):
        self.prompt = prompt.lower()  
        
        if self.prompt in ["hi", "hello", "hey"]:
            return "Hello! I’m your friendly chatbot. How can I assist you today?"
        elif self.prompt == "price":
            return "The price of the ticket is Rs. 100."
        elif self.prompt == "joke":
            return "Why don't scientists trust atoms? Because they make up everything!"
        elif self.prompt == "fun fact":
            return "Did you know? Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still edible!"
        elif self.prompt == "weather":
            return "I can't check the weather, but I hope it's sunny and bright where you are!"
        elif self.prompt == "quote":
            return "Here's a motivational quote for you: 'The only way to do great work is to love what you do.' – Steve Jobs"
        elif self.prompt == "thanks":
            return "You're welcome! If you need anything else, just let me know."
        elif self.prompt == "bye":
            return "Goodbye! Have a great day!"
        else:
            return "I’m not sure how to respond to that. Can you ask me something else?"

# Example usage
obj = Chatbot()
