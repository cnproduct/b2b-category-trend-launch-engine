# 🌐 Global Clean URLs Standard (Zero `.html` Policy)

## 1. Core Rule & Architecture
Any modern, professional B2B export portal must never expose static `.html` extensions in browser address bars, internal links, canonical tags, OpenGraph metadata, or XML sitemaps. Clean URLs ensure semantic search indexing, improved click-through rates, and prevention of duplicate content penalties.

---

## 2. Forbidden vs. Mandatory Syntax

| Component | ❌ Strictly Forbidden | ✅ Mandatory Standard |
|---|---|---|
| **Home Link** | `href="index.html"` | `href="./"` or `href="/"` |
| **Catalog / Detail** | `href="products.html"` | `href="products"` or `href="/products"` |
| **Product Slug** | `href="products/item.html"` | `href="products/item"` |
| **Anchor Link** | `href="products.html#features"` | `href="products#features"` |
| **Canonical Tag** | `<link rel="canonical" href=".../page.html">` | `<link rel="canonical" href=".../page">` |
| **OpenGraph URL** | `<meta property="og:url" content=".../page.html">` | `<meta property="og:url" content=".../page">` |
| **Sitemap `<loc>`** | `<loc>https://domain.com/item.html</loc>` | `<loc>https://domain.com/item</loc>` |

---

## 3. Server-Side Routing Configurations

### A. Nginx (`/etc/nginx/sites-available/...`)
```nginx
server {
    server_name example.com;
    root /var/www/example.com;
    index index.html;

    # Clean URL routing without .html extension
    location / {
        try_files $uri.html $uri $uri/ =404;
    }

    # 301 Redirect legacy .html requests to Clean URLs
    if ($request_uri ~ ^/(.*)\.html(\?.*)?$) {
        return 301 /$1$2;
    }
}
```

### B. Vercel (`vercel.json`)
```json
{
  "version": 2,
  "cleanUrls": true,
  "trailingSlash": false
}
```

### C. Cloudflare Pages & GitHub Pages
Native clean URL resolution is supported out of the box when linking with relative or absolute extensionless paths.
