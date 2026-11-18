#!/usr/bin/env python3
"""
Universal B2B Product Page Generator
Enforces Global Clean URLs Standard (Zero .html Policy)
"""

import os
import sys
import json
import re
import argparse

def generate_product_page(product_data, site_config, category_profile, template_path, output_dir):
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    title = product_data.get('title', 'High Quality B2B Export Product')
    short_title = product_data.get('short_title', title[:80])
    sku = site_config.get('sku', 'NK-B2B-001')
    domain = site_config.get('domain', 'https://example.com').rstrip('/')
    clean_slug = product_data.get('clean_slug', 'custom-b2b-product')
    canonical_url = f"{domain}/products/{clean_slug}"

    brand_name = site_config.get('brand_name', 'B2B Factory Direct')
    email = site_config.get('email', 'sales@example.com')
    phone = site_config.get('phone', '+86 180 6522 8363')
    wa_number = site_config.get('wa_number', '8618065228363')

    category_name = category_profile.get('name', 'General Sourcing')
    category_slug = clean_slug.split('-')[0]

    # Images
    images = product_data.get('images', [])
    hero_image = images[0] if images else '/images/products/default_product.jpg'

    # Generate Thumbnails HTML
    thumbs_html = []
    for idx, img in enumerate(images[:5]):
        border_style = 'border:2px solid #2563eb;' if idx == 0 else 'border:1px solid #e2e8f0;'
        thumbs_html.append(f'''<div style="width:80px; height:80px; border-radius:8px; {border_style} overflow:hidden; cursor:pointer;" onclick="document.getElementById('mainProductImg').src='{img}';">
  <img src="{img}" alt="{title} view {idx+1}" style="width:100%; height:100%; object-fit:cover;">
</div>''')
    thumbnails_html = '\n'.join(thumbs_html)

    # Credentials
    certs = category_profile.get('certifications', ['ISO 9001:2015', 'CE Marking'])
    cred_html = []
    for c in certs[:5]:
        cred_html.append(f'''<div style="display:flex; align-items:center; gap:8px;">
  <span style="color:#16a34a; font-weight:700;">✓</span>
  <span>{c} Certified & Verified</span>
</div>''')
    credentials_html = '\n'.join(cred_html)

    # Technical Specifications
    specs = product_data.get('specs', {})
    if not specs:
        specs = {
            "Product Classification": category_name,
            "Primary Materials": ", ".join(category_profile.get('materials', ['Industrial Grade Steel', 'ABS'])),
            "Quality Compliance": ", ".join(certs[:3]),
            "Standard Packaging": ", ".join(category_profile.get('packaging_options', ['Export Master Carton'])),
            "Production Turnaround": category_profile.get('lead_time', '15–20 days'),
            "OEM / Customization": "Custom logo, packaging, Pantone color matching, private labeling"
        }

    spec_rows = []
    for idx, (k, v) in enumerate(specs.items()):
        bg = 'background:#f8fafc;' if idx % 2 == 0 else ''
        spec_rows.append(f'''<tr style="border-bottom:1px solid #e2e8f0; {bg}">
  <td style="padding:10px 16px; font-weight:600; color:#475569; width:35%;">{k}</td>
  <td style="padding:10px 16px; color:#1e293b;">{v}</td>
</tr>''')
    spec_rows_html = '\n'.join(spec_rows)

    fob_price = product_data.get('fob_price', category_profile.get('typical_fob_range', '$1.00 - $5.00 / pc'))
    moq = product_data.get('moq', category_profile.get('default_moq', '500 pcs'))
    meta_desc = product_data.get('meta_desc', f"Factory direct wholesale supply of {title}. Certified with {', '.join(certs[:3])}. Direct OEM/ODM manufacturer pricing from {brand_name}.")
    keywords = ", ".join(category_profile.get('keywords', []))

    # Schema JSON-LD Graph
    schema_graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": ["Organization", "ManufacturingBusiness", "LocalBusiness"],
                "@id": f"{domain}/#organization",
                "name": brand_name,
                "url": f"{domain}/",
                "logo": f"{domain}/images/logo.png",
                "email": email,
                "telephone": phone
            },
            {
                "@type": "BreadcrumbList",
                "@id": f"{canonical_url}#breadcrumb",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{domain}/"},
                    {"@type": "ListItem", "position": 2, "name": "Products", "item": f"{domain}/products"},
                    {"@type": "ListItem", "position": 3, "name": short_title, "item": canonical_url}
                ]
            },
            {
                "@type": "Product",
                "@id": f"{canonical_url}#product",
                "name": title,
                "description": meta_desc,
                "image": [f"{domain}{hero_image}" if not hero_image.startswith('http') else hero_image],
                "sku": sku,
                "mpn": sku,
                "category": category_name,
                "brand": {"@type": "Brand", "name": brand_name},
                "manufacturer": {"@id": f"{domain}/#organization"},
                "offers": {
                    "@type": "AggregateOffer",
                    "priceCurrency": "USD",
                    "price": fob_price.replace('$', '').split(' ')[0],
                    "availability": "https://schema.org/InStock",
                    "seller": {"@id": f"{domain}/#organization"}
                }
            }
        ]
    }
    schema_json_ld = f'<script type="application/ld+json">\n{json.dumps(schema_graph, indent=2, ensure_ascii=False)}\n</script>'

    # Replace Template Tokens
    replacements = {
        '{{PRODUCT_TITLE}}': title,
        '{{PRODUCT_SHORT_TITLE}}': short_title,
        '{{PRODUCT_SKU}}': sku,
        '{{PRODUCT_META_DESC}}': meta_desc,
        '{{PRODUCT_KEYWORDS}}': keywords,
        '{{CANONICAL_URL}}': canonical_url,
        '{{SITE_DOMAIN}}': domain,
        '{{CLEAN_SLUG}}': clean_slug,
        '{{BRAND_NAME}}': brand_name,
        '{{CONTACT_EMAIL}}': email,
        '{{CONTACT_PHONE}}': phone,
        '{{WA_NUMBER}}': wa_number,
        '{{CATEGORY_NAME}}': category_name,
        '{{CATEGORY_SLUG}}': category_slug,
        '{{HERO_IMAGE_URL}}': hero_image,
        '{{THUMBNAILS_HTML}}': thumbnails_html,
        '{{CREDENTIALS_HTML}}': credentials_html,
        '{{FOB_PRICE_STRING}}': fob_price,
        '{{MOQ_STRING}}': moq,
        '{{PRODUCT_LONG_DESCRIPTION}}': product_data.get('long_description', meta_desc),
        '{{SPEC_ROWS_HTML}}': spec_rows_html,
        '{{SCHEMA_JSON_LD}}': schema_json_ld
    }

    rendered_html = template
    for placeholder, val in replacements.items():
        rendered_html = rendered_html.replace(placeholder, str(val))

    # Clean URL Sanity Check
    rendered_html = rendered_html.replace('.html"', '"').replace(".html'", "'")

    os.makedirs(output_dir, exist_ok=True)
    out_file = os.path.join(output_dir, f"{clean_slug}.html")
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(rendered_html)
    print(f"[Page Generator] Successfully generated: {out_file} ({len(rendered_html)} bytes)")
    return out_file

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Universal B2B Product Page Generator")
    parser.add_argument("--productJson", required=True, help="Path to parsed product JSON")
    parser.add_argument("--siteConfig", required=True, help="Path to site configuration JSON")
    parser.add_argument("--category", default="toys", help="Category profile key")
    parser.add_argument("--template", default="templates/b2b_product_page_template.html", help="Template path")
    parser.add_argument("--outDir", default="./dist", help="Output directory")
    args = parser.parse_args()

    with open(args.productJson, 'r', encoding='utf-8') as f:
        p_data = json.load(f)
    with open(args.siteConfig, 'r', encoding='utf-8') as f:
        s_conf = json.load(f)
    
    profiles_path = os.path.join(os.path.dirname(__file__), '../templates/category_profiles.json')
    with open(profiles_path, 'r', encoding='utf-8') as f:
        profiles = json.load(f).get('categories', {})
    
    cat_profile = profiles.get(args.category.lower(), profiles.get('toys'))
    generate_product_page(p_data, s_conf, cat_profile, args.template, args.outDir)
