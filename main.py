# import search as dex
import npyscreen
import views


class MyApp(npyscreen.NPSAppManaged):
    def onStart(self):
        # Create the search page form and display it
        self.addForm("MAIN", views.SearchPage, name="MangaDex Downloader")
        # self.addForm("CONFORMATION", views.ConfirmationForm, name="Exit conformation")
        self.addForm("SEARCH_PROMPT", views.Searching_Popup, name="MangaDex Downloader")
        self.addForm("DOWNLOAD_PROGRESS", views.ProgressBarPopup, name="Downloading")
        self.addForm("CHAPTERS", views.Chapter_Selection, name="Chapters")
        self.previous_form = None


app = MyApp()
app.run()


# save_directory = '/Volumes/Ramdisk/MonotoneBlue'  # Replace with your desired save directory
#
# # download_images_from_api(hashVal, save_directory)
# result = dex.search_work("Monotone Blue")
# result = dex.search_chapters(result[1]["id"])
# # download_images_from_api(result[1], save_directory)
# print(result)
