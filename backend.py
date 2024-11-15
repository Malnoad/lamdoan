# Main UI layout
with ui.row().classes('w-full'):
    with ui.column().classes('w-1/4 p-4'):
        ui.label('Type of Content').classes('text-2xl')
        ui.separator()
        ui.link('Short Stories', '/short-stories')
        ui.link('Articles', '/articles')
        ui.link('News', '/news')

    with ui.column().classes('w-3/4 p-4'):
        content_label = ui.label('Select a category from the sidebar to begin reading.').classes('text-lg')

with ui.row().classes('w-full mt-4'):
    with ui.column().classes('w-1/4 p-4'):
        ui.label('List of Stories').classes('text-2xl')
        ui.separator()

        # Beginner Section
        ui.label('Beginner').classes('text-xl mt-4')
        for story_id, story in beginner_stories.items():
            ui.button(story["display_title"], on_click=partial(show_story, 1, story_id)).classes('w-full')

        # Intermediate Section
        ui.label('Intermediate').classes('text-xl mt-4')
        for story_id, story in intermediate_stories.items():
            ui.button(story["display_title"], on_click=partial(show_story, 1, story_id)).classes('w-full')

    with ui.column().classes('w-3/4 p-4'):
        content_label = ui.label('Select a story to read.').classes('text-lg')
        options = ui.column().classes('mt-4')  # Container for options (radio buttons)

# Function to run Flask in a separate thread
def run_flask():
    app.run(port=5000)

# Run Flask in a separate thread to avoid blocking NiceGUI
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

# Run the NiceGUI UI
ui.run()
