#!/usr/bin/env python3
"""
Unit and Integration Test Suite for B2B Category Trend Launch Engine
"""

import os
import sys
import unittest
import json

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, 'scripts'))

from page_generator import generate_product_page
from clean_url_auditor import audit_clean_urls

class TestCategoryEngine(unittest.TestCase):
    def setUp(self):
        self.profiles_path = os.path.join(base_dir, 'templates', 'category_profiles.json')
        self.template_path = os.path.join(base_dir, 'templates', 'b2b_product_page_template.html')
        self.test_dist = os.path.join(base_dir, 'tests', 'test_output')
        os.makedirs(self.test_dist, exist_ok=True)

    def test_category_profiles_integrity(self):
        with open(self.profiles_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        categories = data.get('categories', {})
        for cat in ['toys', 'shoes', 'garments', 'lunch box', 'stone machine']:
            self.assertIn(cat, categories, f"Category '{cat}' missing from category_profiles.json")
            profile = categories[cat]
            self.assertTrue(len(profile.get('keywords', [])) > 0)
            self.assertTrue(len(profile.get('certifications', [])) > 0)

    def test_page_generator_clean_urls(self):
        product_data = {
            "title": "Automated 5-Axis CNC Bridge Saw Machine",
            "short_title": "5-Axis CNC Bridge Saw",
            "clean_slug": "5-axis-cnc-bridge-saw-machine",
            "images": ["/images/products/cnc_bridge_saw.jpg"],
            "fob_price": "$18,500 - $26,000 / set",
            "moq": "1 Set"
        }
        site_config = {
            "domain": "https://hlstonemachine.com",
            "brand_name": "HL Stone Machinery",
            "sku": "HL-CNC-5A",
            "email": "info@hlstonemachine.com",
            "phone": "+86 180 6522 8363",
            "wa_number": "8618065228363"
        }
        with open(self.profiles_path, 'r', encoding='utf-8') as f:
            profiles = json.load(f)['categories']
        cat_profile = profiles['stone machine']

        out_file = generate_product_page(product_data, site_config, cat_profile, self.template_path, self.test_dist)
        self.assertTrue(os.path.exists(out_file))

        # Audit generated page with Clean URL auditor
        passed = audit_clean_urls(self.test_dist)
        self.assertTrue(passed, "Clean URL Auditor failed on generated output!")

if __name__ == '__main__':
    unittest.main()
