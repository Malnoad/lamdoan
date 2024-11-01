from flask import Flask
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
    # Additional questions can be added here...
]

# Function to load stories from a single file
def load_stories_from_file(filename):
    stories = {}
    try:
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

    except FileNotFoundError:
        print(f"File {filename} not found.")
    return stories

# Function to load stories from multiple files
def load_stories_from_multiple_files(filenames):
    all_stories = {}
    for filename in filenames:
        file_stories = load_stories_from_file(filename)
        all_stories.update(file_stories)
    return all_stories

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
    story_content, story_questions = stories.get(story_title, ([], []))
    content_label.set_text(f"Story: {story_title}\n\n" + "\n".join(story_content))
    answer_label.set_text('')  # Clear previous answer feedback
    question_label.set_text('')  # Clear previous question
    options.clear()  # Clear previous options

    # Generate a new random question for the story
    show_exercise()

# Function to show a random question and its options
def show_exercise():
    # Select a random question from the questions_data
    question_item = random.choice(questions_data)
    question_label.set_text(question_item["question"])  # Display the question
    
    # Clear previous options
    options.clear()

    # Create a dropdown (select) menu with the options
    with options:
        ui.select(
            options=question_item["options"],  # List of options
            label='Choose an answer',
            on_change=lambda e: check_answer(e.value, question_item)
        ).classes('w-full')

# Function to check the user's answer
def check_answer(user_answer, question_item):
    correct_answer = question_item["answer"]
    if user_answer.lower() == correct_answer.lower():
        answer_label.set_text("Correct!").classes('text-lg text-green-500')
    else:
        answer_label.set_text(f"Incorrect! The correct answer was: {correct_answer}").classes('text-lg text-red-500')



# Main UI layout
with ui.row().classes('w-full'):
    with ui.column().classes('w-1/4 p-4'):
        ui.label('Type of Content').classes('text-2xl')
        ui.separator()
        ui.link('Short Stories', '/short-stories')
        ui.link('Articles', '/articles')
        ui.link('News', '/news')

    with ui.column().classes('w-3/4 p-4'):
        content_label = ui.label('Select a category from the sidebar to begin reading.').classes('text-lg')

with ui.row().classes('w-full mt-4'):
    with ui.column().classes('w-1/4 p-4'):
        ui.label('List of Stories').classes('text-2xl')
        ui.separator()
        # Dynamically create buttons for each story
        for story in stories.keys():
            ui.button(story, on_click=lambda name=story: show_story(name)).classes('w-full')
    with ui.column().classes('w-3/4 p-4'):
        content_label = ui.label('Select a story to read.').classes('text-lg')
        options = ui.column().classes('mt-4')  # Container for options (radio buttons)

# Question and answer section
with ui.row().classes('w-full mt-4'):
    with ui.column().classes('w-3/4 p-4'):
        question_label = ui.label('').classes('text-xl')  # Label for the question
        options = ui.column().classes('mt-4')  # Container for options (radio buttons)
        answer_label = ui.label('').classes('text-lg text-green-500')  # Feedback for the selected answer


# Function to run Flask in a separate thread
def run_flask():
    app.run(port=5000)

# Run Flask in a separate thread to avoid blocking NiceGUI
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

# Run the NiceGUI UI
ui.run()
