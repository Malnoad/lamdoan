from flask import Flask, request, jsonify
import os
from threading import Lock

class StoryLoader:
    @staticmethod
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
                        continue

                    if line.startswith("Title:"):
                        # Save the previous story
                        if current_title and current_content:
                            unique_id = f"{filename}_{current_title}"
                            stories[unique_id] = {
                                "display_title": current_title,
                                "content": current_content,
                                "questions": current_questions
                            }

                        current_title = line[6:].strip()
                        current_content = []
                        current_questions = []
                    elif line.startswith("Question:"):
                        question_text = line[9:].strip()
                        try:
                            options = next(file).strip().split(';')
                            answer = next(file).strip()
                            current_questions.append({
                                "question": question_text,
                                "options": options,
                                "answer": answer
                            })
                        except StopIteration:
                            print(f"Incomplete question data for '{question_text}'.")
                            break
                    else:
                        current_content.append(line)

                # Save the last story
                if current_title and current_content:
                    unique_id = f"{filename}_{current_title}"
                    stories[unique_id] = {
                        "display_title": current_title,
                        "content": current_content,
                        "questions": current_questions
                    }
        except FileNotFoundError:
            print(f"File {filename} not found.")
        except Exception as e:
            print(f"Error loading file {filename}: {e}")
        return stories

class BackendApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.stories = {"beginner": {}, "intermediate": {}}
        self.user_progress = {}  # Tracks user progress {user_id: {story_id: "yes"/"no"}}
        self.lock = Lock()  # For thread-safe updates
        self.load_stories()
        self.add_routes()

    def load_stories(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        beginner_files = ['alo.txt', 'alo1.txt', 'alo2.txt']
        intermediate_files = ['alo3.txt', 'alo4.txt', 'alo5.txt']

        for filename in beginner_files + intermediate_files:
            full_path = os.path.join(current_dir, filename)
            file_stories = StoryLoader.load_stories_from_file(full_path)
            if filename in beginner_files:
                self.stories["beginner"].update(file_stories)
            elif filename in intermediate_files:
                self.stories["intermediate"].update(file_stories)

    def update_user_progress(self, user_id, story_id, status):
        with self.lock:
            if user_id not in self.user_progress:
                self.user_progress[user_id] = {}
            self.user_progress[user_id][story_id] = status

    def get_user_progress(self, user_id):
        with self.lock:
            return self.user_progress.get(user_id, {})

    def add_routes(self):
        @self.app.route('/get_progress/<user_id>', methods=['GET'])
        def get_progress(user_id):
            return jsonify(self.get_user_progress(user_id))

        @self.app.route('/update_progress', methods=['POST'])
        def update_progress():
            data = request.json
            user_id = data.get('user_id')
            story_id = data.get('story_id')
            status = data.get('status')
            if not all([user_id, story_id, status]):
                return jsonify({"error": "Missing parameters"}), 400
            self.update_user_progress(user_id, story_id, status)
            return jsonify({"message": "Progress updated"}), 200

    def run(self, port=5000):
        self.app.run(port=port)
