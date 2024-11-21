from flask import Flask
import os

class StoryManager:
    def __init__(self, file_list):
        self.stories = self._load_stories_from_multiple_files(file_list)

    def _load_stories_from_file(self, filename):
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
                                "questions": current_questions,
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
                                "answer": answer,
                            })
                        except StopIteration:
                            print(f"Error: Incomplete question data for '{question_text}'.")
                            break
                    else:
                        current_content.append(line)

                if current_title and current_content:
                    stories[current_title] = {
                        "content": current_content,
                        "questions": current_questions,
                    }

        except FileNotFoundError:
            print(f"File {filename} not found.")
        return stories

    def _load_stories_from_multiple_files(self, filenames):
        all_stories = {}
        for filename in filenames:
            all_stories.update(self._load_stories_from_file(filename))
        return all_stories


class ProgressManager:
    def __init__(self):
        self.user_progress = {}

    def update_progress(self, user_id, story_id, status):
        if user_id not in self.user_progress:
            self.user_progress[user_id] = {}
        self.user_progress[user_id][story_id] = status
        print(f"Updated progress for user {user_id} on story {story_id}: {status}")

    def get_progress(self, user_id, story_id):
        return self.user_progress.get(user_id, {}).get(story_id, None)


# Initialize the Flask app and managers
app = Flask(__name__)

# Story and user progress management
file_list = [f"alo{i}.txt" for i in range(6)]
story_manager = StoryManager(file_list)
progress_manager = ProgressManager()
