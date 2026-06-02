from flask import Flask, render_template, request, jsonify
import os
import sys
from recommender import ContentBasedRecommender
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Initialize recommender system
try:
    dataset_path = 'data/books.csv'
    if not os.path.exists(dataset_path):
        print(f"⚠ Warning: Dataset not found at {dataset_path}")
        print("Please ensure data/books.csv exists in the project directory")
        recommender = None
    else:
        print("🚀 Initializing recommendation engine...")
        recommender = ContentBasedRecommender(dataset_path)
        print("✓ Recommendation engine ready!\n")
except Exception as e:
    print(f"✗ Error initializing recommender: {e}")
    recommender = None

# Google Books API configuration
GOOGLE_BOOKS_API_KEY = os.getenv('GOOGLE_BOOKS_API_KEY', '')
GOOGLE_BOOKS_API_URL = 'https://www.googleapis.com/books/v1/volumes'


@app.route('/')
def index():
    """Home page - book selection interface."""
    if recommender is None:
        return render_template('index.html', 
                             books=[],
                             dataset_loaded=False,
                             error="Dataset not found. Please check data/books.csv")
    
    # Get some books for initial display
    books = recommender.get_all_books(limit=100)
    stats = recommender.get_dataset_stats()
    
    return render_template('index.html',
                         books=books,
                         dataset_loaded=True,
                         stats=stats)


@app.route('/api/search', methods=['POST'])
def api_search():
    """Search for books (local dataset)."""
    if recommender is None:
        return jsonify({'error': 'Recommender not initialized'}), 500
    
    data = request.get_json()
    query = data.get('query', '').strip()
    
    if len(query) < 2:
        return jsonify({'results': []})
    
    results = recommender.search_books(query, limit=20)
    return jsonify({'results': results})


@app.route('/api/google-search', methods=['POST'])
def api_google_search():
    """Search for books using Google Books API."""
    if not GOOGLE_BOOKS_API_KEY:
        return jsonify({'error': 'Google Books API key not configured'}), 400
    
    data = request.get_json()
    query = data.get('query', '').strip()
    
    if len(query) < 2:
        return jsonify({'results': []})
    
    try:
        params = {
            'q': query,
            'key': GOOGLE_BOOKS_API_KEY,
            'maxResults': 20,
            'printType': 'books'
        }
        
        response = requests.get(GOOGLE_BOOKS_API_URL, params=params, timeout=10)
        response.raise_for_status()
        
        books_data = response.json().get('items', [])
        results = []
        
        for item in books_data:
            volume_info = item.get('volumeInfo', {})
            
            # Extract image URL with fallback to placeholder
            image_url = 'https://via.placeholder.com/128x192?text=No+Cover'
            if 'imageLinks' in volume_info:
                image_url = volume_info['imageLinks'].get('thumbnail', image_url)
            
            book_dict = {
                'title': volume_info.get('title', 'Unknown'),
                'authors': ', '.join(volume_info.get('authors', ['Unknown'])),
                'description': volume_info.get('description', 'No description available')[:300],
                'image_url': image_url,
                'source': 'google'
            }
            results.append(book_dict)
        
        return jsonify({'results': results})
    
    except requests.RequestException as e:
        print(f"✗ Google Books API error: {e}")
        return jsonify({'error': 'Failed to fetch from Google Books API'}), 500


@app.route('/api/recommend', methods=['POST'])
def api_recommend():
    """Generate recommendations based on selected books."""
    if recommender is None:
        return jsonify({'error': 'Recommender not initialized'}), 500
    
    data = request.get_json()
    selected_books = data.get('selected_books', [])
    
    if len(selected_books) < 3:
        return jsonify({
            'error': 'Please select at least 3 books',
            'recommendations': [],
            'explanation': ''
        }), 400
    
    recommendations, explanation = recommender.get_recommendations(selected_books, top_n=10)
    
    return jsonify({
        'recommendations': recommendations,
        'explanation': explanation,
        'selected_count': len(selected_books)
    })


@app.route('/recommendations')
def recommendations():
    """Recommendations result page."""
    return render_template('recommendations.html')


@app.route('/api/stats', methods=['GET'])
def api_stats():
    """Get dataset statistics."""
    if recommender is None:
        return jsonify({'error': 'Recommender not initialized'}), 500
    
    stats = recommender.get_dataset_stats()
    return jsonify(stats)


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('index.html', 
                         books=[],
                         dataset_loaded=False,
                         error='Page not found'), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    return render_template('index.html',
                         books=[],
                         dataset_loaded=False,
                         error='Server error'), 500


if __name__ == '__main__':
    print("=" * 60)
    print("📚 BOOK RECOMMENDATION SYSTEM")
    print("=" * 60)
    print("\n🔍 Configuration:")
    print(f"  - Dataset path: data/books.csv")
    print(f"  - Google Books API: {'✓ Configured' if GOOGLE_BOOKS_API_KEY else '✗ Not configured'}")
    print(f"  - Flask debug: {app.debug}")
    print("\n🌐 Starting Flask server...")
    print("📍 Navigate to: http://localhost:5000")
    print("\n" + "=" * 60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
