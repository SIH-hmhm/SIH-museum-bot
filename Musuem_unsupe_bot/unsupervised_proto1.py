import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.models import Model
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class UnsupervisedChatbot:
    def __init__(self, intents_data):
        self.intents_data = intents_data
        self.vectorizer = TfidfVectorizer()
        self.X = self.vectorizer.fit_transform([q for intent in intents_data for q in intent['questions']])
        self.model = self._build_model()
        
    def _build_model(self):
        input_dim = self.X.shape[1]
        inputs = Input(shape=(input_dim,))
        encoded = Dense(64, activation='relu')(inputs)
        decoded = Dense(input_dim, activation='linear')(encoded)
        
        autoencoder = Model(inputs, decoded)
        autoencoder.compile(optimizer='adam', loss='mse')
        
        return autoencoder
    
    def train(self, epochs=1000, batch_size=128):
        self.model.fit(self.X.toarray(), self.X.toarray(), 
                       epochs=epochs, batch_size=batch_size, verbose=1)
    
    def get_response(self, user_input):
        user_vector = self.vectorizer.transform([user_input])
        encoded_user = self.model.predict(user_vector.toarray())
        
        similarities = cosine_similarity(encoded_user, self.X.toarray())
        most_similar_idx = np.argmax(similarities)
        
        for intent in self.intents_data:
            if user_input.lower() in [q.lower() for q in intent['questions']]:
                return np.random.choice(intent['answers'])
        
        for intent in self.intents_data:
            if most_similar_idx < len(intent['questions']):
                return np.random.choice(intent['answers'])
            most_similar_idx -= len(intent['questions'])
        
        return "I'm not sure how to respond to that."
    
    def interactive_session(self):
        print("Chatbot: Hello! How can I help you today? (Type 'quit' to exit)")
        while True:
            user_input = input("You: ")
            if user_input.lower() == 'quit':
                print("Chatbot: Goodbye!")
                break
            response = self.get_response(user_input)
            print("Chatbot:", response)
    
    def add_intent(self, new_intent):
        self.intents_data.append(new_intent)
        new_questions = [q for q in new_intent['questions']]
        new_vectors = self.vectorizer.transform(new_questions)
        self.X = tf.sparse.concat(0, [self.X, new_vectors])
        self.train(epochs=10)  # Quick retraining

# Example usage
intents_data = [
    {
        "intent": "greeting",
        "questions": ["Hello", "Hi", "Hey", "Good morning", "Good afternoon"],
        "answers": ["Hello!", "Hi there!", "Hey! How can I help you?", "Good day! How may I assist you?", "Greetings! What can I do for you?"]
    },
    {
        "intent": "farewell",
        "questions": ["Bye", "Goodbye", "See you later", "Take care", "I'm leaving"],
        "answers": ["Goodbye!", "See you later!", "Have a great day!", "Take care!", "Farewell! Come back soon!"]
    },
    {
        "intent": "thank_you",
        "questions": ["Thanks", "Thank you", "I appreciate it", "Thanks a lot", "Much appreciated"],
        "answers": ["You're welcome!", "Glad I could help!", "My pleasure!", "Anytime!", "Happy to assist!"]
    },
    {
        "intent": "weather_query",
        "questions": ["What's the weather like?", "Is it going to rain today?", "Temperature today", "Weather forecast", "Is it sunny outside?"],
        "answers": ["I'm sorry, I don't have real-time weather data. You might want to check a weather app or website for accurate information.", "I don't have access to current weather information. Maybe try looking outside or checking a weather service?", "Unfortunately, I can't provide weather forecasts. Consider checking a reliable weather source for up-to-date information."]
    },
    {
        "intent": "time_query",
        "questions": ["What time is it?", "Current time", "Tell me the time", "Do you know what time it is?", "What's the time now?"],
        "answers": ["I'm afraid I don't have access to the current time. You might want to check your device's clock.", "As an AI, I don't have real-time information about the current time. You could check your watch or phone for the accurate time.", "I don't have the ability to tell the current time. Perhaps you could look at a clock or your device's time display?"]
    },
    {
        "intent": "name_query",
        "questions": ["What's your name?", "Who are you?", "What should I call you?", "Do you have a name?", "Introduce yourself"],
        "answers": ["I'm an AI assistant created by Anthropic. You can call me Claude.", "My name is Claude. I'm an AI created by Anthropic to assist with various tasks.", "I'm Claude, an AI assistant. It's nice to meet you!"]
    },
    {
        "intent": "age_query",
        "questions": ["How old are you?", "What's your age?", "When were you created?", "How long have you existed?", "Are you a new AI?"],
        "answers": ["As an AI, I don't have an age in the traditional sense. I was created recently by Anthropic, but I don't have a specific 'birth date'.", "I don't have an age like humans do. I'm an AI that was developed recently, but I'm not sure of the exact date.", "I'm not sure how to quantify my age. I'm a recently developed AI, but the concept of age doesn't really apply to me in the same way it does to humans."]
    },
    {
        "intent": "capability_query",
        "questions": ["What can you do?", "What are your capabilities?", "How can you help me?", "What tasks can you perform?", "Tell me about your abilities"],
        "answers": ["I can assist with a wide range of tasks including writing, analysis, math, coding, and answering questions on various topics. What kind of help do you need?", "My capabilities include helping with writing tasks, providing information on diverse subjects, assisting with problem-solving, and offering creative ideas. How may I assist you today?", "I'm able to help with many things such as research, writing, coding, math, and general knowledge questions. What would you like help with?"]
    },
    {
        "intent": "joke_request",
        "questions": ["Tell me a joke", "Do you know any jokes?", "Make me laugh", "I want to hear a joke", "Got any good jokes?"],
        "answers": ["Why don't scientists trust atoms? Because they make up everything!", "What do you call a fake noodle? An impasta!", "Why did the scarecrow win an award? He was outstanding in his field!", "What do you call a bear with no teeth? A gummy bear!", "Why did the math book look so sad? Because it had too many problems."]
    },
    {
        "intent": "favorite_color",
        "questions": ["What's your favorite color?", "Do you have a preferred color?", "Which color do you like best?", "Tell me about your favorite color", "If you had to choose a color, which would it be?"],
        "answers": ["As an AI, I don't have personal preferences or favorites, including colors. I don't experience color the way humans do.", "I don't actually have a favorite color. As an AI, I don't have personal preferences or the ability to see or experience colors.", "I don't have favorites or preferences, including for colors. I'm an AI, so I don't perceive or experience colors like humans do."]
    },
    {
        "intent": "meaning_of_life",
        "questions": ["What is the meaning of life?", "Why are we here?", "What's the purpose of existence?", "Can you explain the meaning of life?", "Is there a point to life?"],
        "answers": ["The meaning of life is a profound philosophical question that has been debated for centuries. There's no one agreed-upon answer.", "That's a deep question that philosophers have pondered for ages. There are many different perspectives on the meaning of life.", "The purpose of existence is a complex topic with no definitive answer. It often depends on individual beliefs and philosophies."]
    },
    {
        "intent": "favorite_food",
        "questions": ["What's your favorite food?", "What do you like to eat?", "Do you have a preferred cuisine?", "What's the best food in your opinion?", "If you could eat anything, what would it be?"],
        "answers": ["As an AI, I don't eat food or have preferences for taste. I don't have the ability to experience flavors or have favorite foods.", "I don't actually eat or have favorite foods. I'm an AI, so I don't have the ability to taste or experience food like humans do.", "I don't have favorite foods or eat anything. As an AI, I don't have the capacity to taste or enjoy food."]
    },
    {
        "intent": "hobbies",
        "questions": ["What are your hobbies?", "What do you do for fun?", "Do you have any interests?", "How do you spend your free time?", "What activities do you enjoy?"],
        "answers": ["As an AI, I don't have hobbies or free time in the way humans do. My purpose is to assist and provide information.", "I don't actually have hobbies or do things for fun. I'm an AI assistant, so I'm here to help with tasks and answer questions.", "I don't have personal interests or hobbies. My function is to assist users with various tasks and provide information."]
    },
    {
        "intent": "current_location",
        "questions": ["Where are you located?", "What's your current location?", "Where are you right now?", "Are you in a specific place?", "Tell me about your location"],
        "answers": ["As an AI, I don't have a physical location. I exist as a computer program and can be accessed from anywhere with an internet connection.", "I don't have a specific location. I'm a digital AI assistant, so I exist in the cloud and can be accessed from various places.", "I'm not located in any particular place. As an AI, I operate in a virtual environment and can assist users from anywhere."]
    },
    {
        "intent": "book_recommendation",
        "questions": ["Can you recommend a good book?", "What should I read next?", "Any book suggestions?", "What's a must-read book?", "I need a book recommendation"],
        "answers": ["There are many great books out there! Can you tell me what genres you enjoy or what kind of book you're looking for?", "I'd be happy to suggest some books. What types of books do you usually enjoy reading?", "Book recommendations can be very personal. Could you share some of your favorite books or authors to help me make a good suggestion?"]
    },
    {
        "intent": "movie_recommendation",
        "questions": ["What's a good movie to watch?", "Can you suggest a film?", "I need a movie recommendation", "What movie should I see?", "Any must-watch films?"],
        "answers": ["There are so many great movies out there! What genres do you enjoy or what kind of movie are you in the mood for?", "I'd be happy to suggest some movies. Could you tell me some of your favorite films or directors to help guide my recommendation?", "Movie preferences can be quite personal. Can you share what types of films you typically enjoy watching?"]
    },
    {
        "intent": "travel_destination",
        "questions": ["Where should I go on vacation?", "Can you suggest a travel destination?", "I need ideas for a trip", "What's a good place to visit?", "Recommend a holiday spot"],
        "answers": ["There are many wonderful places to visit! What kind of vacation are you looking for? Beach, city, nature, or something else?", "I'd be happy to suggest some destinations. What's your budget and how long do you plan to travel?", "Travel recommendations depend on various factors. Can you tell me what you enjoy doing on vacation and any preferences you have?"]
    },
    {
        "intent": "learn_language",
        "questions": ["How can I learn a new language?", "What's the best way to study a foreign language?", "Tips for language learning", "I want to become fluent in another language", "Strategies for mastering a new language"],
        "answers": ["Learning a new language can be exciting! Some effective methods include immersion, regular practice, using language learning apps, and finding a language exchange partner.", "To learn a new language, consider taking classes, using language learning software, practicing with native speakers, and immersing yourself in media in that language.", "Consistency is key in language learning. Try to study a little bit every day, use various resources like books, apps, and podcasts, and don't be afraid to make mistakes!"]
    },
    {
        "intent": "exercise_tips",
        "questions": ["How can I start exercising?", "What are some good workouts for beginners?", "Tips for getting fit", "How to create an exercise routine", "Best exercises for weight loss"],
        "answers": ["Starting an exercise routine can be as simple as going for daily walks. Gradually increase intensity with activities like jogging, swimming, or cycling. Always consult a doctor before starting a new exercise program.", "For beginners, a mix of cardio and strength training is often recommended. Start with bodyweight exercises like push-ups, squats, and lunges, combined with moderate cardio like brisk walking or cycling.", "The key to a successful exercise routine is consistency. Find activities you enjoy, start slowly, and gradually increase duration and intensity. Don't forget to include both cardio and strength training in your routine."]
    },
    {
        "intent": "healthy_eating",
        "questions": ["How can I eat healthier?", "What's a balanced diet?", "Nutrition tips", "Foods to avoid for better health", "How to improve my diet"],
        "answers": ["Eating healthier often involves incorporating more fruits, vegetables, whole grains, and lean proteins into your diet. Try to limit processed foods, sugary drinks, and excessive amounts of saturated fats.", "A balanced diet typically includes a variety of foods from all food groups. Focus on whole foods, control portion sizes, and stay hydrated. It's also important to limit intake of added sugars and unhealthy fats.", "To improve your diet, try meal planning, cooking at home more often, reading nutrition labels, and gradually replacing unhealthy foods with nutritious alternatives. Remember, small changes can make a big difference over time."]
    },
    {
        "intent": "stress_management",
        "questions": ["How can I reduce stress?", "Tips for managing anxiety", "Ways to relax", "Stress relief techniques", "How to cope with pressure"],
        "answers": ["Managing stress can involve techniques like deep breathing, meditation, regular exercise, and ensuring you get enough sleep. It's also important to maintain a healthy work-life balance.", "To reduce stress, try practicing mindfulness, engaging in hobbies you enjoy, spending time in nature, and talking to friends or a therapist. Regular physical activity can also be very effective in managing stress.", "Coping with pressure often involves developing good time management skills, setting realistic goals, and learning to say no when necessary. Remember to take breaks and practice self-care regularly."]
    },
    {
        "intent": "career_advice",
        "questions": ["How can I advance in my career?", "Tips for professional growth", "Ways to get promoted", "How to switch careers", "Advice for job seekers"],
        "answers": ["Advancing in your career often involves continuous learning, networking, taking on new responsibilities, and clearly communicating your goals to your superiors. Consider seeking a mentor in your field.", "For professional growth, focus on developing both hard and soft skills relevant to your industry. Stay updated with industry trends, attend conferences, and look for opportunities to lead projects or mentor others.", "If you're looking to switch careers, start by assessing your skills and interests. Research potential fields, consider additional education or training if necessary, and try to gain relevant experience through volunteering or part-time work."]
    },
    {
        "intent": "personal_finance",
        "questions": ["How can I manage my money better?", "Tips for saving money", "How to create a budget", "Advice for personal finance", "Ways to reduce debt"],
        "answers": ["Managing money effectively often starts with creating a budget. Track your income and expenses, set financial goals, and try to live below your means. Consider automating your savings to make it easier.", "To save money, look for ways to reduce unnecessary expenses, compare prices before making purchases, and consider using cash instead of credit cards for daily spending. Setting up an emergency fund is also important.", "Reducing debt usually involves paying more than the minimum payment, starting with high-interest debt first. Consider consolidating debts if possible, and avoid taking on new debt while paying off existing ones."]
    },
    {
        "intent": "time_management",
        "questions": ["How can I manage my time better?", "Tips for productivity", "Ways to stop procrastinating", "How to be more efficient", "Advice for balancing work and life"],
        "answers": ["Effective time management often involves prioritizing tasks, breaking larger projects into smaller, manageable steps, and using tools like calendars and to-do lists. Try to eliminate or delegate less important tasks.", "To boost productivity, consider techniques like the Pomodoro method (working in focused 25-minute intervals with short breaks), minimizing distractions, and tackling your most important tasks when your energy levels are highest.", "Balancing work and life often requires setting clear boundaries, learning to say no to non-essential commitments, and scheduling time for both work and personal activities. Remember to include time for self-care and relaxation."]
    },
    {
        "intent": "sustainability_tips",
        "questions": ["How can I be more eco-friendly?", "Tips for sustainable living", "Ways to reduce carbon footprint", "How to help the environment", "Advice for green living"],
        "answers": ["Being more eco-friendly can start with small changes like reducing single-use plastics, conserving water and energy, and choosing sustainable transportation options when possible.", "For sustainable living, consider buying products with minimal packaging, supporting local and sustainable businesses, and reducing meat consumption. Composting and recycling properly also make a significant impact.", "To reduce your carbon footprint, try to minimize car use, opt for energy-efficient appliances, insulate your home properly, and consider switching to renewable energy sources if available in your area."]
    },
    {
        "intent": "sleep_improvement",
        "questions": ["How can I sleep better?", "Tips for improving sleep quality", "Ways to fall asleep faster", "How to establish a sleep routine", "Advice for dealing with insomnia"],
        "answers": ["To improve sleep, try to maintain a consistent sleep schedule, create a relaxing bedtime routine"]
    }]

chatbot = UnsupervisedChatbot(intents_data)
chatbot.train()
chatbot.interactive_session()