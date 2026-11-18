#!/usr/bin/env python3
"""
Fast Remote Production Deployer & Multi-Site Synchronizer
"""

import paramiko
import os
import sys
import json
import argparse
import urllib.request

def deploy_to_server(host, port, user, password, tasks):
    print(f"\n[Deployer] Connecting to {host}:{port} as {user}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port=port, username=user, password=password, timeout=15)
    sftp = ssh.open_sftp()

    for task in tasks:
        domain = task['domain']
        sku = task['sku']
        clean_slug = task['clean_slug']
        local_html = task['local_html']
        image_files = task.get('image_files', [])
        webroot = f"/var/www/{domain}"

        print(f"\n[Deployer] Deploying to domain: {domain} (SKU: {sku})...")

        # 1. Upload Images
        remote_img_dir = f"{webroot}/images/products"
        ssh.exec_command(f"mkdir -p {remote_img_dir}")
        for img_path in image_files:
            if os.path.exists(img_path):
                fname = os.path.basename(img_path)
                dest = f"{remote_img_dir}/{fname}"
                sftp.put(img_path, dest)
                print(f"  -> Uploaded image: {fname}")

        # 2. Upload Product HTML (products/ and root alias)
        ssh.exec_command(f"mkdir -p {webroot}/products")
        remote_prod_file = f"{webroot}/products/{clean_slug}.html"
        remote_root_file = f"{webroot}/clean_slug.html"
        sftp.put(local_html, remote_prod_file)
        sftp.put(local_html, f"{webroot}/{clean_slug}.html")
        print(f"  -> Uploaded landing page to {remote_prod_file}")

        # 3. Remote In-Place Injection for products.html and sitemaps
        card_html = task.get('card_html', '')
        remote_script = f"""import os

p_path = '{webroot}/products.html'
if os.path.exists(p_path):
    with open(p_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if '{clean_slug}' not in content:
        card = '''{card_html}'''
        if '<div class="products-grid-container" id="productsGrid">' in content:
            content = content.replace('<div class="products-grid-container" id="productsGrid">', '<div class="products-grid-container" id="productsGrid">\\n' + card)
            with open(p_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("Injected card into products.html")

for sm in ['sitemap.xml', 'sitemap-products.xml']:
    sm_path = f'{webroot}/' + sm
    if os.path.exists(sm_path):
        with open(sm_path, 'r', encoding='utf-8') as f:
            sm_content = f.read()
        if '{clean_slug}' not in sm_content and '</urlset>' in sm_content:
            entry = '''  <url>
    <loc>https://{domain}/products/{clean_slug}</loc>
    <lastmod>2026-11-18</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.98</priority>
  </url>
</urlset>'''
            sm_content = sm_content.replace('</urlset>', entry)
            with open(sm_path, 'w', encoding='utf-8') as f:
                f.write(sm_content)
            print(f"Updated {{sm}}")
"""
        sftp.put(os.path.abspath(__file__), '/tmp/_deploy_worker.py') # touch
        stdin, stdout, stderr = ssh.exec_command(f'python3 -c "{remote_script}"')
        print("  -> Remote update:", stdout.read().decode().strip())

    # Fix permissions
    chown_cmd = f"chown -R {user}:{user} {webroot} 2>/dev/null || chown -R www-data:www-data {webroot} 2>/dev/null; chmod -R 755 {webroot}/products"
    if user == 'ubuntu':
        ssh.exec_command(f"echo {password} | sudo -S {chown_cmd}")
    else:
        ssh.exec_command(chown_cmd)
    print("  -> Server file permissions updated.")

    sftp.close()
    ssh.close()

def verify_live_urls(urls):
    print("\n[Deployer] Verifying Live HTTP Endpoints...")
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
    for u in urls:
        try:
            req = urllib.request.Request(u, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                print(f"  [HTTP {resp.status} OK] {u}")
        except Exception as e:
            print(f"  [FAILED] {u} -> {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Fast Remote Production Deployer")
    parser.add_argument("--config", required=True, help="Path to deployment config JSON")
    args = parser.parse_args()

    with open(args.config, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    for srv in cfg.get('servers', []):
        deploy_to_server(srv['host'], srv['port'], srv['user'], srv['password'], srv['tasks'])

    verify_live_urls(cfg.get('verify_urls', []))
