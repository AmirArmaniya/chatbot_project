#!/usr/bin/env python3
"""
Script to generate initial tenant data for the chatbot application.
This creates a CSV file with sample tenant data.
"""

import os
import csv
import json
import uuid
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define the output file
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(DATA_DIR, 'tenants.csv')

# Sample tenant configurations
SAMPLE_TENANTS = [
    {
        "tenant_id": "store1",
        "name": "فروشگاه دیجیتال",
        "api_key": str(uuid.uuid4()),
        "config": json.dumps({
            "logo_url": "https://example.com/store1/logo.png",
            "primary_color": "#3366CC",
            "support_email": "support@digitalstore.com",
            "business_hours": "9:00 - 18:00",
            "products": ["موبایل", "لپتاپ", "تبلت", "لوازم جانبی"]
        }, ensure_ascii=False)
    },
    {
        "tenant_id": "store2",
        "name": "فروشگاه لباس",
        "api_key": str(uuid.uuid4()),
        "config": json.dumps({
            "logo_url": "https://example.com/store2/logo.png",
            "primary_color": "#FF6600",
            "support_email": "help@fashionstore.com",
            "business_hours": "10:00 - 20:00",
            "products": ["پیراهن", "شلوار", "کفش", "لباس زنانه", "لباس مردانه"]
        }, ensure_ascii=False)
    },
    {
        "tenant_id": "store3",
        "name": "لوازم خانگی",
        "api_key": str(uuid.uuid4()),
        "config": json.dumps({
            "logo_url": "https://example.com/store3/logo.png",
            "primary_color": "#33AA33",
            "support_email": "support@homeappliances.com",
            "business_hours": "9:00 - 19:00",
            "products": ["یخچال", "ماشین لباسشویی", "اجاق گاز", "جاروبرقی", "مایکروویو"]
        }, ensure_ascii=False)
    }
]

def generate_tenant_data():
    """Generate tenant data and write to CSV file"""
    try:
        # Create data directory if it doesn't exist
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # Write tenant data to CSV
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['tenant_id', 'name', 'api_key', 'config']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for tenant in SAMPLE_TENANTS:
                writer.writerow(tenant)
        
        logger.info(f"Successfully generated tenant data at {OUTPUT_FILE}")
        logger.info(f"Created {len(SAMPLE_TENANTS)} tenant records")
        
        # Print API keys for reference
        logger.info("API Keys for tenants:")
        for tenant in SAMPLE_TENANTS:
            logger.info(f"Tenant: {tenant['name']} (ID: {tenant['tenant_id']})")
            logger.info(f"API Key: {tenant['api_key']}")
            logger.info("-" * 40)
        
    except Exception as e:
        logger.error(f"Error generating tenant data: {str(e)}")
        raise

if __name__ == "__main__":
    generate_tenant_data()