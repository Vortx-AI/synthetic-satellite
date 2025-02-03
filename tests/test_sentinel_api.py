# tests/test_sentinel_api.py

import os
import sys
import traceback
from shapely.geometry import box
import matplotlib.pyplot as plt
import numpy as np
import os
from dotenv import load_dotenv
# Add project path to sys.path to import CustomSentinelAPI
load_dotenv()

# Add project path
project_path = os.getenv('PROJECT_ROOT')
if project_path not in sys.path:
    sys.path.insert(0, project_path)

# Set credentials
os.environ["COPERNICUS_USER"] = os.getenv('COPERNICUS_USER')
os.environ["COPERNICUS_PASSWORD"] = os.getenv('COPERNICUS_PASSWORD')
if project_path not in sys.path:
    sys.path.insert(0, project_path)

from src.data_acquisition.sources.sentinel_api import CustomSentinelAPI

def test_search_and_download():
    """Test searching and downloading Sentinel data"""
    try:
        # Initialize API with SciHub endpoint
        print("Initializing API...")
        api = CustomSentinelAPI(
            api_url="https://scihub.copernicus.eu/dhus"  # Original SciHub endpoint
        )
        print("API initialized successfully!")

        # Define search parameters
        bbox_coords = (-122.5185, 37.7021, -122.3555, 37.8198)  # San Francisco Bay Area

        # Dates in YYYYMMDD format
        start_date = "20240101"
        end_date = "20240201"

        print("\nSearching for data...")
        print(f"Area: San Francisco Bay")
        print(f"Date range: {start_date} to {end_date}")
        print(f"Cloud cover limit: 20%")

        result = api.search_and_download(
            bbox=bbox_coords,
            start_date=start_date,
            end_date=end_date,
            cloud_cover=20.0
        )

        if result:
            print("\nData retrieved successfully!")
            print(f"Data shape: {result['data'].shape}")
            print("\nMetadata:")
            for key, value in result['metadata'].items():
                print(f"{key}: {value}")

            # Visualize the data
            visualize_data(result)
        else:
            print("\nNo data found for the specified criteria")

        return result

    except Exception as e:
        print(f"\nError occurred: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nNote: If you're getting authentication errors, you may need to:")
        print("1. Register at https://scihub.copernicus.eu/dhus")
        print("2. Update your credentials")
        print("3. Accept the terms and conditions on the website")
        traceback.print_exc()
        return None

def visualize_data(result):
    """Visualize the downloaded Sentinel data"""
    data = result['data']

    if data is None:
        print("No data available to visualize.")
        return

    plt.figure(figsize=(15, 5))

    # Assuming data shape is (4, height, width) for bands B02, B03, B04, B08
    # Replace this with actual processing logic

    # Dummy data for demonstration
    # Remove the following lines when implementing actual data processing
    height, width = 500, 500
    data = {
        "B02": np.random.randint(0, 3000, (height, width)),
        "B03": np.random.randint(0, 3000, (height, width)),
        "B04": np.random.randint(0, 3000, (height, width)),
        "B08": np.random.randint(0, 3000, (height, width)),
    }

    # RGB composite
    rgb = np.stack([
        data["B04"],  # Red
        data["B03"],  # Green
        data["B02"]   # Blue
    ], axis=-1)

    # Normalize for visualization
    rgb = np.clip(rgb / 3000, 0, 1)

    plt.subplot(131)
    plt.imshow(rgb)
    plt.title("RGB Composite")
    plt.axis('off')

    # NDVI
    nir = data["B08"]  # Near-Infrared
    red = data["B04"]  # Red
    ndvi = (nir - red) / (nir + red)
    ndvi = np.nan_to_num(ndvi)  # Handle division by zero

    plt.subplot(132)
    plt.imshow(ndvi, cmap='RdYlGn', vmin=-1, vmax=1)
    plt.colorbar(label='NDVI')
    plt.title("NDVI")
    plt.axis('off')

    # False color composite
    false_color = np.stack([
        data["B08"],  # NIR
        data["B04"],  # Red
        data["B03"]   # Green
    ], axis=-1)
    false_color = np.clip(false_color / 3000, 0, 1)

    plt.subplot(133)
    plt.imshow(false_color)
    plt.title("False Color (NIR)")
    plt.axis('off')

    plt.tight_layout()
    plt.show()

def test_product_info():
    """Test retrieving product information"""
    try:
        api = CustomSentinelAPI(
            api_url="https://scihub.copernicus.eu/dhus"
        )

        # Search for products first
        bbox_coords = (-122.5185, 37.7021, -122.3555, 37.8198)
        products = api.api.query(
            area=box(*bbox_coords).wkt,
            date=('20240101', '20240201'),
            platformname='Sentinel-2',
            cloudcoverpercentage=(0, 20)
        )

        if products:
            # Get first product ID
            product_id = list(products.keys())[0]
            print(f"\nRetrieving info for product ID: {product_id}")

            # Get product info
            info = api.get_product_info(product_id)
            print("\nProduct Information:")
            for key, value in info.items():
                print(f"{key}: {value}")
        else:
            print("No products found.")

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print("Testing Sentinel API functionality...\n")

    print("1. Testing search and download...")
    result = test_search_and_download()

    print("\n2. Testing product info retrieval...")
    test_product_info()