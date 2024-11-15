from flask import Flask
from nicegui import ui
import os
import threading
from functools import partial

app = Flask(__name__)

# A simple dictionary to track progress (could be stored in a database)
user_progress = {}

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
                        # Store using a unique ID but keep the title separate
                        unique_id = f"{filename}_{current_title}"
                        stories[unique_id] = {
                            "display_title": current_title,  # Display only the title
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
                unique_id = f"{filename}_{current_title}"
                stories[unique_id] = {
                    "display_title": current_title,
                    "content": current_content,
                    "questions": current_questions
                }

    except FileNotFoundError:
        print(f"File {filename} not found.")
    return stories

# Load stories from files and categorize
current_dir = os.path.dirname(os.path.abspath(__file__))
beginner_files = ['alo.txt', 'alo1.txt', 'alo2.txt']
intermediate_files = ['alo3.txt', 'alo4.txt', 'alo5.txt']

# Separate stories based on category
beginner_stories = {}
intermediate_stories = {}

for filename in beginner_files + intermediate_files:
    full_path = os.path.join(current_dir, filename)
    file_stories = load_stories_from_file(full_path)
    if filename in beginner_files:
        beginner_stories.update(file_stories)
    elif filename in intermediate_files:
        intermediate_stories.update(file_stories)

# Function to track progress
def tracking_progress(user_id, story_id, question_id=None, answer=None):
    if user_id not in user_progress:
        user_progress[user_id] = {}

    if story_id not in user_progress[user_id]:
        user_progress[user_id][story_id] = {"status": "in_progress", "questions_answered": {}}

    # If question is answered, track it
    if question_id is not None and answer is not None:
        user_progress[user_id][story_id]["questions_answered"][question_id] = answer

    print(f"User {user_id} progress: {user_progress[user_id]}")  # For debugging

# Function to display the selected story
def show_story(user_id, story_id):
    story = beginner_stories.get(story_id) or intermediate_stories.get(story_id)
    if story:
        story_content = story["content"]
        story_questions = story["questions"]
        content_label.set_text(f"Story: {story['display_title']}\n\n" + "\n".join(story_content))
        options.clear()  # Clear previous options

        # Track progress for user
        tracking_progress(user_id, story_id)

        # Pass the specific questions for this story
        show_exercise(user_id, story_questions)
    else:
        print(f"Story with ID '{story_id}' not found in loaded stories.")

# Function to dynamically create a check_answer function for each question with separate feedback
def create_check_answer_function(user_id, story_id, question_item, feedback_label):
    def check_answer(user_answer):
        correct_answer = question_item["answer"]

        # Track the answer in progress
        tracking_progress(user_id, story_id, question_item["question"], user_answer)

        # Reset the feedback label each time an answer is selected
        feedback_label.set_text("")  # Clear the text
        feedback_label.classes('text-lg')  # Reset to base text class without color

        # Set feedback based on correctness of the answer
        if user_answer.lower() == correct_answer.lower():
            feedback_label.set_text("Correct!")
            feedback_label.classes('text-lg text-green-500')  # Green for correct answer
        else:
            feedback_label.set_text(f"Incorrect! The correct answer was: {correct_answer}")
            feedback_label.classes('text-lg text-red-500')  # Red for incorrect answer

    return check_answer

# Update show_exercise to receive the questions for the current story
def show_exercise(user_id, story_questions):
    options.clear()  # Clear previous options

    # Display each question in the story
    for question_item in story_questions:
        with options:
            ui.label(question_item["question"]).classes('text-xl mb-2')  # Question text
            
            # Create a dropdown (select) menu with the options and feedback directly below
            with ui.column().classes('w-full mb-2'):
                feedback_label = ui.label('').classes('text-lg mt-2')  # Separate label for each feedback below the select
                check_answer_function = create_check_answer_function(user_id, story_id, question_item, feedback_label)
                ui.select(
                    options=question_item["options"],  # List of options
                    label='Choose an answer',
                    on_change=lambda e, check_func=check_answer_function: check_func(e.value)  # Call the specific check_answer function
                ).classes('w-full mb-2')  # Add spacing between questions and feedback

                # Position the feedback label immediately below the dropdown menu
                feedback_label.classes('text-lg mt-2')  # Adds spacing between answer and feedback
