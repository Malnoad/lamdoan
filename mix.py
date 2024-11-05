from flask import Flask
from nicegui import ui
import os
import threading
from functools import partial

app = Flask(__name__)

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
                        stories[current_title] = {
                            "content": current_content,
                            "questions": current_questions
                        }

                    current_title = line[6:].strip()
                    current_content = []
                    current_questions = []  # Reset for new story
                elif line.startswith("Question:"):
                    question_text = line[9:].strip()
                    try:
                        options = next(file).strip().split(';')  # Expect options on the next line
                        answer = next(file).strip()  # Expect the correct answer on the line after options
                        current_questions.append({
                            "question": question_text,
                            "options": options,
                            "answer": answer
                        })
                    except StopIteration:
                        print(f"Error: Incomplete question data for '{question_text}'.")
                        break  # Stop processing further questions
                else:
                    current_content.append(line)

            if current_title and current_content:
                stories[current_title] = {
                    "content": current_content,
                    "questions": current_questions
                }

    except FileNotFoundError:
        print(f"File {filename} not found.")
    return stories

# Function to load stories from multiple files
def load_stories_from_multiple_files(filenames):
    all_stories = {}
    for filename in filenames:
        file_stories = load_stories_from_file(filename)
        if file_stories:  # Only add if there are valid stories
            all_stories.update(file_stories)
        else:
            print(f"No valid stories found in {filename}.")
    print("Loaded Stories:", all_stories)  # Debug print to verify loaded stories
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
    story = stories.get(story_title, None)
    if story:
        story_content = story["content"]
        story_questions = story["questions"]
        content_label.set_text(f"Story: {story_title}\n\n" + "\n".join(story_content))
        options.clear()  # Clear previous options

        # Pass the specific questions for this story
        show_exercise(story_questions)
    else:
        print(f"Story '{story_title}' not found in loaded stories.")

# Function to dynamically create a check_answer function for each question with separate feedback
def create_check_answer_function(question_item, feedback_label):
    def check_answer(user_answer):
        correct_answer = question_item["answer"]
        if user_answer.lower() == correct_answer.lower():
            feedback_label.set_text("Correct!")  # Separate the method calls
            feedback_label.classes('text-lg text-green-500')
        else:
            feedback_label.set_text(f"Incorrect! The correct answer was: {correct_answer}")
            feedback_label.classes('text-lg text-red-500')
    return check_answer

# Update show_exercise to receive the questions for the current story
def show_exercise(story_questions):
    options.clear()  # Clear previous options

    # Display each question in the story
    for question_item in story_questions:
        with options:
            ui.label(question_item["question"]).classes('text-xl mb-2')  # Question text
            
            # Create a dropdown (select) menu with the options and feedback directly below
            with ui.column().classes('w-full mb-2'):
                feedback_label = ui.label('').classes('text-lg mt-2')  # Separate label for each feedback below the select
                check_answer_function = create_check_answer_function(question_item, feedback_label)
                ui.select(
                    options=question_item["options"],  # List of options
                    label='Choose an answer',
                    on_change=lambda e, check_func=check_answer_function: check_func(e.value)  # Call the specific check_answer function
                ).classes('w-full mb-2')  # Add spacing between questions and feedback

                # Position the feedback label immediately below the dropdown menu
                feedback_label.classes('text-lg mt-2')  # Adds spacing between answer and feedback


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
        # Dynamically create buttons for each story using titles instead of filenames
        for story_title in stories.keys():
            ui.button(story_title, on_click=partial(show_story, story_title)).classes('w-full')
    with ui.column().classes('w-3/4 p-4'):
        content_label = ui.label('Select a story to read.').classes('text-lg')
        options = ui.column().classes('mt-4')  # Container for options (radio buttons)

# Function to run Flask in a separate thread
def run_flask():
    app.run(port=5000)

# Run Flask in a separate thread to avoid blocking NiceGUI
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

# Run the NiceGUI UI
ui.run()
