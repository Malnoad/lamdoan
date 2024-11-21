from nicegui import ui
from functools import partial

class ReadingPlatformUI:
    def __init__(self, story_manager, progress_manager):
        self.story_manager = story_manager
        self.progress_manager = progress_manager

    def main_page(self):
        @ui.page('/')
        def render():
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

    def short_stories_page(self):
        @ui.page('/short-stories')
        def render():
            with ui.column().classes('w-full min-h-screen items-center p-4') \
                    .style('background: linear-gradient(135deg, #f0f4ff, #e5e7ff)'):
                with ui.column().classes('max-w-4xl mx-auto p-6 bg-gray-50 rounded-lg shadow-lg'):
                    ui.label('List of Stories').classes('text-3xl font-bold text-gray-800 mb-4 text-center')
                    ui.separator().classes('my-4')
                    with ui.grid().classes('grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'):
                        for story_title in self.story_manager.stories.keys():
                            with ui.card().classes('bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-200'):
                                ui.link(story_title, f'/story/{story_title}').classes(
                                    'block text-xl font-semibold text-indigo-600 hover:text-indigo-800 py-4 px-6 no-underline'
                                )
                                description = self.story_manager.stories[story_title].get('content', ['No description available.'])[0]
                                ui.label(description[:100] + '...').classes('text-gray-600 px-6 pb-4')

    def story_detail_page(self):
        @ui.page('/story/{story_title}')
        def render(story_title):
            story = self.story_manager.stories.get(story_title, None)
            if story:
                with ui.column().classes('w-full min-h-screen items-center p-4') \
                        .style('background: linear-gradient(135deg, #f0f4ff, #e5e7ff)'):
                    with ui.column().classes('max-w-4xl mx-auto p-6 bg-gray-50 rounded-lg shadow-lg'):
                        ui.label(f"Story: {story_title}").classes('text-2xl font-bold mb-4')
                        ui.label("\n".join(story["content"])).classes('text-lg mb-4')
                        self.show_exercise(story["questions"], user_id=123, story_id=story_title)  # Example with user_id
            else:
                with ui.column().classes('w-full min-h-screen items-center p-4') \
                        .style('background: linear-gradient(135deg, #f0f4ff, #e5e7ff)'):
                    ui.label(f"Story '{story_title}' not found.").classes('text-2xl text-red-600')

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
                self.progress_manager.update_progress(user_id, story_id, status)

            ui.label("Progress submitted!").style('color: green; font-size: 1.2rem;')

        ui.button('Submit Progress', on_click=submit_progress).classes('w-full bg-indigo-600 hover:bg-indigo-800 text-white py-2 rounded-lg')


# Initialize the UI
ui_app = ReadingPlatformUI(story_manager, progress_manager)
ui_app.main_page()
ui_app.short_stories_page()
ui_app.story_detail_page()

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title='Reading Platform')
