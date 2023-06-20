import curses
import os.path
import shutil
import npyscreen
import download

import search as dex

import sys

global work_to_download


def get_abs_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    elif __file__:
        return os.path.dirname(os.path.abspath(__file__))


def on_exit():
    # Perform any actions or processing before the form exits
    confirmed = npyscreen.notify_yes_no("Do you want to exit?", title="Exit Confirmation")
    if confirmed:
        sys.exit(0)  # Exit the program


class Chapter_Selection(npyscreen.Form):

    OK_BUTTON_TEXT = "Download"

    def create(self):
        # Create the widgets
        self.back_button = self.add(npyscreen.ButtonPress, name="Back", when_pressed_function=self.back)
        self.select_all_button = self.add(npyscreen.ButtonPress, name="Select all",
                                          when_pressed_function=self.select_all)
        self.add_widget(LineDivider, relx=2, rely=4)
        columns, rows = shutil.get_terminal_size()
        self.result_count_label = self.add(npyscreen.FixedText, value="Searching, please wait", rely=5)
        self.add(npyscreen.ButtonPress, name="EXIT", when_pressed_function=on_exit, relx=columns - 13, rely=2)
        self.result_list = self.add(CustomMultiSelect, values=[], select_exit=True, rely=6)
        self.result_list.add_handlers({curses.ascii.ESC: self.on_escape})
        self.first_entry = True

    def back(self):
        self.first_entry = True
        self.parentApp.switchForm(self.parentApp.previous_form)
        self.result_list.value = []  # Clear the selected values

    def unselect_all(self):
        self.result_list.value = []
        self.select_all_button.name = "Select all"
        self.select_all_button.when_pressed_function = self.select_all
        self.display()

    def select_all(self):
        self.result_list.value = list(range(len(self.result_list.values)))  # Select all options
        self.select_all_button.name = "Unselect all"
        self.select_all_button.when_pressed_function = self.unselect_all
        self.display()

    def on_escape(self, _input):
        # Move the focus to another widget
        # self.result_list.hidden = True
        self.set_editing(self.back_button)
        self.result_list.h_exit_down(None)
        self.display()

    def beforeEditing(self):
        if not self.first_entry:
            # Perform actions during subsequent entries of the form
            selected_items = self.result_list.get_selected_objects()
            if selected_items:
                confirmed = npyscreen.notify_yes_no(f"Selected Chapters: {selected_items}\n Download it now?",
                                                    title="Selection Result")
                if confirmed:
                    selected_indices = [self.result_list.values.index(obj) for obj in selected_items]
                    chap_list = [self.search_results[index + 1] for index in selected_indices]
                    progress_bar = self.parentApp.getForm("DOWNLOAD_PROGRESS")

                    download_folder = os.path.join(get_abs_path(), work_to_download)
                    os.makedirs(download_folder, exist_ok=True)

                    download.download_images_from_api(chap_list, progress_bar, download_folder)
            else:
                npyscreen.notify_confirm("No selection made", title="Error")

        else:
            self.first_entry = False

    def update_results(self, search_results):
        self.result_list.values = search_results

        self.result_count_label.value = f"Total Results: {len(search_results)}"
        if not search_results:
            self.result_count_label.value = f"No results found."
        self.result_count_label.editable = False
        self.result_count_label.display()

        # chapters = [f"Chapter {index}" for index, _ in enumerate(search_results[1:], start=1)]
        chapters = [f"{chapter[1]}" for chapter in search_results[1:]]
        self.result_list.values = chapters
        self.search_results = search_results
        self.result_list.display()


class SearchPage(npyscreen.Form):

    def create(self):
        # Create the widgets
        self.search_box = self.add(npyscreen.TitleText, name="Search Works:")
        self.add(npyscreen.ButtonPress, name="Search", when_pressed_function=self.search)
        self.add_widget(LineDivider, relx=2, rely=4)
        columns, rows = shutil.get_terminal_size()
        self.add(npyscreen.ButtonPress, name="EXIT", when_pressed_function=on_exit, relx=columns - 13, rely=3)
        self.result_list = self.add(CustomMultiLine, values=[], rely=6, hidden=True)
        self.result_list.add_handlers({curses.ascii.ESC: self.on_escape})

    def search(self):
        self.result_count_label = self.add(npyscreen.FixedText, value="Searching, please wait", rely=5)
        self.result_count_label.display()

        search_query = self.search_box.value
        self.results = dex.search_work(search_query)
        display_results = [f"{item['title']} | {item['genre']}" for item in self.results[1:]]

        self.result_count_label.value = f"Total Results: {len(display_results)}"
        self.result_count_label.editable = False
        if not display_results:
            self.result_count_label.value = f"No results found."
        self.result_count_label.display()

        self.result_list.values = display_results
        self.result_list.hidden = False
        self.result_list.display()

    def search_entry(self, selected_index, selected_value):
        # Action to perform when an item is selected
        self.parentApp.getForm("SEARCH_PROMPT").display()

        work_to_search = self.results[selected_index + 1]
        global work_to_download
        work_to_download = selected_value
        hash_to_search = work_to_search["id"]
        results = dex.search_chapters(hash_to_search)

        self.parentApp.getForm("CHAPTERS").update_results(results)
        self.parentApp.previous_form = "MAIN"
        self.parentApp.switchForm("CHAPTERS")

        # Switch to the next page or perform other actions

    # def afterEditing(self):
    #     # Called when the form editing is finished
    #     self.on_exit()

    def on_escape(self, _input):
        # Move the focus to another widget
        # self.result_list.hidden = True
        self.set_editing(self.search_box)
        self.result_list.h_exit_down(None)
        self.display()


class LineDivider(npyscreen.FixedText):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = "-" * self.width
        self.editable = False


class Searching_Popup(npyscreen.Popup):
    def create(self):
        self.add(npyscreen.FixedText, value="Searching available chapters")


class ProgressBarPopup(npyscreen.Popup):
    def create(self):
        self.add(npyscreen.TitleFixedText, name='Chapter', rely=2, editable=False)
        self.chap_progress = self.add(npyscreen.SliderPercent, rely=4, editable=False)
        self.add(npyscreen.TitleText, name='Image', rely=5, editable=False)
        self.img_progress = self.add(npyscreen.SliderPercent, rely=7, editable=False)

    def update_chap_progress(self, chap_progress):
        self.chap_progress.value = chap_progress

    def update_img_progress(self, img_progress):
        self.img_progress.value = img_progress


class CustomMultiLine(npyscreen.MultiLine):
    def handle_input(self, _input):
        if _input == 10:  # Check for Enter key event (ASCII code 10)
            selected_index = self.cursor_line
            selected_value = self.values[selected_index]
            self.parent.search_entry(selected_index, selected_value)  # Switch to the next page with selected value
        else:
            super().handle_input(_input)


class CustomMultiSelect(npyscreen.MultiSelect):
    def when_value_edited(self):
        super().when_cursor_moved()
        selected_options = self.get_selected_objects()

        if not selected_options:
            self.parent.select_all_button.name = "Select all"
            self.parent.select_all_button.when_pressed_function = self.parent.select_all
            self.parent.select_all_button.display()
        else:
            self.parent.select_all_button.name = "Unselect all"
            self.parent.select_all_button.when_pressed_function = self.parent.unselect_all
            self.parent.select_all_button.display()
