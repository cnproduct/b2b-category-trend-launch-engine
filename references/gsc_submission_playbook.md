# 🔍 Google Search Console (GSC) Automated Indexing Playbook

## 1. Overview
This playbook defines the standardized protocol for submitting newly deployed B2B product URLs and XML sitemaps to Google Search Console via authenticated browser sessions in **Ego Lite (`ego-browser`)**.

---

## 2. Prerequisites & Task Space Architecture
Ego Lite maintains authenticated sessions without re-authenticating for Google services.
Always allocate an isolated task space:
```javascript
const space = await taskSpace("gsc-indexing");
const page = space.page("p1");
```

---

## 3. Step-by-Step Procedure

### Step 1: Property Identification
Navigate directly using `resource_id`:
- **Domain Property**: `https://search.google.com/search-console?resource_id=sc-domain:example.com`
- **URL-Prefix Property**: `https://search.google.com/search-console?resource_id=https%3A%2F%2Fwww.example.com%2F`

### Step 2: Sitemap Submission
1. Navigate to: `https://search.google.com/search-console/sitemaps?resource_id={ENCODED_RESOURCE_ID}`
2. Locate the input field: `input[aria-label*="sitemap" i]`
3. Enter sitemap relative path (e.g. `sitemap-products.xml` or `sitemap.xml`).
4. Click `SUBMIT`.
5. Capture proof screenshot: `gsc_sitemap_submitted.png`.

### Step 3: Top-Bar URL Inspection
1. Navigate to GSC Overview.
2. Locate top inspection bar: `input[placeholder*="Inspect" i], input[aria-label*="Inspect" i]`.
3. Type the full Clean URL (e.g. `https://example.com/products/custom-item`).
4. Press `Enter`.
5. Wait for Google's live retrieval dialog to finish.

### Step 4: Live URL Test & Request Indexing
1. Click `REQUEST INDEXING` (or `TEST LIVE URL` if first time).
2. Monitor polling status for confirmation text:
   - `"Indexing requested"`
   - `"URL was added to priority crawl queue"`
3. Capture final confirmation screenshot: `gsc_indexing_confirmed.png`.
