from flask import Flask
from nicegui import ui
import os
from functools import partial

app = Flask(__name__)

# Simulate a database to store user progress
user_progress = {}

# Story loading functions
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

def load_stories_from_multiple_files(filenames):
    all_stories = {}
    for filename in filenames:
        file_stories = load_stories_from_file(filename)
        if file_stories:  # Only add if there are valid stories
            all_stories.update(file_stories)
        else:
            print(f"No valid stories found in {filename}.")
    return all_stories

# Load stories
current_dir = os.path.dirname(os.path.abspath(__file__))  # Get the current directory
file_list = [
    os.path.join(current_dir, 'alo.txt'),
    os.path.join(current_dir, 'alo1.txt'),
    os.path.join(current_dir, 'alo2.txt'),
    os.path.join(current_dir, 'alo3.txt'),
    os.path.join(current_dir, 'alo4.txt'),
    os.path.join(current_dir, 'alo5.txt'),
]
stories = load_stories_from_multiple_files(file_list)

# Function to update user progress
def update_user_progress(user_id, story_id, status):
    if user_id not in user_progress:
        user_progress[user_id] = {}

    user_progress[user_id][story_id] = status
    print(f"Updated progress for user {user_id} on story {story_id}: {status}")

# Main page
@ui.page('/')
def main_page():
    with ui.column().classes('w-full min-h-screen items-center p-4') \
            .style('background: linear-gradient(135deg, #f0f4ff, #e5e7ff)'):
        with ui.card().classes('w-full max-w-3xl p-6 mt-8 items-center'):
            with ui.row().classes('w-full items-center gap-4 mb-6'):
                ui.icon('school', size='32px').classes('text-indigo-600')
                ui.label('READING').classes('text-2xl font-bold text-indigo-600')
            with ui.row().style('justify-content: center; margin: 10px 0;gap: 10px; flex-wrap: wrap;'):
                for category in ['Short Stories', 'Articles', 'News']:
                    ui.link(category, f'/{category.lower().replace(" ", "-")}').classes(
                        'w-full bg-indigo hover:bg-indigo-600 text-white font-semibold py-2 rounded-lg shadow-md no-underline text-center'
                    )

# Short stories page
@ui.page('/short-stories')
def short_stories_page():
    with ui.column().classes('w-full min-h-screen items-center p-4') \
            .style('background: linear-gradient(135deg, #f0f4ff, #e5e7ff)'):
        with ui.column().classes('max-w-4xl mx-auto p-6 bg-gray-50 rounded-lg shadow-lg'):
            ui.label('List of Stories').classes('text-3xl font-bold text-gray-800 mb-4 text-center')
            ui.separator().classes('my-4')
            with ui.grid().classes('grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'):
                for story_title in stories.keys():
                    with ui.card().classes('bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-200'):
                        ui.link(story_title, f'/story/{story_title}').classes(
                            'block text-xl font-semibold text-indigo-600 hover:text-indigo-800 py-4 px-6 no-underline'
                        )
                        description = stories[story_title].get('content', ['No description available.'])[0]
                        ui.label(description[:100] + '...').classes('text-gray-600 px-6 pb-4')

# Story detail page
@ui.page('/story/{story_title}')
def show_story(story_title):
    story = stories.get(story_title, None)
    if story:
        with ui.column().classes('w-full min-h-screen items-center p-4') \
                .style('background: linear-gradient(135deg, #f0f4ff, #e5e7ff)'):
            with ui.column().classes('max-w-4xl mx-auto p-6 bg-gray-50 rounded-lg shadow-lg'):
                ui.label(f"Story: {story_title}").classes('text-2xl font-bold mb-4')
                ui.label("\n".join(story["content"])).classes('text-lg mb-4')
                show_exercise(story["questions"], user_id=123, story_id=story_title)  # Example with user_id
    else:
        with ui.column().classes('w-full min-h-screen items-center p-4') \
                .style('background: linear-gradient(135deg, #f0f4ff, #e5e7ff)'):
            ui.label(f"Story '{story_title}' not found.").classes('text-2xl text-red-600')

def show_exercise(story_questions, user_id, story_id):
    answers = {}  # Dictionary to store user's answers

    for question_item in story_questions:
        # Display the question
        ui.label(question_item["question"]).classes('text-xl font-semibold mb-2')

        # Create a unique feedback label for each question
        feedback_label = ui.label("").style('font-size: 1rem; margin-top: 0.5rem; display: block;')  # Ensure visibility

        # Define the function to check the user's answer
        def check_answer(user_answer, feedback_label, question_item):
            correct_answer = question_item["answer"]

            # Reset feedback styles
            feedback_label.style('font-size: 1rem; margin-top: 0.5rem; display: block;')  # Ensure label is visible

            if user_answer.lower() == correct_answer.lower():
                feedback_label.set_text("✓ Correct!")
                feedback_label.style('color: green; font-size: 1.2rem;')  # Success styling
                answers[question_item["question"]] = 'yes'
            else:
                feedback_label.set_text(f"✗ Incorrect! The correct answer was: {correct_answer}")
                feedback_label.style('color: red; font-size: 1.2rem;')  # Error styling
                answers[question_item["question"]] = 'no'

        # Bind the feedback_label and question_item to the function
        bound_check_answer = partial(check_answer, feedback_label=feedback_label, question_item=question_item)

        # Create a dropdown for selecting answers
        ui.select(
            options=question_item["options"],
            label='Choose an answer',
            on_change=lambda e, f=bound_check_answer: f(e.value)  # Use the bound function
        ).classes('w-full mb-2 bg-gray-100 border border-gray-300 rounded-md p-2')

    # Submit button to update progress
    def submit_progress():
        for question, status in answers.items():
            update_user_progress(user_id, story_id, status)  # Update progress for each question

        ui.label("Progress submitted!").style('color: green; font-size: 1.2rem;')  # Show success message

    ui.button('Submit Progress', on_click=submit_progress).classes('w-full bg-indigo-600 hover:bg-indigo-800 text-white py-2 rounded-lg')


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title='Reading Platform')
