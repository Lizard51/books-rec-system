import pandas as pd
import re
from typing import Tuple


def clean_text(text):
    """Convert text to lowercase and remove extra whitespace."""
    if pd.isna(text) or text is None:
        return ""
    text = str(text).lower()
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def load_and_clean_dataset(filepath: str) -> pd.DataFrame:
    """
    Load CSV dataset and perform automatic data cleaning.
    
    Returns:
        pd.DataFrame: Cleaned dataset with combined text field for TF-IDF
    """
    try:
        df = pd.read_csv(filepath)
        print(f"✓ Loaded {len(df)} books from dataset")
    except FileNotFoundError:
        print(f"✗ Dataset file not found: {filepath}")
        return pd.DataFrame()
    
    # Step 1: Remove records without description
    df = df.dropna(subset=['description'])
    print(f"✓ After removing missing descriptions: {len(df)} books")
    
    # Step 2: Remove duplicates by title
    df = df.drop_duplicates(subset=['title'], keep='first')
    print(f"✓ After removing duplicates: {len(df)} books")
    
    # Step 3: Remove books with description < 50 characters
    df = df[df['description'].astype(str).str.len() >= 50]
    print(f"✓ After filtering short descriptions: {len(df)} books")
    
    # Step 4: Clean text fields
    df['description'] = df['description'].apply(clean_text)
    
    # Handle genres field
    if 'genres' in df.columns:
        df['genres'] = df['genres'].fillna('').apply(clean_text)
    else:
        df['genres'] = ''
    
    # Step 5: Combine description + genres into unified text field for TF-IDF
    df['combined_text'] = df['description'] + " " + df['genres']
    df['combined_text'] = df['combined_text'].apply(lambda x: re.sub(r'\s+', ' ', x).strip())
    
    # Remove any remaining duplicates based on combined text
    df = df.drop_duplicates(subset=['combined_text'], keep='first')
    print(f"✓ After removing combined text duplicates: {len(df)} books")
    
    # Ensure we have title and authors
    df['title'] = df['title'].fillna('Unknown')
    if 'authors' in df.columns:
        df['authors'] = df['authors'].fillna('Unknown')
    else:
        df['authors'] = 'Unknown'
    
    print(f"✓ Final cleaned dataset: {len(df)} books")
    return df


def validate_dataset(df: pd.DataFrame) -> bool:
    """
    Validate that the dataset has required columns and sufficient data.
    
    Returns:
        bool: True if dataset is valid, False otherwise
    """
    required_columns = ['title', 'description', 'combined_text']
    
    for col in required_columns:
        if col not in df.columns:
            print(f"✗ Missing required column: {col}")
            return False
    
    if len(df) == 0:
        print("✗ Dataset is empty")
        return False
    
    print(f"✓ Dataset validation passed: {len(df)} records")
    return True
