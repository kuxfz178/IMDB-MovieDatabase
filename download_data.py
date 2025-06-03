#!/usr/bin/env python3
"""
Download IMDb dataset files automatically

This script downloads IMDb's non-commercial datasets for personal use.
Data source: https://developer.imdb.com/non-commercial-datasets/
Please ensure compliance with IMDb's terms and conditions.
"""

import os
import urllib.request
import gzip
import shutil

def download_and_extract(url, filename):
    """Download and extract a gzipped file"""
    print(f"Downloading {filename}...")
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Download the gzipped file
    gz_filename = f"data/{filename}.gz"
    urllib.request.urlretrieve(url, gz_filename)
    
    # Extract the file
    print(f"Extracting {filename}...")
    with gzip.open(gz_filename, 'rb') as f_in:
        with open(f"data/{filename}", 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    # Remove the gzipped file
    os.remove(gz_filename)
    print(f"✅ {filename} ready!")

def main():
    """Download all required IMDb dataset files"""
    print("🎬 Downloading IMDb dataset files...")
    print("📋 Data source: https://developer.imdb.com/non-commercial-datasets/")
    print("⚖️  For personal and non-commercial use only")
    print("This may take several minutes depending on your internet connection.\n")
    
    files_to_download = [
        ("https://datasets.imdbws.com/title.basics.tsv.gz", "title.basics.tsv"),
        # Uncomment if you need additional datasets:
        # ("https://datasets.imdbws.com/name.basics.tsv.gz", "name.basics.tsv"),
        # ("https://datasets.imdbws.com/title.akas.tsv.gz", "title.akas.tsv"),
    ]
    
    for url, filename in files_to_download:
        try:
            download_and_extract(url, filename)
        except Exception as e:
            print(f"❌ Error downloading {filename}: {e}")
            return False
    
    print("\n🎉 All files downloaded successfully!")
    print("You can now run: python database_setup.py")
    return True

if __name__ == "__main__":
    main() 