from flask import Flask
import os

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

class BackendApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.stories = {"beginner": {}, "intermediate": {}}
        self.load_stories()

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

    def run(self, port=5000):
        self.app.run(port=port)
