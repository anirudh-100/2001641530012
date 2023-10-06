from flask import Flask, request, jsonify
import requests
from concurrent.futures import ThreadPoolExecutor, TimeoutError

app = Flask(__name__)

def fetch_numbers_from_url(url):
    try:
        response = requests.get(url, timeout=0.5)  # Set a timeout of 500 milliseconds
        response.raise_for_status()
        data = response.json()
        return data.get("numbers", [])
    except (requests.exceptions.RequestException, ValueError, KeyError):
        return []

@app.route('/numbers', methods=['GET'])
def fetch_and_merge_numbers():
    urls = request.args.getlist('url')

    if not urls:
        return jsonify({'error': 'No URLs provided'}), 400

    with ThreadPoolExecutor(max_workers=len(urls)) as executor:
        futures = {executor.submit(fetch_numbers_from_url, url): url for url in urls}
        merged_numbers = set()

        for future in futures:
            url = futures[future]
            try:
                numbers = future.result()
                merged_numbers.update(numbers)
            except TimeoutError:
                pass  # Ignore URLs that exceeded the timeout

    sorted_numbers = sorted(merged_numbers)
    return jsonify({'numbers': sorted_numbers})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8008)
