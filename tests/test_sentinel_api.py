# tests/test_direct_api.py

import os
import requests
from requests.auth import HTTPBasicAuth
from shapely.geometry import box
import json

# Set your Copernicus credentials
COPERNICUS_USER = os.getenv("COPERNICUS_USER", "your_username")
COPERNICUS_PASSWORD = os.getenv("COPERNICUS_PASSWORD", "your_password")

# Define the API endpoint (Replace with the correct endpoint)
API_URL = "https://dataspace.copernicus.eu/apihub/search"

def direct_api_query(bbox, start_date, end_date, cloud_cover=20.0):
    """Directly query the Copernicus Data Space API."""
    footprint = box(*bbox).wkt
    query = f"footprint:\"Intersects({footprint})\" AND beginPosition:[{start_date}T00:00:00Z TO {end_date}T00:00:00Z] AND cloudcoverpercentage:[0 TO {cloud_cover}] AND platformname:Sentinel-2 AND producttype:S2MSI2A"

    params = {
        "format": "json",
        "rows": 100,
        "start": 0,
        "q": query
    }

    try:
        response = requests.get(API_URL, params=params, auth=HTTPBasicAuth(COPERNICUS_USER, COPERNICUS_PASSWORD), timeout=60)
        response.raise_for_status()  # Raises stored HTTPError, if one occurred.

        data = response.json()
        products = data.get('products', [])
        return products

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # e.g., 401 Unauthorized
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}")
    except json.JSONDecodeError as json_err:
        print(f"JSON decode error: {json_err}")

    return []

if __name__ == "__main__":
    bbox = (-122.5185, 37.7021, -122.3555, 37.8198)  # San Francisco Bay Area
    start_date = "2024-01-01"
    end_date = "2024-02-01"

    products = direct_api_query(bbox, start_date, end_date)

    if products:
        print(f"Found {len(products)} products:")
        for product in products:
            print(json.dumps(product, indent=2))
    else:
        print("No products found or an error occurred.")
