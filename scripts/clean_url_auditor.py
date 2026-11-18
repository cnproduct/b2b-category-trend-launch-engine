#!/usr/bin/env python3
"""
Zero .html Policy & Clean URLs Quality Auditor
Scans HTML, XML, and JSON files to detect illegal static .html extensions.
"""

import os
import sys
import re
import argparse

def audit_clean_urls(target_dir):
    violations = []
    total_files = 0

    print(f"\n[Clean URL Auditor] Auditing directory: {target_dir}")
    for root, _, files in os.walk(target_dir):
        for f in files:
            if f.endswith('.html') or f.endswith('.xml'):
                total_files += 1
                fpath = os.path.join(root, f)
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as fp:
                    content = fp.read()

                # 1. Canonical tag check
                canonicals = re.findall(r'<link[^>]*rel=[\"\']canonical[\"\'][^>]*href=[\"\']([^\"\']+)[\"\']', content, re.IGNORECASE)
                for c in canonicals:
                    if c.endswith('.html'):
                        violations.append((fpath, "Canonical with .html", c))

                # 2. og:url check
                og_urls = re.findall(r'<meta[^>]*property=[\"\']og:url[\"\'][^>]*content=[\"\']([^\"\']+)[\"\']', content, re.IGNORECASE)
                for o in og_urls:
                    if o.endswith('.html'):
                        violations.append((fpath, "og:url with .html", o))

                # 3. Internal href check (skip external http/https, mailto, tel, javascript)
                hrefs = re.findall(r'href=[\"\'](/[^\"\'#?]+\.html|[^\"\'#?:/]+\.html)[\"\'#?]', content, re.IGNORECASE)
                for h in hrefs:
                    if h.endswith('.html'):
                        violations.append((fpath, "Internal href with .html", h))

                # 4. Sitemap <loc> check
                if f.endswith('.xml'):
                    locs = re.findall(r'<loc>([^<]+)</loc>', content)
                    for l in locs:
                        if l.endswith('.html'):
                            violations.append((fpath, "Sitemap loc with .html", l))

    print(f"[Clean URL Auditor] Scanned {total_files} files.")
    if violations:
        print(f"\n❌ [FAILED] Found {len(violations)} Clean URL violations:")
        for v in violations:
            print(f"  - [{v[1]}] in {v[0]}: {v[2]}")
        return False
    else:
        print(f"✅ [PASSED] 100% Zero .html Policy compliant. No violations found.")
        return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Clean URL Auditor")
    parser.add_argument("--dir", default=".", help="Target directory to audit")
    args = parser.parse_args()

    success = audit_clean_urls(args.dir)
    sys.exit(0 if success else 1)
