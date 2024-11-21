from nicegui import ui
import requests

API_BASE_URL = 'http://127.0.0.1:5000/api'

# Helper class for API communication
class APIClient:
    @staticmethod
    def fetch_stories():
        response = requests.get(f"{API_BASE_URL}/stories")
        return response.json().get("stories", [])

    @staticmethod
    def fetch_story_details(title):
        response = requests.get(f"{API_BASE_URL}/stories/{title}")
        return response.json()

    @staticmethod
    def submit_progress(user_id, story_id, progress):
        data = {"user_id": user_id, "story_id": story_id, "progress": progress}
        requests.post(f"{API_BASE_URL}/progress", json=data)

# Frontend pages
@ui.page('/')
def main_page():
    with ui.column().classes('w-full min-h-screen items-center p-4'):
        ui.label('READING PLATFORM').classes('text-4xl font-bold mb-4')
        stories = APIClient.fetch_stories()
        for story in stories:
            ui.link(story, f"/story/{story}").classes('text-lg text-indigo-600 underline mb-2')

@ui.page('/story/{title}')
def story_page(title):
    story = APIClient.fetch_story_details(title)
    if 'error' in story:
        ui.label(story['error']).classes('text-red-500')
    else:
        ui.label(f"Story: {title}").classes('text-2xl font-bold mb-4')
        for paragraph in story['content']:
            ui.label(paragraph).classes('text-lg mb-2')

        progress = {}
        for question in story['questions']:
            ui.label(question['question']).classes('text-xl mb-2')
            selected_option = ui.select(question['options'], label='Choose an answer')
            progress[question['question']] = selected_option.value

        def submit():
            APIClient.submit_progress(123, title, progress)
            ui.notify('Progress submitted successfully!')

        ui.button('Submit Progress', on_click=submit).classes('bg-blue-500 text-white p-2 rounded')

if __name__ == '__main__':
    ui.run(title="Reading Platform")
