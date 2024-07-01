from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http import HttpResponseRedirect
import sentencepiece
from django.views.decorators.csrf import csrf_exempt
import re
import random
from django.shortcuts import render
import requests
from newspaper import Article
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer
from .models import ChatHistory

R_EATING = "I don't like eating anything because I'm a bot obviously!"
R_ADVICE = "If I were you, I would go to the internet and type exactly what you wrote there!"

def unknown():
    response = ["Could you please re-phrase that? ",
                "...",
                "Sounds about right.",
                "What does that mean?"][
        random.randrange(4)]
    return response

def HomePage(request):
    return render(request,'login.html',{})

from django.db import IntegrityError
from django.contrib.auth.models import User

def Register(request):
    if request.method == 'POST':
        fname = request.POST['fname']
        lname = request.POST['lname']
        username = request.POST['use']
        email = request.POST['email']
        password = request.POST['pws']
    
        try:
            new_user = User.objects.create_user(username, email, password)
            new_user.first_name = fname
            new_user.last_name = lname
            new_user.save()
            return redirect('login-page')
        except IntegrityError:
            error_message = "Username already exists. Please choose a different username."
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html', {})

def Login(request):
    if request.method == 'POST':
        name=request.POST['use']
        password = request.POST['pws']

        User=authenticate(username=name,password=password)
        if User is not None:
            login(request,User)
            return render(request, 'index.html', {'username': User.username})
        else:
            return HttpResponse('Error user does not exist')

    return render(request,'login.html',{})

def logoutuser(request):
    logout(request)
    return redirect('login-page')


def message_probability(user_message, recognised_words, single_response=False, required_words=[]):
    message_certainty = 0
    has_required_words = True

    # Counts how many words are present in each predefined message
    for word in user_message:
        if word in recognised_words:
            message_certainty += 1

    # Calculates the percent of recognised words in a user message
    percentage = float(message_certainty) / float(len(recognised_words))

    # Checks that the required words are in the string
    for word in required_words:
        if word not in user_message:
            has_required_words = False
            break

    # Must either have the required words, or be a single response
    if has_required_words or single_response:
        return int(percentage * 100)
    else:
        return 0


import random

def check_all_messages(message):
    highest_prob_list = {}

    # Simplifies response creation / adds it to the dict
    def response(bot_response, list_of_words, single_response=False, required_words=[]):
        nonlocal highest_prob_list
        highest_prob_list[bot_response] = message_probability(message, list_of_words, single_response, required_words)
    help_you_words = [
        "What can I help you with?",
        "What's on your mind?",
    ]
    
    # Randomly select one response
    selected_words = random.choice(help_you_words)
    
    # Add the response to the highest_prob_list
    response(selected_words, ['hello', 'hi', 'hey', 'sup', 'heyo','letsstart','again','restart','oncemore','start'], single_response=True)



    ms1 = [
        "I'm doing well, thanks for asking. ",
        "Going good, thanks.",
        "Things are going alright. ",
        "It's going pretty well, thanks.", 
        "Feeling pretty good today. ",
        "Doing alright, thanks.",
    ]
    
    # Randomly select one response
    sw1 = random.choice(ms1)
    
    # Add the response to the highest_prob_list
    response(sw1, ['how', 'are', 'you', 'doing','is','it','going'], single_response=True)

    bye_responses = [
        "Goodbye! Take care.",
        "See you later!",
        "Bye for now!",
        "Catch you later!",
        "Until next time!",
        "Farewell!",
        "Adios!",
    ]
    selected_response = random.choice(bye_responses)
        # Add the response to the highest_prob_list
    response(selected_response, ['bye', 'goodbye', 'see you', 'farewell'], single_response=True)

    thank_you_responses = [
        "You're welcome!",
        "Happy to help!",
        "Glad I could assist!",
        "Anytime!",
        "You got it!",
    ]
    selected_response = random.choice(thank_you_responses)
        # Add the response to the highest_prob_list
    response(selected_response, ['thank', 'thanks', 'thankyou'], single_response=True)

    compliment_responses = [
    "Thank you for the compliment!",
    "I appreciate your kind words!",
    "It's great to hear that you're satisfied with my performance!",
    "I'm glad I could meet your expectations!",
    "Your feedback means a lot to me!",
]
    selected_response = random.choice(compliment_responses)
    # Add the response to the highest_prob_list
    response(selected_response, ['great job', 'well done', 'awesome', 'excellent'],single_response=True)
    update_responses = [
    "Sure, let me check for updates.",
    "Let me see if there are any updates available.",
    "I'll look into that for you. One moment please.",
    "I'll check and get back to you with any updates.",
]

    selected_response = random.choice(update_responses)
    # Add the response to the highest_prob_list
    response(selected_response, ['update', 'updates', 'any news','any updates'],single_response=True)

    # Longer responses
    response(R_ADVICE, ['give', 'advice'], required_words=['advice'])
    response(R_EATING, ['what', 'you', 'eat'], required_words=['you', 'eat'])

    # Check if "Paragraph Bites" is in the message (case-insensitive)
    if any("paragraphbites" in word.lower() for word in message):
        return random.choice([        
        "Share your literary gem here!",
        "Let's dive into your paragraph, drop it like it's hot!",
        "Time to unveil your paragraph masterpiece!",
        "Got a paragraph brewing? Pour it out here!",
        "Showcase your paragraph prowess!",
        
        ])

    # Check if "Article Appetizer" is in the message (case-insensitive)
    if any("articleappetizer" in word.lower() for word in message):
        return random.choice([
    "Share the web address with us",
    "Got a link to drop? Paste it here!",
    "Time to unveil the magic of your URL! Share it here!",
    "Ready to guide us to the digital wonderland? Paste the URL!",
    "Let's make the internet come alive! Share your URL here!",
        "We're curious! Drop that URL in the box below!",
    "Got a link that's worth a click? Share it here!",
    "Ready to dazzle us with a link? Paste it here!",
    "Unlock the digital treasure! Share your URL here!",
    "Link us up! Paste the URL and let the journey begin!",
        ])
    
    best_match = max(highest_prob_list, key=highest_prob_list.get)
    return unknown() if highest_prob_list[best_match] < 1 else best_match

def summarize(text, per):
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)
    tokens = [token.text for token in doc]
    word_frequencies = {}
    for word in doc:
        if word.text.lower() not in STOP_WORDS and word.text.lower() not in punctuation:
            if word.text not in word_frequencies.keys():
                word_frequencies[word.text] = 1
            else:
                word_frequencies[word.text] += 1
    
    max_frequency = max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word] = word_frequencies[word] / max_frequency
    
    sentence_tokens = [sent for sent in doc.sents]
    sentence_scores = {}
    for sent in sentence_tokens:
        for word in sent:
            if word.text.lower() in word_frequencies.keys():
                if sent not in sentence_scores.keys():
                    sentence_scores[sent] = word_frequencies[word.text.lower()]
                else:
                    sentence_scores[sent] += word_frequencies[word.text.lower()]
    
    select_length = int(len(sentence_tokens) * per)
    summary = nlargest(select_length, sentence_scores, key=sentence_scores.get)
    final_summary = [word.text for word in summary]
    summary = ' '.join(final_summary)
    return summary

def process_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            article = Article(url)
            article.download(input_html=response.text)
            article.parse()
            return summarize(article.text, 0.05)
        else:
            return 'Error: The URL is not accessible (Status Code {}).'.format(response.status_code)
    except requests.RequestException as e:
        return 'An error occurred: {}'.format(str(e))


def generate_summary(text):
    # Load pre-trained T5 model and tokenizer
    model_name = "t5-base"
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)

    # Tokenize input text
    inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=512, truncation=True)

    # Generate summary
    summary_ids = model.generate(inputs, max_length=150, min_length=40, length_penalty=2.0, num_beams=4, early_stopping=True)

    # Decode the summary
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary


# Used to get the response
def get_response(user_input):
    # Count the number of words in the user input
    word_count = len(user_input.split())
    
    # If word count is greater than 20, call the summary function
    if word_count > 20:
        response = generate_summary(user_input)
    else:
        split_message = re.split(r'\s+|[,;?!.-]\s*', user_input.lower())
        if user_input.startswith("https://"):
            # Extract the URL from the user input
            url = user_input.strip()  # Assuming the URL is the entire message
            # Call the function to process the URL
            response = process_url(url)
        else:
            response = check_all_messages(split_message)
    return response

    # Testing the response system
def chatbot(request):    
    username = request.user.username
    if request.method == 'POST':
        # Get the user input from the form
        msg = request.POST.get('msg', '')
        message=get_response(msg)
        print(message)
        chat = ChatHistory(user=request.user, message="message:"+msg ,response="response:"+message)
        chat.save()
        return render(request, 'chatbot.html', {'username': username,'message': message})
    return render(request, 'chatbot.html',{'username': username})

def index(request):
        return render(request, 'index.html', {})

def history(request):
    # Retrieve chat history for the logged-in user
    username = request.user.username
    chat_history = ChatHistory.objects.filter(user=request.user)
    return render(request, 'history.html', {'username': username, 'chat_history': chat_history})
