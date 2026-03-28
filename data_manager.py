import json
import csv
import os

class DataManager:
    DATA_FILE = "store_data.json"

    @staticmethod
    def load_data():
        if not os.path.exists(DataManager.DATA_FILE):
            return {"products": [], "invoices": []}
        try:
            with open(DataManager.DATA_FILE, "r") as f:
                return json.load(f)
        except:
            return {"products": [], "invoices": []}

    @staticmethod
    def save_data(data):
        with open(DataManager.DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def export_to_csv(data, filename, fields):
        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(data)