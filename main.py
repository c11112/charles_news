from flask import Flask, render_template, jsonify, request
import requests
import uuid
import pandas

app = Flask(__name__, static_url_path='/static')

DEFAULT_VALUES = {
    'entry_id': '',
    'category': 'No entries',
    'title': '',
    'metadata': '',
    'link': '',
    'summary': '',
    'source': '',
}

def fetch_data(url, metadata_filter=None):
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        entries = []

        if data is not None and isinstance(data, dict):
            for top_folder_id, top_folder_data in data.items():
                if not top_folder_data:
                    continue

                for second_layer_id, second_layer_data in top_folder_data.items():
                    if not second_layer_data or 'category' not in second_layer_data:
                        continue

                    entry_id = top_folder_id

                    entry = {
                        'entry_id': entry_id,
                        'category': second_layer_data.get('category', DEFAULT_VALUES['category']),
                        'title': second_layer_data.get('title', DEFAULT_VALUES['title']),
                        'metadata': second_layer_data.get('metadata', DEFAULT_VALUES['metadata']),
                        'link': second_layer_data.get('link', DEFAULT_VALUES['link']),
                        'summary': second_layer_data.get('summary', DEFAULT_VALUES['summary']),
                        'source': second_layer_data.get('source', DEFAULT_VALUES['source']),
                    }

                    if metadata_filter is None or entry['metadata'] == metadata_filter:
                        entries.append(entry)

            return entries or [DEFAULT_VALUES]
        else:
            return [DEFAULT_VALUES]
    else:
        return [DEFAULT_VALUES]

@app.route('/')
def index():
    get_all_child_ids_url = "https://digest-a3589-default-rtdb.firebaseio.com/.json"
    entries = fetch_data(get_all_child_ids_url, metadata_filter="n/a")
    return render_template('digest.html', entries=entries)

@app.route('/shelf')
def saved():
    get_saved_data_url = "https://digest-a3589-default-rtdb.firebaseio.com/.json"
    entries = fetch_data(get_saved_data_url, metadata_filter="Saved")
    return render_template('shelf.html', entries=entries)

@app.route('/delete_data/<entry_id>', methods=['POST', 'DELETE'])
def delete_data(entry_id):
    delete_url = f"https://digest-a3589-default-rtdb.firebaseio.com/{entry_id}.json"
    response = requests.delete(delete_url, params={'id': entry_id})
    return jsonify({'message': 'Data deleted successfully'})

@app.route('/delete_all_entries', methods=['POST'])
def delete_all_entries():
    get_all_data_url = "https://digest-a3589-default-rtdb.firebaseio.com/.json"
    entries = fetch_data(get_all_data_url)

    for entry in entries:
        if entry['metadata'] != 'Saved':
            delete_url = f"https://digest-a3589-default-rtdb.firebaseio.com/{entry['entry_id']}.json"
            response = requests.delete(delete_url)
            if response.status_code not in [200, 204]:
                print(f"Failed to delete {entry['entry_id']}: {response.status_code}")

    return jsonify({'message': 'Non-saved entries deleted successfully'})

@app.route('/update_data/<entry_id>', methods=['POST', 'PUT'])
def update_data(entry_id):
    update_url = f"https://digest-a3589-default-rtdb.firebaseio.com/{entry_id}.json"

    existing_data_url = f"https://digest-a3589-default-rtdb.firebaseio.com/{entry_id}.json"
    existing_data = requests.get(existing_data_url).json()

    if existing_data:
        entry_key, entry_info = existing_data.popitem()
        category = entry_info.get('category', 'n/a')
        link = entry_info.get('link', 'n/a')
        metadata = "Saved"
        summary = entry_info.get('summary', 'n/a')
        title = entry_info.get('title', 'n/a')

        data_to_update = {
            entry_id: {
                'category': category,
                'link': link,
                'summary': summary,
                'title': title,
                'metadata': metadata
            }
        }

        response = requests.put(update_url, json=data_to_update)
        return jsonify({'message': 'Data updated successfully'})

@app.route('/add_entry', methods=['POST'])
def add_entry():
    entry = request.form.get('entry')

    if not entry:
        return jsonify({'error': 'No entry provided'}), 400

    entry_id = str(uuid.uuid4())

    post_data = {
        entry_id: {
            'category': 'n/a',
            'title': entry,
            'metadata': 'Saved',
            'link': entry,
            'summary': 'n/a',
            'source': 'n/a'
        }
    }

    base_url = 'https://digest-a3589-default-rtdb.firebaseio.com/'

    firebase_id = str(uuid.uuid4())
    post_url = f'{base_url}{firebase_id}.json'
    response = requests.put(post_url, json=post_data)

    if response.status_code in [200, 201]:
        return jsonify({'message': 'Entry added successfully', 'entry': post_data[entry_id]}), 201
    else:
        return jsonify({'error': 'Failed to add entry'}), response.status_code

@app.route('/reload_entries', methods=['GET'])
def reload_entries():
    get_all_child_ids_url = "https://digest-a3589-default-rtdb.firebaseio.com/.json"
    entries = fetch_data(get_all_child_ids_url, metadata_filter="n/a")
    return jsonify(entries=entries)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
