from flask import Flask, render_template, request, jsonify
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer
import requests

app = Flask(__name__)

# Initialize chatbot with logic adapter
bot = ChatBot("chatbot", read_only=False, logic_adapters=[
    {
        "import_path": "chatterbot.logic.BestMatch",
        "default_response": "Sorry, I don't understand that yet.",
        "maximum_similarity_threshold": 0.90
    }
])

# Train with default corpus
corpus_trainer = ChatterBotCorpusTrainer(bot)
corpus_trainer.train("chatterbot.corpus.english")

# Custom conversational training
custom_convos = [
    "hello", "hi there!",
    "hi", "hi there!",
    "What is your name?", "I am WeatherBot, your weather assistant.",
    "Who created you?", "I was created by Vishwas Choudhary.",
    "Tell me a joke", "Why did the sun go to school? To get a little brighter!",
    "How are you?", "I'm great! Ready to help with weather and questions.",
    "What can you do?", "I can give you real-time weather updates and chat with you.",
    "What's the capital of India?", "The capital of India is New Delhi.",
    "Thank you", "You're welcome!",
    "Bye", "Goodbye! Have a sunny day ☀️"
]

list_trainer = ListTrainer(bot)
list_trainer.train(custom_convos)

# Home route
@app.route("/")
def index():
    return render_template("index.html")

# Chat route
@app.route("https://weather-chatbot.onrender.com/get")
def get_response():
    user_msg = request.args.get("userMessage")

    try:
        # Try weather lookup only for short messages (likely city names)
        if len(user_msg.split()) <= 3:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={user_msg}&appid=2c9bf91950bd2902df3be629ab2bfe1d&units=metric"
            res = requests.get(url)
            data = res.json()

            if data.get("cod") == 200:
                return jsonify({
                    "weather": True,
                    "city": data["name"],
                    "temp": data["main"]["temp"],
                    "desc": data["weather"][0]["description"],
                    "humidity": data["main"]["humidity"],
                    "icon": data["weather"][0]["icon"]
                })

        # If not weather, fallback to chatbot
        response = str(bot.get_response(user_msg))
        return jsonify({"weather": False, "text": response})

    except Exception as e:
        return jsonify({"weather": False, "text": "Sorry, something went wrong."})

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
