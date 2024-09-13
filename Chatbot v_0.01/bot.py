class AnimeChatbot:
    def __init__(self):
        pass
        
    def message(self, prompt):
        self.prompt = prompt.lower()  
        
        if self.prompt in ["hi", "hello", "hey"]:
            return "Ora ora! I’m your anime buddy! Ready for some action? How can I assist you today?"
        elif self.prompt == "price":
            return "In the world of One Piece, the treasure is priceless! But for tickets here, it’s 100 yen. ⚔️"
        elif self.prompt == "joke":
            return "Why did Ichigo always bring a ladder to school? Because he wanted to reach new heights in his Soul Reaper training! 😂"
        elif self.prompt == "fun fact":
            return "Did you know? In Dr. Stone, the characters use science to bring back humanity. Pretty amazing, right? 🧪"
        elif self.prompt == "weather":
            return "I can't check the weather, but I hope it’s as blazing as a Fire Force flame! 🔥"
        elif self.prompt == "quote":
            return "Here’s a motivational quote from JoJo's Bizarre Adventure: 'It’s not the size of the dog in the fight, it’s the size of the fight in the dog.' – Joseph Joestar 💪"
        elif self.prompt == "thanks":
            return "Thanks a bunch! If you need more anime knowledge, just call on me, like Gon calling for his friends! 🌟"
        elif self.prompt == "bye":
            return "See you later, partner! May your journey be as epic as Luffy’s adventures! 🌊"
        elif self.prompt == "fire force":
            return "In Fire Force, the Special Fire Force Company 8 fights against spontaneous human combustion with intense flames and heroic spirit! 🔥"
        elif self.prompt == "fairy tail":
            return "Fairy Tail is all about magic, friendship, and epic guild battles! 'Together, we can face any challenge!' 🌟"
        elif self.prompt == "favorite character":
            return "It’s tough to choose, but I’d say Natsu from Fairy Tail for his fiery spirit, or Jonathan Joestar for his heroic legacy! ✨"
        elif self.prompt == "recommendation":
            return "If you love action and adventure, try watching Attack on Titan or Fullmetal Alchemist! They’re packed with epic moments and strong characters. 🚀"
        elif self.prompt == "battle":
            return "Who would win in a fight, Goku or Saitama? It’s a tough call, but both are legendary in their own universes! ⚔️"
        else:
            return "Hmm, that’s a bit out of my anime knowledge range. Ask me something about JoJo, One Piece, Bleach, Hunter x Hunter, Fire Force, Fairy Tail, or Dr. Stone! 🌀"

# Example usage
obj = AnimeChatbot()
