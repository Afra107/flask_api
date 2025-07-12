from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import json
import os

app = Flask(__name__)
CORS(app)  # Enable CORS to allow access from other sites

CSV_FILE = 'g2g_softwares.csv'
JSON_FILE = 'g2g_softwares.json'

# Function to convert CSV to JSON file
def convert_csv_to_json(csv_file, json_file):
    df = pd.read_csv(csv_file)
    df.to_json(json_file, orient='records', indent=2)

# Ensure JSON file is up to date
if not os.path.exists(JSON_FILE) or os.path.getmtime(CSV_FILE) > os.path.getmtime(JSON_FILE):
    convert_csv_to_json(CSV_FILE, JSON_FILE)

# Load JSON file
def load_json_data():
    with open(JSON_FILE, 'r') as f:
        return json.load(f)

# Load data once at startup
data = load_json_data()

# API route: Get all products
@app.route('/api/products', methods=['GET'])
def get_all_products():
    return jsonify(data)

# API route: Get product by Sr No
@app.route('/api/products/<int:sr_no>', methods=['GET'])
def get_product_by_srno(sr_no):
    for item in data:
        if item.get("Sr No") == sr_no:
            return jsonify(item)
    return jsonify({"error": "Product not found"}), 404

# API route: Get products by Category
@app.route('/api/products/category/<string:category>', methods=['GET'])
def get_products_by_category(category):
    filtered = [item for item in data if item.get("Category", "").lower() == category.lower()]
    if filtered:
        return jsonify(filtered)
    return jsonify({"error": "No products found in this category"}), 404

if __name__ == '__main__':
    app.run(debug=True)
