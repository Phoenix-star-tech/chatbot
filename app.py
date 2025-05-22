from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import re
import random

app = Flask(__name__)

# Memory (context chaining for current session)
chat_context = {}

# Smart typo corrections
corrections = {
    r"\bprimester\b": "prime minister",
    r"\bmodi ji\b": "narendra modi",
    r"\bindian leaders\b": "leaders of india",
    r"\bwhats\b": "what is",
    r"\bwht\b": "what",
    r"\btmie\b": "time",
    r"\bnam\b": "name",
    r"\bpls\b|\bplease\b": "",
    r"\bcan you\b|\bcould you\b": "",
    r"\bumm+\b": "",
    r"\bam\b": "i am",
    r"\bgogle\b": "google",
    r"\brecpie\b": "recipe",
    r"\bweathr\b": "weather",
    r"\bi m\b": "i am",
    r"\bim\b": "i am",
    r"\bu\b": "you",
    r"\br u\b": "are you",
}

# Emotion responses
emotion_responses = {
    "i am sad": "I'm really sorry you're feeling this way 💔. I'm always here to talk.",
    "i'm happy": "That's amazing to hear! 🥳 Keep shining!",
    "i feel lonely": "You're not alone anymore, I'm right here 💙 Want to chat?",
    "i'm angry": "That's okay. We all get upset. Want to vent a bit?",
    "i am bored": "Wanna hear a joke or need something fun to search?",
    "i love you": "Aww, I love you too 💖 You're amazing!",
    "i hate you": "That's okay... I'm just a bot. But I still like you 💙",
    "i am tired": "Take a deep breath and maybe get some rest 💤 You deserve it!",
    "i feel anxious": "Everything will be okay 🤗 Let’s talk about it?",
    "i feel stressed": "Take a deep breath... I'm here with you 💆‍♀️",
}

greetings = ["hi", "hello", "hey", "good morning", "good evening", "good afternoon"]
farewells = ["bye", "see you", "take care", "good night"]

# Clean message
def clean_message(message):
    message = message.lower().strip()
    for pattern, replacement in corrections.items():
        message = re.sub(pattern, replacement, message)
    return message

# Search web using DuckDuckGo
def search_web(query):
    try:
        search_term = query.replace("search ", "").replace("what is ", "").replace("who is ", "").replace("tell me about ", "").strip()
        if not search_term:
            return "Hmm... what exactly should I look up? 🤔"
        
        url = f"https://api.duckduckgo.com/?q={search_term}&format=json"
        res = requests.get(url)
        data = res.json()

        if data.get("AbstractText"):
            return data["AbstractText"]

        for topic in data.get("RelatedTopics", []):
            if isinstance(topic, dict) and topic.get("Text"):
                return topic["Text"]

        return f"I didn’t find a direct answer, but this might help: https://duckduckgo.com/?q={search_term} 🌐"
    except Exception as e:
        return f"Oops! Something went wrong while searching 😢: {str(e)}"

# Generate a smart chatbot response
def get_response(message, user_id="default"):
    message = clean_message(message)

    # Simulate context
    last = chat_context.get(user_id, {}).get("last", "")

    # Save context
    chat_context.setdefault(user_id, {})["last"] = message

    # Emotional support
    for emotion, reply in emotion_responses.items():
        if emotion in message:
            return reply

    # Greetings
    if any(greet in message for greet in greetings):
        return random.choice([
            "Hey there! 😊", "Hello! 👋 What’s on your mind?",
            "Hi! I'm all ears 👂", "Yo! What's up?"
        ])

    # Farewells
    if any(bye in message for bye in farewells):
        return random.choice([
            "Bye bye! 👋 Stay awesome.", "Catch you later!",
            "Take care and ping me anytime!", "Logging out emotionally... 💻❤️"
        ])

    # Small Talk / Memory Reference
    if "you remember" in message:
        if last:
            return f"You said: '{last}' — let's continue from there!"
        else:
            return "Hmm... I don't remember anything yet 🧠"

    # Common Questions
    if "how are you" in message:
        return "I'm charged up ⚡ and ready to chat! How are you feeling?"

    if "your name" in message or "who are you" in message:
        return "I'm your AI assistant, smarter than Siri, and always here for you 💬🤖"

    if "joke" in message:
        return random.choice([
            "Why don’t robots panic? Because they always keep their cool circuits.",
            "I'm reading a book on anti-gravity. It's impossible to put down! 😂",
            "Why did the computer get cold? Because it left its Windows open!",
            "Why was the computer tired when it got home? It had too many tabs open! 🧠💻"
        ])

    if "time" in message:
        return f"The current time is {datetime.now().strftime('%H:%M:%S')} ⏰"
    
    if "date" in message or "today" in message:
        return f"Today is {datetime.now().strftime('%A, %B %d, %Y')} 📅"

    # Explicit or vague search
    if message.startswith(("search ", "what is ", "who is ", "tell me about ")):
        return search_web(message)
    
    if len(message.split()) <= 4:
        return search_web("search " + message)

    # Default to smart search
    return search_web(message)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    user_id = request.remote_addr  # Basic user ID tracking
    response = get_response(user_message, user_id=user_id)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
