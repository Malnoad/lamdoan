from flask import Flask, jsonify, request
import os

app = Flask(__name__)

# Simulated database for user progress
class UserProgress:
    def __init__(self):
        self.data = {}

    def update_progress(self, user_id, story_id, status):
        if user_id not in self.data:
            self.data[user_id] = {}
        self.data[user_id][story_id] = status

    def get_progress(self, user_id):
        return self.data.get(user_id, {})

user_progress = UserProgress()

# Class for loading stories
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
                        if current_title and current_content:
                            stories[current_title] = {
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

    @staticmethod
    def load_stories_from_multiple_files(filenames):
        all_stories = {}
        for filename in filenames:
            file_stories = StoryLoader.load_stories_from_file(filename)
            all_stories.update(file_stories)
        return all_stories

# Load stories
current_dir = os.path.dirname(os.path.abspath(__file__))
file_list = [os.path.join(current_dir, f'alo{i}.txt') for i in range(6)]
stories = StoryLoader.load_stories_from_multiple_files(file_list)

# API Endpoints
@app.route('/api/stories', methods=['GET'])
def get_stories():
    return jsonify({"stories": list(stories.keys())})

@app.route('/api/stories/<string:title>', methods=['GET'])
def get_story(title):
    story = stories.get(title)
    if story:
        return jsonify(story)
    return jsonify({"error": "Story not found"}), 404

@app.route('/api/progress', methods=['POST'])
def update_progress():
    data = request.json
    user_id = data.get("user_id")
    story_id = data.get("story_id")
    progress = data.get("progress")
    if user_id and story_id:
        user_progress.update_progress(user_id, story_id, progress)
        return jsonify({"message": "Progress updated"})
    return jsonify({"error": "Invalid data"}), 400

if __name__ == '__main__':
    app.run(debug=True)
