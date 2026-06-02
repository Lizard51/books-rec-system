import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple
from utils.preprocessing import load_and_clean_dataset, validate_dataset


class ContentBasedRecommender:
    """
    Content-Based Recommendation System using TF-IDF and Cosine Similarity.
    
    Algorithm:
    1. TF-IDF Vectorization: Convert book descriptions+genres to numerical vectors
    2. User Profile: Average of TF-IDF vectors of selected books
    3. Similarity Calculation: Cosine similarity between user profile and all books
    4. Ranking: Top-10 books by similarity score
    """
    
    def __init__(self, dataset_path: str):
        """
        Initialize the recommender system.
        
        Args:
            dataset_path: Path to books.csv file
        """
        self.df = load_and_clean_dataset(dataset_path)
        
        if not validate_dataset(self.df):
            raise ValueError("Dataset validation failed")
        
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self._build_tfidf_model()
    
    def _build_tfidf_model(self):
        """Build TF-IDF model from dataset."""
        print("\n🔨 Building TF-IDF model...")
        
        # Create TF-IDF vectorizer
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            min_df=2,
            max_df=0.8,
            ngram_range=(1, 2)
        )
        
        # Fit and transform the combined text
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.df['combined_text'])
        print(f"✓ TF-IDF model built: {self.tfidf_matrix.shape}")
        print(f"  - Vocabulary size: {len(self.tfidf_vectorizer.get_feature_names_out())}")
        print(f"  - Matrix dimensions: {self.tfidf_matrix.shape[0]} books × {self.tfidf_matrix.shape[1]} features\n")
    
    def get_book_by_title(self, title: str) -> Dict:
        """
        Find a book by title (case-insensitive).
        
        Args:
            title: Book title to search for
            
        Returns:
            Dictionary with book info or None if not found
        """
        title_lower = title.lower()
        matching_books = self.df[self.df['title'].str.lower() == title_lower]
        
        if len(matching_books) > 0:
            return self._book_row_to_dict(matching_books.iloc[0])
        return None
    
    def search_books(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search books by title or description.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching books
        """
        query_lower = query.lower()
        
        # Search in title
        title_matches = self.df[self.df['title'].str.lower().str.contains(query_lower, na=False)]
        
        # Search in description
        desc_matches = self.df[self.df['description'].str.lower().str.contains(query_lower, na=False)]
        
        # Combine and remove duplicates
        results = pd.concat([title_matches, desc_matches]).drop_duplicates()
        results = results.head(limit)
        
        return [self._book_row_to_dict(row) for _, row in results.iterrows()]
    
    def get_recommendations(self, book_titles: List[str], top_n: int = 10) -> Tuple[List[Dict], str]:
        """
        Generate content-based recommendations.
        
        Algorithm:
        1. Find indices of selected books in dataset
        2. Extract TF-IDF vectors for these books
        3. Compute average vector (user profile)
        4. Calculate cosine similarity with all books
        5. Rank and return top-N
        
        Args:
            book_titles: List of 3-5 book titles selected by user
            top_n: Number of recommendations to return (default: 10)
            
        Returns:
            Tuple of (recommendations list, explanation string)
        """
        if len(book_titles) < 3:
            return [], "Please select at least 3 books"
        
        # Step 1: Find book indices
        book_indices = []
        found_books = []
        
        for title in book_titles:
            idx = self.df[self.df['title'].str.lower() == title.lower()].index
            if len(idx) > 0:
                book_indices.append(idx[0])
                found_books.append(title)
            else:
                print(f"⚠ Book not found: {title}")
        
        if len(book_indices) < 3:
            return [], f"Could not find enough selected books. Found: {found_books}"
        
        # Step 2: Extract TF-IDF vectors
        selected_vectors = self.tfidf_matrix[book_indices]
        
        # Step 3: Compute user profile vector (average)
        user_profile_vector = np.asarray(selected_vectors.mean(axis=0)).flatten()
        
        # Step 4: Calculate cosine similarity
        similarities = cosine_similarity([user_profile_vector], self.tfidf_matrix)[0]
        
        # Step 5: Get book indices sorted by similarity (exclude selected books)
        similarity_scores = list(enumerate(similarities))
        similarity_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Filter out selected books and get top-N
        recommendations_idx = [
            idx for idx, score in similarity_scores
            if idx not in book_indices
        ][:top_n]
        
        # Build recommendation list
        recommendations = []
        for idx in recommendations_idx:
            book_data = self._book_row_to_dict(self.df.iloc[idx])
            book_data['similarity_score'] = float(similarities[idx])
            book_data['score_percent'] = f"{float(similarities[idx]) * 100:.1f}%"
            recommendations.append(book_data)
        
        explanation = (
            "✓ Recommendations based on text similarity of descriptions and genres. "
            "The system analyzes your selected books and finds similar titles in the database."
        )
        
        return recommendations, explanation
    
    def _book_row_to_dict(self, row) -> Dict:
        """Convert a DataFrame row to a dictionary."""
        return {
            'title': row.get('title', 'Unknown'),
            'authors': row.get('authors', 'Unknown'),
            'description': row.get('description', 'No description available'),
            'genres': row.get('genres', 'N/A'),
            'rating': row.get('rating', 'N/A') if 'rating' in row.index else 'N/A'
        }
    
    def get_all_books(self, limit: int = None) -> List[Dict]:
        """Get all books from dataset."""
        df = self.df if limit is None else self.df.head(limit)
        return [self._book_row_to_dict(row) for _, row in df.iterrows()]
    
    def get_dataset_stats(self) -> Dict:
        """Get statistics about the dataset."""
        return {
            'total_books': len(self.df),
            'total_features': self.tfidf_matrix.shape[1] if self.tfidf_matrix is not None else 0,
            'avg_description_length': int(self.df['description'].str.len().mean())
        }
