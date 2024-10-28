from flask import Flask, jsonify, request
from nicegui import ui
import os
import threading
import random

app = Flask(__name__)

# Predefined list of questions and their options
questions_data = [
    {
        "question": "What use for constellations is NOT mentioned in the opening paragraphs?",
        "options": [
            "To help people find their way",
            "To understand the origins of life in the universe",
            "To provide entertainment",
            "To allow people to orientate themselves"
        ],
        "answer": "To understand the origins of life in the universe"
    },
    {
        "question": "What is the best meaning of the word 'sparse' in the second paragraph?",
        "options": [
            "rare",
            "boring",
            "painful",
            "limited"
        ],
        "answer": "boring"
    },
    {
        "question": "Why do constellations change in the sky from month to month?",
        "options": [
            "Because of passing fashions",
            "Because of the weather",
            "Because the Earth's movements",
            "Because stars are always moving"
        ],
        "answer": "Because the Earth's movements"
    },
    {
        "question": "Why do astronomers call the constellation 'Ursa Major' by this name?",
        "options": [
            "To ease international communication",
            "Because the Russians insisted",
            "Because Russia provides much of the finance for these organisations",
            "They decided that's what it most looks like"
        ],
        "answer": "To ease international communication"
    },
    {
        "question": "What point is being made in the penultimate paragraph?",
        "options": [
            "Stars used to be closer together",
            "The stars look different depending on where you are standing",
            "You won't see stars well under street lights",
            "Perspective makes stars seem closer"
        ],
        "answer": "Perspective makes stars seem closer"
    },
    {
        "question": "Where would you most likely find this text?",
        "options": [
            "A scholarly publication",
            "A newspaper",
            "A children's encyclopedia",
            "A political leaflet"
        ],
        "answer": "A children's encyclopedia"
    }
]

# Function to load stories from a single file
def load_stories_from_file(filename):
    stories = {}
    with open(filename, 'r', encoding='utf-8') as file:
        current_title = None
        current_content = []
        current_questions = []

        for line in file:
            line = line.strip()
            if not line:
                continue  # Skip empty lines

            if line.startswith("Title:"):
                if current_title and current_content:
                    stories[current_title] = (current_content, current_questions)

                current_title = line[6:].strip()
                current_content = []
                current_questions = []  # Reset for new story
            elif line.startswith("Question:"):
                current_questions.append(line[9:].strip())  # Store the question
            else:
                current_content.append(line)
        
        if current_title and current_content:
            stories[current_title] = (current_content, current_questions)

    return stories

# Function to load stories from multiple files
def load_stories_from_multiple_files(filenames):
    all_stories = {}
    for filename in filenames:
        file_stories = load_stories_from_file(filename)
        all_stories.update(file_stories)
    return all_stories

# Automatically load stories from the specified files
current_dir = os.path.dirname(os.path.abspath(__file__))  # Get the current directory
file_list = [
    os.path.join(current_dir, 'alo.txt'),
    os.path.join(current_dir, 'alo1.txt'),
    os.path.join(current_dir, 'alo2.txt'),
    os.path.join(current_dir, 'alo3.txt')
]
stories = load_stories_from_multiple_files(file_list)

# Function to display the selected story
def show_story(story_title):
    story_content, _ = stories.get(story_title, (['Story not found'], []))
    content_label.set_text("\n".join(story_content))  # Set the story content
    answer_label.set_text('')  # Clear previous answer feedback
    question_label.set_text('')  # Clear question label
    options.clear()  # Clear previous options

    # Generate a question for the story
    show_exercise()

# Function to show a random question and its options
def show_exercise():
    # Select a random question from the questions_data
    question_item = random.choice(questions_data)
    question_label.set_text(question_item["question"])  # Display the question
    options.clear()  # Clear previous options

    for option in question_item["options"]:
        ui.radio(option, value=option, on_change=lambda value=option, question=question_item["question"]: check_answer(value, question_item)).classes('w-full')

# Function to check the user's answer
def check_answer(user_answer, question_item):
    correct_answer = question_item["answer"]
    if user_answer.lower() == correct_answer.lower():
        answer_label.set_text("Correct!")
    else:
        answer_label.set_text(f"Incorrect! The correct answer was: {correct_answer}")

# Main UI layout
with ui.row().classes('w-full'):
    with ui.column().classes('w-1/4 p-4'):
        ui.label('Type of paragraph').classes('text-2xl')
        ui.separator()
        ui.link('Short stories', '/short-stories')
        ui.link('Articles', '/articles')
        ui.link('News', '/news')

    with ui.column().classes('w-3/4 p-4'):
        content_label = ui.label('Select a category from the sidebar to begin reading.')

with ui.row().classes('w-full mt-4'):
    with ui.column().classes('w-1/4 p-4'):
        ui.label('List of articles').classes('text-2xl')
        ui.separator()
        for title in stories:
            ui.button(title, on_click=lambda title=title: show_story(title)).classes('w-full')
    with ui.column().classes('w-3/4 p-4'):
        content_label = ui.label('Select a story to read.')

        options = ui.column().classes('mt-4')  # Container for question options

# Question and answer section
with ui.row().classes('w-full mt-4'):
    with ui.column().classes('w-1/4 p-4'):
        ui.label('Question and answer')
        ui.separator()
        question_label = ui.label('').classes('text-2xl')  # Initially empty
        answer_label = ui.label('').classes('text-lg')  # Feedback for answers

# Function to run Flask in a separate thread
def run_flask():
    app.run(port=5000)

# Run Flask in a separate thread to avoid blocking NiceGUI
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

# Run the UI
ui.run()
