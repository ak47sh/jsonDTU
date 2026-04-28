import webview
import json
from collections import Counter

class API:
    def __init__(self):
        self.data = None

    def openFile(self):
        filePath = webview.windows[0].create_file_dialog(
            webview.FileDialog.OPEN,
            file_types=("JSON Files (*.json)",)
        )

        if filePath:
            filePath = filePath[0]

            with open(filePath, 'r') as f:
                self.data = json.load(f)

            return f"Loaded: {filePath}"
        
        return "No file selected"

    def isDynamicObject(self, values, threshold=0.8):
        dict_values = [v for v in values if isinstance(v, dict)]
        if len(dict_values) < len(values):
            return False

        key_counter = Counter()
        for v in dict_values:
            key_counter.update(v.keys())

        total = len(dict_values)

        common_keys = {
            k for k, count in key_counter.items()
            if count / total >= threshold
        }

        if not common_keys:
            return False

        return all(common_keys.issubset(v.keys()) for v in dict_values)

    def findDynamicKeys(self, obj, path=""):
        results = []

        # Handle dict
        if isinstance(obj, dict):
            keys = list(obj.keys())

            if len(keys) >= 4:
                values = list(obj.values())

                if self.isDynamicObject(values):
                    results.append(path or "root")

            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                results.extend(self.findDynamicKeys(value, new_path))

        elif isinstance(obj, list):
            for item in obj:
                new_path = f"{path}[]" if path else "[]"
                results.extend(self.findDynamicKeys(item, new_path))

        return list(set(results))
        
    def jsDynamicKeys(self):
        if self.data is None:
            return {"error": "No data loaded"}

        paths = self.findDynamicKeys(self.data)

        return {
            "dynamic_paths": paths
        }

    def jsStructure(self):
        if self.data is None:
            return {"error": "No data loaded"}

        return self.getStructure(self.data)
    
    def getStructure(self, obj):
        # Handle dict
        if isinstance(obj, dict):
            values = list(obj.values())

            # 👇 if dynamic → collapse to one representative
            if len(obj) >= 4 and self.isDynamicObject(values):
                first_value = next(iter(obj.values()))
                return {"<dynamic>": self.getStructure(first_value)}

            return {k: self.getStructure(v) for k, v in obj.items()}

        # Handle list
        elif isinstance(obj, list):
            if not obj:
                return []
            return [self.getStructure(obj[0])]

        # Handle primitive
        else:
            return type(obj).__name__


api = API()

webview.create_window("jsonDTU", "index.html", js_api=api)
webview.start()