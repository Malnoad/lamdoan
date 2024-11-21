from flask import Flask
from nicegui import ui
import os
from read_backend import StoryLoader, UserProgress
from functools import partial


class ReadingUI:
    def __init__(self):
        # Initialize Flask app
        self.app = Flask(__name__)

        # Initialize backend components
        current_dir = os.path.dirname(os.path.abspath(__file__))  # Get the current directory
        file_list = [
            os.path.join(current_dir, 'alo.txt'),
            os.path.join(current_dir, 'alo1.txt'),
            os.path.join(current_dir, 'alo2.txt'),
            os.path.join(current_dir, 'alo3.txt'),
            os.path.join(current_dir, 'alo4.txt'),
            os.path.join(current_dir, 'alo5.txt'),
        ]
        self.story_loader = StoryLoader(file_list)
        self.user_progress = UserProgress()
        self.stories = self.story_loader.stories

        # Debug: Check if stories are loaded
        if not self.stories:
            print("No stories found! Please check your file paths.")
        else:
            print("Loaded stories:", list(self.stories.keys()))

        # Set up routes
        self._set_routes()

    def _set_routes(self):
        # Main Reading Page
        @ui.page('/reading')
        def reading_main_page():
            with ui.column().classes('w-full min-h-screen items-center p-4') \
                    .style('background: linear-gradient(135deg, #f0f4ff, #e5e7ff)'):
                with ui.card().classes('w-full max-w-3xl p-6 mt-8 items-center'):
                    with ui.row().classes('w-full items-center gap-4 mb-6'):
                        ui.icon('book', size='32px').classes('text-indigo-600')
                        ui.label('Reading Section').classes('text-3xl font-bold text-indigo-600 text-center')
                    with ui.row().style('justify-content: center; margin: 10px 0; gap: 10px; flex-wrap: wrap;'):
                        for category in ['Short Stories', 'Articles', 'News']:
                            ui.link(category, f'/reading/{category.lower().replace(" ", "-")}').classes(
                                'w-full bg-indigo-600 hover:bg-indigo-800 text-white font-semibold py-2 rounded-lg shadow-md no-underline text-center'
                            )

        # Short Stories Page
        @ui.page('/reading/short-stories')
        def short_stories_page():
            with ui.column().classes('w-full min-h-screen items-center p-4') \
                    .style('background: linear-gradient(135deg, #f0f4ff, #e5e7ff)'):
                with ui.card().classes('max-w-4xl mx-auto p-6 bg-gray-50 rounded-lg shadow-lg'):
                    ui.label('Short Stories').classes('text-3xl font-bold text-gray-800 mb-4 text-center')
                    ui.separator().classes('my-4')
                    with ui.grid().classes('grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'):
                        for story_title in self.stories.keys():
                            with ui.card().classes('bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-200'):
                                ui.link(story_title, f'/reading/story/{story_title}').classes(
                                    'block text-xl font-semibold text-indigo-600 hover:text-indigo-800 py-4 px-6 no-underline'
                                )
                                description = self.stories[story_title].get('content', ['No description available.'])[0]
                                ui.label(description[:100] + '...').classes('text-gray-600 px-6 pb-4')

        # Story Detail Page
        @ui.page('/reading/story/{story_title}')
        def show_story(story_title):
            story = self.stories.get(story_title, None)
            if story:
                with ui.column().classes('w-full min-h-screen items-center p-4') \
                        .style('background: linear-gradient(135deg, #f0f4ff, #e5e7ff)'):
                    with ui.column().classes('max-w-4xl mx-auto p-6 bg-gray-50 rounded-lg shadow-lg'):
                        ui.label(f"Story: {story_title}").classes('text-2xl font-bold mb-4')
                        ui.label("\n".join(story["content"])).classes('text-lg mb-4')
                        self.show_exercise(story["questions"], user_id=123, story_id=story_title)

                        ui.link('Back to Homepage', 'http://192.168.1.38:8080').classes(
                        'w-auto bg-indigo-600 hover:bg-indigo-800 text-white py-1 px-4 rounded-lg mt-4 text-sm')


            else:
                with ui.column().classes('w-full min-h-screen items-center p-4') \
                        .style('background: linear-gradient(135deg, #f0f4ff, #e5e7ff)'):
                    ui.label(f"Story '{story_title}' not found.").classes('text-2xl text-red-600')
                    ui.link('Back to Home', '/reading').classes(
                        'w-full bg-gray-700 hover:bg-gray-900 text-white py-2 rounded-lg mt-4')

    def show_exercise(self, story_questions, user_id, story_id):
        answers = {}  # Dictionary to store user's answers

        for question_item in story_questions:
            ui.label(question_item["question"]).classes('text-xl font-semibold mb-2')
            feedback_label = ui.label("").style('font-size: 1rem; margin-top: 0.5rem; display: block;')

            def check_answer(user_answer, feedback_label, question_item):
                correct_answer = question_item["answer"]
                feedback_label.style('font-size: 1rem; margin-top: 0.5rem; display: block;')

                if user_answer.lower() == correct_answer.lower():
                    feedback_label.set_text("✓ Correct!")
                    feedback_label.style('color: green; font-size: 1.2rem;')
                    answers[question_item["question"]] = 'yes'
                else:
                    feedback_label.set_text(f"✗ Incorrect! The correct answer was: {correct_answer}")
                    feedback_label.style('color: red; font-size: 1.2rem;')
                    answers[question_item["question"]] = 'no'

            bound_check_answer = partial(check_answer, feedback_label=feedback_label, question_item=question_item)

            ui.select(
                options=question_item["options"],
                label='Choose an answer',
                on_change=lambda e, f=bound_check_answer: f(e.value)
            ).classes('w-full mb-2 bg-gray-100 border border-gray-300 rounded-md p-2')

        def submit_progress():
            for question, status in answers.items():
                self.user_progress.update_progress(user_id, story_id, status)

            ui.label("Progress submitted!").style('color: green; font-size: 1.2rem;')

            ui.button('Submit Progress', on_click=submit_progress).classes(
            'w-full bg-indigo-600 hover:bg-indigo-800 text-white py-2 rounded-lg')

    def run(self):
        ui.run(title='Reading Platform', favicon='🎓')


if __name__ == '__main__':
    app = ReadingUI()
    app.run()
