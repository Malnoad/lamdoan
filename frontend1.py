from nicegui import ui
from functools import partial
from backend1 import stories, update_user_progress

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

        ui.select(
            options=question_item["options"],
            label='Choose an answer',
            on_change=lambda e, f=partial(check_answer, feedback_label=feedback_label, question_item=question_item): f(e.value)
        ).classes('w-full mb-2 bg-gray-100 border border-gray-300 rounded-md p-2')

    def submit_progress():
        for question, status in answers.items():
            update_user_progress(user_id, story_id, status)
        ui.label("Progress submitted!").style('color: green; font-size: 1.2rem;')

    ui.button('Submit Progress', on_click=submit_progress).classes('w-full bg-indigo-600 hover:bg-indigo-800 text-white py-2 rounded-lg')

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title='Reading Platform')
