# 🚀 Complete Setup Guide

## Prerequisites

- **Python 3.8+**
- **pip** (Python package manager)
- **Git** (for cloning)
- ~500MB free disk space

---

## Step-by-Step Installation

### 1. Clone Repository

```bash
git clone https://github.com/Lizard51/books-rec-system.git
cd books-rec-system
```

### 2. Create Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Prepare Dataset

Create `data/books.csv`:

```csv
title,authors,description,genres,rating
The Hobbit,J.R.R. Tolkien,"In a hole in the ground there lived a hobbit...",Fantasy,4.7
1984,George Orwell,"It is the year 1984...",Dystopian,4.6
```

Or download from [Kaggle](https://www.kaggle.com/datasets/jealousleopard/goodreadscsv)

### 5. Configure Google Books API (Optional)

```bash
cp .env.example .env
```

Edit `.env`:
```
GOOGLE_BOOKS_API_KEY=your_api_key_here
```

### 6. Run Application

```bash
python app.py
```

Open **http://localhost:5000** in your browser.

---

## Testing

1. **Local Search**: Type a book name in "Search Local Database"
2. **Select Books**: Add 3+ books to your selection
3. **Generate**: Click "Generate Recommendations"
4. **View Results**: See similar books with similarity scores

---

## Troubleshooting

### Module not found: flask
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### FileNotFoundError: data/books.csv
```bash
mkdir -p data
# Add your CSV file
```

### Port 5000 already in use
```bash
# Change port in app.py last line:
# app.run(debug=True, host='0.0.0.0', port=5001)
```

### Google Books API: 403 Forbidden
- Check API key in `.env`
- Verify API is enabled in Google Cloud Console
- Regenerate key if needed

---

## Performance Optimization

For large datasets (10,000+ books), edit `recommender.py`:

```python
TfidfVectorizer(
    max_features=1000,      # Reduced from 5000
    min_df=5,               # Increased from 2
    max_df=0.7             # Reduced from 0.8
)
```

---

## Next Steps

1. ✓ Try different book selections
2. ✓ Add more books to dataset
3. ✓ Configure Google Books API
4. ✓ Deploy to production (optional)

---

**Enjoy your book recommendations! 📚✨**
