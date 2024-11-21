import os

class StoryManager:
    def __init__(self):
        self.user_progress = {}
        self.stories = {}
        self.load_stories()

    def load_stories_from_file(self, filename):
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

    def load_stories_from_multiple_files(self, filenames):
        all_stories = {}
        for filename in filenames:
            file_stories = self.load_stories_from_file(filename)
            if file_stories:  # Only add if there are valid stories
                all_stories.update(file_stories)
            else:
                print(f"No valid stories found in {filename}.")
        return all_stories

    def load_stories(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))  # Get the current directory
        file_list = [
            os.path.join(current_dir, 'alo.txt'),
            os.path.join(current_dir, 'alo1.txt'),
            os.path.join(current_dir, 'alo2.txt'),
            os.path.join(current_dir, 'alo3.txt'),
            os.path.join(current_dir, 'alo4.txt'),
            os.path.join(current_dir, 'alo5.txt'),
        ]
        self.stories = self.load_stories_from_multiple_files(file_list)

    def update_user_progress(self, user_id, story_id, status):
        if user_id not in self.user_progress:
            self.user_progress[user_id] = {}

        self.user_progress[user_id][story_id] = status
        print(f"Updated progress for user {user_id} on story {story_id}: {status}")
