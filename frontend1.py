from nicegui import ui
from threading import Thread
from functools import partial
import requests
from backend1 import BackendApp

class FrontendApp:
    def __init__(self, backend, user_id="user_1"):
        self.backend = backend
        self.content_label = None
        self.options = None
        self.user_id = user_id
        self.current_story_id = None  # Track the currently selected story

    def create_ui(self):
        with ui.row().classes('w-full'):
            with ui.column().classes('w-1/4 p-4'):
                ui.label('Type of Content').classes('text-2xl')
                ui.separator()
                ui.link('Short Stories', '/short-stories')
                ui.link('Articles', '/articles')
                ui.link('News', '/news')

            with ui.column().classes('w-3/4 p-4'):
                self.content_label = ui.label('Select a category from the sidebar to begin reading.').classes('text-lg')

        with ui.row().classes('w-full mt-4'):
            with ui.column().classes('w-1/4 p-4'):
                ui.label('List of Stories').classes('text-2xl')
                ui.separator()

                ui.label('Beginner').classes('text-xl mt-4')
                for story_id, story in self.backend.stories["beginner"].items():
                    ui.button(story["display_title"], on_click=partial(self.show_story, story_id)).classes('w-full')

                ui.label('Intermediate').classes('text-xl mt-4')
                for story_id, story in self.backend.stories["intermediate"].items():
                    ui.button(story["display_title"], on_click=partial(self.show_story, story_id)).classes('w-full')

            with ui.column().classes('w-3/4 p-4'):
                self.content_label = ui.label('Select a story to read.').classes('text-lg')
                self.options = ui.column().classes('mt-4')

    def show_story(self, story_id):
        self.current_story_id = story_id
        story = self.backend.stories["beginner"].get(story_id) or self.backend.stories["intermediate"].get(story_id)
        if story:
            self.content_label.set_text(f"Story: {story['display_title']}\n\n" + "\n".join(story["content"]))
            self.show_exercise(story["questions"])
        else:
            print(f"Story with ID '{story_id}' not found.")

    def show_exercise(self, questions):
        self.options.clear()
        completed = [False]  # Mutable list to track if the exercise is completed

        for question in questions:
            with self.options:
                ui.label(question["question"]).classes('text-xl mb-2')
                with ui.column().classes('w-full mb-2'):
                    feedback_label = ui.label('').classes('text-lg mt-2')
                    ui.select(
                        options=question["options"],
                        label='Choose an answer',
                        on_change=lambda e, q=question, fl=feedback_label: self.check_answer(e.value, q, fl, completed)
                    ).classes('w-full mb-2')

        ui.button("Submit Exercise", on_click=lambda: self.mark_exercise_done(completed)).classes('mt-4')

    def check_answer(self, user_answer, question, feedback_label, completed):
        correct_answer = question["answer"]
        is_correct = user_answer.lower() == correct_answer.lower()
        feedback_label.set_text("Correct!" if is_correct else f"Incorrect! Correct: {correct_answer}")
        feedback_label.classes('text-lg text-green-500' if is_correct else 'text-lg text-red-500')
        if is_correct:
            completed[0] = True

    def mark_exercise_done(self, completed):
        if not self.current_story_id:
            ui.notify("No story selected!", type="negative")
            return

        status = "yes" if completed[0] else "no"
        response = requests.post("http://127.0.0.1:5000/update_progress", json={
            "user_id": self.user_id,
            "story_id": self.current_story_id,
            "status": status
        })
        if response.status_code == 200:
            ui.notify(f"Exercise marked as {'done' if status == 'yes' else 'not done'}.")
        else:
            ui.notify("Failed to update progress.", type="negative")

    def run(self):
        ui.run()

def run_backend_in_thread(backend):
    thread = Thread(target=backend.run, daemon=True)
    thread.start()

if __name__ in {"__main__", "__mp_main__"}:
    backend_app = BackendApp()
    frontend_app = FrontendApp(backend_app)
    run_backend_in_thread(backend_app)
    frontend_app.create_ui()
    frontend_app.run()
