import webview
import json

class API:
    def __init__(self):
        self.data = None

    def openFile(self):
        filePath = webview.windows[0].create_file_dialog(
            webview.FileDialog.OPEN,
            file_types=("JSON Files (*.json)",))

        if filePath:
            filePath = filePath[0]

            with open(filePath, 'r') as f:
                self.data = json.load(f)

            return f"Loaded: {filePath}"
        
        return "No file selected"


api = API()

webview.create_window("jsonDTU", "index.html", js_api=api)
webview.start()