import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Input, Dense # type: ignore
from tensorflow.keras.models import Model # type: ignore
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

class UnsupervisedChatbot:
    def __init__(self, intents_data=None):
        self.vectorizer = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        self.X = np.array([])
        self.cluster_model = None
        self.intents_data = []
        self.autoencoder = None
        self.new_questions = []
        self.new_question_counter = 0
        self.intent_vectors = None
        self.initialize_intents(intents_data)

    def _build_model(self, neurons=256):
        input_dim = 384  # Dimension of sentence embeddings
        inputs = Input(shape=(input_dim,))
        encoded = Dense(neurons, activation='relu')(inputs)
        encoded = Dense(neurons // 2, activation='relu')(encoded)
        encoded = Dense(neurons // 4, activation='relu')(encoded)  # Additional layer
        decoded = Dense(neurons // 2, activation='relu')(encoded)
        decoded = Dense(neurons, activation='relu')(decoded)
        decoded = Dense(input_dim, activation='linear')(decoded)
        
        autoencoder = Model(inputs, decoded)
        autoencoder.compile(optimizer='adam', loss='mse')
        return autoencoder

    def train_autoencoder(self, epochs=150, batch_size=32, neurons=256):
        if self.X.size == 0:
            return
        self.autoencoder = self._build_model(neurons)
        self.autoencoder.fit(self.X, self.X, epochs=epochs, batch_size=batch_size, verbose=1)

    def update_data(self, user_inputs):
        new_embeddings = self.vectorizer.encode(user_inputs)
        
        if self.X.size == 0:
            self.X = new_embeddings
        else:
            self.X = np.vstack([self.X, new_embeddings])
        
        self.X = self.X.astype(np.float64)
        
        self.new_questions.extend(user_inputs)
        self.new_question_counter += len(user_inputs)
        
        if self.new_question_counter >= 20:  # Increased threshold for retraining
            self.train_autoencoder(epochs=100, batch_size=32, neurons=256)
            num_clusters = min(150, max(73, len(self.X) // 5))
            self.cluster_model = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
            self.cluster_model.fit(self.X)
            self.new_questions = []
            self.new_question_counter = 0
            self.precompute_intent_vectors()

    def find_similar_question(self, user_input):
        user_vector = self.vectorizer.encode([user_input])[0]
        user_vector = np.array(user_vector, dtype=np.float64)
        if self.X.size == 0:
            return None
        
        similarities = cosine_similarity([user_vector], self.X)[0]
        most_similar_index = np.argmax(similarities)
        max_similarity = similarities[most_similar_index]
        
        if max_similarity > 0.8:  # Adjusted similarity threshold
            return self.new_questions[most_similar_index]
        return None

    def get_response(self, user_input):
        user_vector = self.vectorizer.encode([user_input])[0]
        
        # Exact match check (case-insensitive)
        lower_input = user_input.lower()
        for intent in self.intents_data:
            if lower_input in [q.lower() for q in intent['questions']]:
                return np.random.choice(intent['answers'])
        
        # Similarity-based matching
        similarities = cosine_similarity([user_vector], self.intent_vectors)[0]
        most_similar_intent_index = np.argmax(similarities)
        max_similarity = similarities[most_similar_intent_index]
        
        if max_similarity > 0.7:  # Adjust this threshold as needed
            return np.random.choice(self.intents_data[most_similar_intent_index]['answers'])
        
        # Fallback for low confidence
        return "I'm not sure how to respond to that. Could you rephrase your question or provide more context?"

    def interactive_session(self):
        print("Chatbot: Hello! How can I help you today? (Type 'quit' to exit)")
        while True:
            user_input = input("You: ")
            if user_input.lower() == 'quit':
                print("Chatbot: Goodbye!")
                break
            self.update_data([user_input])
            response = self.get_response(user_input)
            print("Chatbot:", response)

    def initialize_intents(self, intents_data):
        if intents_data:
            questions = [q for intent in intents_data for q in intent['questions']]
            self.update_data(questions)
            self.train_autoencoder(epochs=500, batch_size=32, neurons=256)
            num_clusters = min(150, max(73, len(self.X) // 5))
            self.cluster_model = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
            self.cluster_model.fit(self.X)
            self.intents_data = intents_data
            self.precompute_intent_vectors()

    def precompute_intent_vectors(self):
        self.intent_vectors = []
        for intent in self.intents_data:
            intent_vector = np.mean([self.vectorizer.encode(q) for q in intent['questions']], axis=0)
            self.intent_vectors.append(intent_vector)
        self.intent_vectors = np.array(self.intent_vectors)

    def save_model(self, filename):
        np.save(f"{filename}_embeddings.npy", self.X)
        self.autoencoder.save(f"{filename}_autoencoder.h5")
        np.save(f"{filename}_intents.npy", self.intents_data)
        np.save(f"{filename}_intent_vectors.npy", self.intent_vectors)

    def load_model(self, filename):
        self.X = np.load(f"{filename}_embeddings.npy")
        self.autoencoder = tf.keras.models.load_model(f"{filename}_autoencoder.h5")
        self.intents_data = np.load(f"{filename}_intents.npy", allow_pickle=True).tolist()
        self.intent_vectors = np.load(f"{filename}_intent_vectors.npy")
        self.update_data([])  # Update clustering

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
    },
    {
        "intent": "favorite_animal",
        "questions": ["What's your favorite animal?", "Do you like animals?", "Which animal do you like?", "Tell me about your favorite animal", "If you had to pick an animal, what would it be?"],
        "answers": ["As an AI, I don't have personal preferences, including favorite animals, but I can tell you about many interesting animals!", "I don't have a favorite animal since I don't experience things like humans, but animals are fascinating to learn about.", "I don't have a favorite animal, but I can share facts about different ones. Do you have a favorite animal?"]
    },
    {
        "intent": "help_with_study",
        "questions": ["Can you help me study?", "How can I improve my study habits?", "Tips for studying", "I need help with studying", "How to focus better while studying?"],
        "answers": ["Of course! One way to improve study habits is by breaking study sessions into shorter intervals and taking breaks in between.", "Yes, I can help! Focus on setting clear goals, managing time effectively, and reviewing material regularly.", "For effective studying, create a study plan, eliminate distractions, and try using active recall techniques. How can I assist you specifically?"]
    },
    {
        "intent": "pet_care",
        "questions": ["How do I take care of my pet?", "Can you give me pet care tips?", "What does my pet need?", "How to keep pets healthy?", "Best ways to care for my dog/cat?"],
        "answers": ["Pet care depends on the type of pet, but generally, make sure they have proper food, exercise, and regular vet check-ups.", "To care for your pet, provide a balanced diet, clean water, regular exercise, and plenty of attention and love.", "Caring for a pet includes providing nutritious food, regular grooming, mental stimulation, and maintaining their overall health with vet visits."]
    },
    {
        "intent": "birthday_wish",
        "questions": ["It's my birthday!", "Can you wish me a happy birthday?", "Today is my birthday!", "Say happy birthday", "I want a birthday message"],
        "answers": ["Happy Birthday! 🎉 Wishing you a wonderful day filled with joy and fun!", "Happy Birthday! May your day be as special as you are!", "Wishing you a fantastic birthday and a year full of happiness ahead! 🎂🎈"]
    },
    {
        "intent": "motivation_boost",
        "questions": ["I need motivation", "Help me stay motivated", "Can you give me a pep talk?", "How can I stay motivated?", "Give me some motivation"],
        "answers": ["You've got this! Keep going, one step at a time. Small progress is still progress.", "Stay focused on your goals! Every effort you make brings you closer to success.", "Believe in yourself! You are capable of achieving great things, just keep pushing forward."]
    },
    {
        "intent": "self_care",
        "questions": ["How can I practice self-care?", "Give me self-care tips", "How do I take care of myself?", "Ways to improve self-care", "Best self-care strategies"],
        "answers": ["Self-care can include simple things like taking breaks, getting enough sleep, eating well, and doing activities that make you happy.", "Taking care of yourself means listening to your body, setting boundaries, and giving yourself time to rest and recharge.", "Practice self-care by doing things you enjoy, practicing mindfulness, and staying connected with loved ones."]
    },
    {
        "intent": "music_recommendation",
        "questions": ["What music should I listen to?", "Can you suggest some music?", "I need a music recommendation", "Recommend me some good songs", "What are your favorite tunes?"],
        "answers": ["There are so many great genres! What kind of music are you in the mood for?", "I can recommend some popular genres like jazz, pop, rock, or classical. Do you have a preference?", "Music tastes can vary. If you're looking for something new, try exploring playlists on music platforms. What genre do you usually enjoy?"]
    },
    {
        "intent": "positive_affirmations",
        "questions": ["Can you give me some positive affirmations?", "Tell me something uplifting", "I need some positivity", "Give me a positive affirmation", "Make me feel better"],
        "answers": ["You are strong, capable, and ready to face any challenge. Believe in yourself!", "You are doing your best, and that's more than enough. Keep going, great things are ahead!", "Every day is a new opportunity to grow and improve. You’ve got this!"]
    },
    {
        "intent": "fun_fact",
        "questions": ["Tell me a fun fact", "Give me an interesting fact", "Do you know any fun facts?", "I want to hear a cool fact", "Share a random fact with me"],
        "answers": ["Did you know that honey never spoils? Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible!", "An octopus has three hearts! Two pump blood to the gills, while the third pumps it to the rest of the body.", "Bananas are berries, but strawberries aren't! Botanically speaking, berries come from a single ovary and have seeds embedded in the flesh."]
    },
    {
        "intent": "news_update",
        "questions": ["What's in the news today?", "Give me a news update", "Tell me the latest news", "What's happening in the world?", "Any current events I should know about?"],
        "answers": ["I can't provide real-time news, but you can check reliable news websites or apps for the latest updates.", "I recommend checking a trusted news source like BBC, CNN, or Reuters for up-to-date information.", "I don't have live news updates, but you can follow current events through reputable news platforms."]
    },
    {
        "intent": "dream_meaning",
        "questions": ["What does my dream mean?", "Can you interpret dreams?", "I had a weird dream", "Tell me about dream meanings", "What is the meaning of dreams?"],
        "answers": ["Dream interpretations can vary, but common themes like falling might represent feeling out of control, while flying could symbolize freedom or ambition.", "Dreams are often symbolic and can reflect your subconscious thoughts or emotions. Is there something specific you'd like to discuss?", "There are many theories about dream meanings, but ultimately, they often relate to your personal experiences or feelings."]
    },
    {
        "intent": "space_fact",
        "questions": ["Tell me a fact about space", "What’s cool about space?", "I want to learn about the universe", "Share a space fact", "What's something interesting about outer space?"],
        "answers": ["Space is completely silent because there’s no atmosphere for sound to travel through.", "One day on Venus is longer than a year on Venus due to its slow rotation.", "There are more stars in the universe than grains of sand on all the beaches on Earth."]
    },
    {
        "intent": "personality_type",
        "questions": ["What's my personality type?", "Can you help me figure out my personality?", "Tell me about personality types", "How do I find my personality type?", "What are the different personality types?"],
        "answers": ["Personality types are often categorized using models like the Myers-Briggs Type Indicator (MBTI). You can take a test to discover your type!", "There are many frameworks for understanding personality, such as MBTI, the Big Five, or Enneagram. Do you want more information on these?", "You can discover your personality type by taking a quiz based on models like MBTI or the Big Five personality traits."]
    },
    {
        "intent": "memory_boost",
        "questions": ["How can I improve my memory?", "Tips for boosting memory", "How do I enhance my memory?", "What helps with remembering things?", "Advice for better memory retention"],
        "answers": ["To improve memory, try techniques like repetition, visualization, and associating new information with something familiar.", "Boosting memory can involve regular mental exercises, staying organized, and getting plenty of sleep.", "For better memory, stay mentally active, manage stress, and maintain a healthy diet with plenty of antioxidants."]
    },
    {
        "intent": "mindfulness_practice",
        "questions": ["How can I practice mindfulness?", "Give me mindfulness tips", "What is mindfulness?", "How do I become more mindful?", "Best ways to stay present?"],
        "answers": ["Mindfulness is about being present in the moment. Practice by focusing on your breath, observing your surroundings, and staying non-judgmental about your thoughts.", "To practice mindfulness, start by dedicating a few minutes a day to focused breathing or meditation. Pay attention to the present moment without judgment.", "You can incorporate mindfulness into your daily routine by being fully engaged in everyday activities like eating, walking, or even washing dishes."]
    },
    {
        "intent": "gratitude_practice",
        "questions": ["How can I practice gratitude?", "Give me tips for being more grateful", "Ways to express gratitude", "How do I focus on the positive?", "Advice for practicing gratitude"],
        "answers": ["To practice gratitude, keep a journal and write down a few things you're thankful for each day. It helps shift focus to the positive aspects of life.", "Express gratitude by regularly acknowledging the people and things you appreciate in life. You can do this through words, actions, or simply reflecting on them.", "Gratitude can be cultivated by being mindful of the good in your life, thanking others often, and focusing on what you have rather than what you lack."]
    },
    {
        "intent": "learning_new_skill",
        "questions": ["How do I learn a new skill?", "What's the best way to master a new skill?", "Tips for picking up a new skill", "I want to learn something new", "Advice for learning quickly"],
        "answers": ["To learn a new skill, start by breaking it down into smaller, manageable parts and practice consistently.", "The best way to master a new skill is through deliberate practice, setting clear goals, and seeking feedback.", "Learning new skills requires patience and persistence. Try practicing regularly, watching tutorials, and applying what you learn in real-life scenarios."]
    },
    {
        "intent": "healthy_habits",
        "questions": ["How can I build healthy habits?", "What are some good habits to adopt?", "Tips for creating new habits", "How do I stick to healthy habits?", "Best ways to form a habit?"],
        "answers": ["Building healthy habits starts with setting small, achievable goals and being consistent. Over time, your brain forms new patterns.", "To form new habits, start small, stay consistent, and reward yourself for sticking with it. It helps to make your environment conducive to your goals.", "Healthy habits are best formed through repetition and gradual progression. Start with small, manageable changes and build up from there."]
    },
    {
        "intent": "overcoming_fear",
        "questions": ["How can I overcome fear?", "Tips for dealing with fear", "I want to conquer my fears", "How do I stop being afraid?", "Advice for overcoming anxiety"],
        "answers": ["Overcoming fear often starts by facing it gradually and practicing techniques like deep breathing, visualization, and self-affirmation.", "To deal with fear, identify what's causing it, take small steps toward confronting it, and use relaxation techniques to stay calm.", "Fear can be managed by breaking it down, addressing it one step at a time, and reminding yourself that it's natural to feel fear."]
    },
    {
        "intent": "overcoming_procrastination",
        "questions": ["How do I stop procrastinating?", "Tips for overcoming procrastination", "Why do I procrastinate?", "Advice for beating procrastination", "I need help with procrastination"],
        "answers": ["To overcome procrastination, try breaking tasks into smaller steps and setting specific, realistic goals.", "Procrastination can be reduced by prioritizing tasks, eliminating distractions, and rewarding yourself after completing small milestones.", "One way to beat procrastination is by starting with the easiest task to build momentum, or by using techniques like the Pomodoro method to stay focused."]
    },
    {
        "intent": "time_management",
        "questions": ["How can I manage my time better?", "Time management tips", "What's the best way to organize my time?", "Advice for managing my schedule", "How do I balance work and personal time?"],
        "answers": ["Good time management involves setting clear priorities, using tools like calendars or to-do lists, and breaking tasks into manageable chunks.", "To manage your time better, try time-blocking, where you allocate specific hours for focused work on each task.", "Effective time management requires planning ahead, avoiding multitasking, and giving yourself breaks to avoid burnout."]
    },
    {
        "intent": "public_speaking_confidence",
        "questions": ["How can I improve my public speaking?", "Tips for speaking confidently", "How do I get over stage fright?", "Advice for public speaking", "I want to speak in public without fear"],
        "answers": ["Improving public speaking confidence starts with practice and preparation. Familiarizing yourself with your content reduces anxiety.", "To speak confidently in public, try practicing in front of a mirror or recording yourself. This helps you refine your presentation and delivery.", "Overcoming stage fright involves deep breathing techniques, positive visualization, and rehearsing your speech to boost confidence."]
    },
    {
        "intent": "effective_studying",
        "questions": ["How can I study more effectively?", "Best study tips?", "What's the most efficient way to study?", "I need help with studying", "How do I retain information while studying?"],
        "answers": ["Effective studying involves active recall, spaced repetition, and breaking study sessions into shorter, focused periods.", "To study effectively, try summarizing information in your own words and teaching it to someone else. This reinforces your understanding.", "Using techniques like the Pomodoro method can help you focus for short bursts of time, followed by breaks, improving retention and productivity."]
    },
    {
        "intent": "stress_management",
        "questions": ["How can I manage stress?", "Tips for dealing with stress", "Advice for stress relief", "What helps with stress?", "I need stress management techniques"],
        "answers": ["Stress can be managed by practicing mindfulness, taking deep breaths, and engaging in physical activity to release tension.", "To manage stress, try journaling, listening to calming music, or spending time in nature. These activities help soothe the mind.", "Effective stress management includes staying organized, setting boundaries, and ensuring you take breaks to recharge throughout the day."]
    },
    {
        "intent": "improving_focus",
        "questions": ["How can I improve my focus?", "Tips for better concentration", "Advice for staying focused", "What helps with concentration?", "I need help focusing on tasks"],
        "answers": ["Improving focus requires minimizing distractions and setting specific goals for each work session. Try techniques like time-blocking or the Pomodoro method.", "Focus can be enhanced by eliminating digital distractions and creating a clean, organized workspace.", "To maintain concentration, take regular breaks and engage in activities like meditation, which helps train your brain to focus better."]
    },
    {
        "intent": "healthy_sleep_habits",
        "questions": ["How can I sleep better?", "Tips for improving sleep", "What are healthy sleep habits?", "I need advice for better sleep", "How do I get more restful sleep?"],
        "answers": ["To improve sleep, try maintaining a consistent sleep schedule, avoiding screens before bed, and creating a relaxing bedtime routine.", "Healthy sleep habits include keeping your bedroom cool, dark, and quiet, and avoiding caffeine or heavy meals close to bedtime.", "Practicing relaxation techniques like deep breathing or meditation before bed can help signal to your body that it's time to sleep."]
    },
    {
        "intent": "boosting_self_esteem",
        "questions": ["How can I boost my self-esteem?", "Tips for building self-confidence", "I want to feel more confident", "How do I improve my self-worth?", "Advice for boosting self-esteem"],
        "answers": ["Boosting self-esteem starts with practicing self-compassion and focusing on your strengths. Avoid comparing yourself to others.", "Building self-confidence can be achieved by setting small, achievable goals and celebrating your successes along the way.", "Improving self-esteem involves challenging negative thoughts and surrounding yourself with positive, supportive people."]
    },
    {
        "intent": "personal_growth",
        "questions": ["How can I grow as a person?", "Tips for self-improvement", "Advice for personal development", "How do I achieve personal growth?", "Ways to improve myself"],
        "answers": ["Personal growth involves setting goals, being open to learning new things, and reflecting on your experiences to gain insight.", "To foster personal development, focus on building healthy habits, surrounding yourself with positive influences, and stepping outside your comfort zone.", "Achieving personal growth is an ongoing process. Keep challenging yourself, learn from your mistakes, and celebrate your progress along the way."]
    },
    {
        "intent": "career_advice",
        "questions": ["Can you give me career advice?", "How do I grow in my career?", "Tips for career advancement", "I need help with my career path", "How can I succeed in my career?"],
        "answers": ["For career advancement, focus on continuous learning, networking, and setting clear, actionable goals for yourself.", "Career success often comes from being adaptable, seeking feedback, and developing skills that align with your goals.", "To grow in your career, take initiative, build strong relationships with colleagues, and always be open to new opportunities for learning and development."]
    },
    {
        "intent": "building_relationships",
        "questions": ["How can I build better relationships?", "Tips for improving relationships", "I want to strengthen my relationships", "How do I connect better with others?", "Advice for building strong relationships"],
        "answers": ["Building strong relationships requires good communication, active listening, and showing empathy and appreciation for others.", "To improve your relationships, make an effort to understand the other person's perspective, be open about your feelings, and resolve conflicts with respect.", "Fostering healthy relationships involves setting boundaries, being honest, and making time for the people who matter most to you."]
    },
    {
        "intent": "dealing_with_loss",
        "questions": ["How do I deal with loss?", "I need help coping with loss", "What are some tips for grieving?", "Advice for dealing with grief", "How can I cope with the loss of a loved one?"],
        "answers": ["Dealing with loss takes time. Allow yourself to grieve and don't be afraid to seek support from friends, family, or a counselor.", "Grieving is a personal process, but talking about your feelings, writing in a journal, or engaging in meaningful rituals can help.", "To cope with loss, be patient with yourself. It's okay to feel a wide range of emotions, and it's important to lean on your support system when needed."]
    },
    {
        "intent": "dealing_with_failure",
        "questions": ["How do I deal with failure?", "Tips for coping with failure", "I failed at something, how do I move on?", "Advice for handling failure", "How do I overcome failure?"],
        "answers": ["Failure is a part of learning. Reflect on what went wrong, identify lessons, and use the experience to improve for the future.", "Coping with failure involves reframing it as a growth opportunity and understanding that everyone faces setbacks at some point.", "To overcome failure, focus on what you can control and set new goals based on what you've learned from the experience."]
    },
    {
        "intent": "developing_emotional_intelligence",
        "questions": ["What is emotional intelligence?", "How can I improve my emotional intelligence?", "Why is emotional intelligence important?", "Tips for developing emotional intelligence", "How do I become more emotionally aware?"],
        "answers": ["Emotional intelligence is the ability to recognize, understand, and manage your emotions and the emotions of others.", "To develop emotional intelligence, practice self-awareness, empathy, and effective communication. Reflect on how your emotions affect your behavior.", "Improving emotional intelligence involves paying attention to how you react to stress, listening actively to others, and practicing emotional regulation techniques."]
    },
    {
        "intent": "coping_with_change",
        "questions": ["How do I cope with change?", "Tips for dealing with change", "How can I adapt to new situations?", "Advice for coping with life changes", "How do I manage transitions in life?"],
        "answers": ["Coping with change involves accepting uncertainty, staying flexible, and focusing on the opportunities that change can bring.", "Adapting to change requires maintaining a positive attitude, seeking support when needed, and breaking down new challenges into manageable steps.", "To navigate transitions, focus on what you can control, set realistic goals, and give yourself time to adjust to new circumstances."]
    },
    {
        "intent": "mindfulness_and_meditation",
        "questions": ["What is mindfulness?", "How do I practice mindfulness?", "Benefits of meditation?", "How can I get started with meditation?", "Tips for being more mindful"],
        "answers": ["Mindfulness is the practice of staying present and fully engaging in the current moment without judgment.", "To practice mindfulness, try deep breathing, body scans, or focusing on your senses to ground yourself in the present.", "Meditation can help reduce stress, improve focus, and enhance emotional well-being. Start with a few minutes each day and gradually increase the duration as you get more comfortable."]
    },
    {
        "intent": "improving_communication_skills",
        "questions": ["How can I communicate better?", "Tips for improving communication skills", "I want to be a better communicator", "How do I express myself clearly?", "Advice for effective communication"],
        "answers": ["Effective communication involves active listening, clear expression of your thoughts, and considering the other person's perspective.", "To improve communication skills, practice speaking confidently, maintaining eye contact, and asking open-ended questions to encourage dialogue.", "Good communication requires being mindful of nonverbal cues, staying calm during difficult conversations, and being open to feedback."]
    },
    {
        "intent": "goal_setting_and_achievement",
        "questions": ["How can I set achievable goals?", "Tips for setting goals", "How do I achieve my goals?", "I need help with goal setting", "Advice for reaching my goals"],
        "answers": ["To set achievable goals, use the SMART framework: Specific, Measurable, Achievable, Relevant, and Time-bound.", "Breaking down your goals into smaller steps makes them more manageable and helps you track progress over time.", "Achieving your goals requires discipline, regular reflection, and adjusting your plan when necessary. Celebrate small victories along the way to stay motivated."]
    },
    {
        "intent": "building_resilience",
        "questions": ["How can I become more resilient?", "Tips for building resilience", "How do I bounce back from setbacks?", "Advice for developing resilience", "What helps with building mental toughness?"],
        "answers": ["Resilience involves maintaining a positive mindset, focusing on your strengths, and using setbacks as learning opportunities.", "Building resilience requires practicing self-care, staying connected with supportive people, and keeping a long-term perspective on challenges.", "To bounce back from adversity, practice gratitude, develop problem-solving skills, and stay flexible in the face of change."]
    },
    {
        "intent": "managing_anxiety",
        "questions": ["How do I manage anxiety?", "Tips for reducing anxiety", "What helps with anxiety?", "I need help with anxiety", "How can I calm myself when anxious?"],
        "answers": ["Managing anxiety involves grounding techniques like deep breathing, mindfulness, and focusing on the present moment.", "To reduce anxiety, identify and challenge irrational thoughts, avoid excessive stress, and take breaks to recharge your mind.", "Calming yourself when anxious can be achieved through progressive muscle relaxation, journaling your thoughts, or engaging in physical activity to release tension."]
    },
    {
        "intent": "improving_memory",
        "questions": ["How can I improve my memory?", "Tips for better memory", "What helps with memory retention?", "I need to boost my memory", "How do I remember things better?"],
        "answers": ["Improving memory can be achieved through regular mental exercises, such as puzzles or learning new skills, to keep your brain active.", "To retain information better, try using mnemonic devices, visualizing concepts, and breaking information into smaller chunks.", "Memory improvement also involves maintaining a healthy lifestyle, including regular sleep, proper nutrition, and staying physically active."]
    },
    {
        "intent": "developing_grit",
        "questions": ["What is grit?", "How can I develop more grit?", "I want to be more persistent", "Tips for building mental strength", "How do I keep going despite challenges?"],
        "answers": ["Grit is the combination of passion and perseverance that helps you pursue long-term goals despite obstacles.", "To develop grit, stay focused on your goals, embrace challenges as learning experiences, and maintain a growth mindset.", "Building mental strength involves staying committed to your purpose, practicing patience, and learning to overcome setbacks with determination."]
    },
    {
        "intent": "self_reflection",
        "questions": ["How can I reflect on myself?", "What are some self-reflection techniques?", "Why is self-reflection important?", "How do I become more self-aware?", "Tips for self-reflection"],
        "answers": ["Self-reflection involves taking time to think deeply about your thoughts, feelings, and actions, and how they align with your values.", "To practice self-reflection, try journaling, meditating, or asking yourself open-ended questions about your experiences.", "Self-awareness is enhanced through regular self-reflection, which can help you make more informed decisions and grow as a person."]
    },
    {
        "intent": "letting_go_of_perfectionism",
        "questions": ["How can I stop being a perfectionist?", "Tips for letting go of perfectionism", "How do I overcome perfectionism?", "I need help with perfectionism", "Why is perfectionism holding me back?"],
        "answers": ["Letting go of perfectionism involves accepting that making mistakes is a natural part of growth and that aiming for 'good enough' is often more productive than seeking perfection.", "Overcoming perfectionism requires challenging unrealistic expectations and focusing on progress rather than flawless outcomes.", "Perfectionism can be managed by practicing self-compassion, setting realistic goals, and learning to celebrate your achievements, even when they aren't perfect."]
    }]
# Example usage
chatbot = UnsupervisedChatbot(intents_data)
chatbot.interactive_session()