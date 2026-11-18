#!/usr/bin/env node
/**
 * Marketplace Scraper - Benchmark Sourcing & Competitor Reverse Engineering
 * Powered by Ego Lite (`ego-browser`)
 * 
 * Usage:
 *   ego-browser nodejs scripts/marketplace_scraper.js --query "collectible bag charm toys" --url "https://www.ebay.com/itm/..." --outDir "./scraped_product"
 */

import { parseArgs } from 'node:util';
import fs from 'node:fs';
import path from 'node:path';

const { values } = parseArgs({
  options: {
    query: { type: 'string', default: '' },
    url: { type: 'string', default: '' },
    outDir: { type: 'string', default: './scraped_product' }
  },
  allowPositionals: true
});

const query = values.query;
let targetUrl = values.url;
const outDir = path.resolve(process.cwd(), values.outDir);
fs.mkdirSync(outDir, { recursive: true });

console.log(`[Marketplace Scraper] Initializing benchmark search for query: "${query}"...`);

const space = await taskSpace(`scraper-${Date.now()}`);
const page = space.page("p1");

if (!targetUrl && query) {
  // 1. Search Google Images / Google Shopping to identify the top authority listing
  const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(query)}&tbm=shop`;
  console.log(`[Marketplace Scraper] Searching Google Shopping: ${searchUrl}`);
  await page.goto(searchUrl, { waitUntil: "domcontentloaded", timeout: 45000 });
  await page.waitForTimeout(4000);

  const foundUrl = await page.evaluate(() => {
    const links = Array.from(document.querySelectorAll('a[href*="ebay.com/itm/"], a[href*="amazon.com/dp/"], a[href*="walmart.com/ip/"], a[href*="shop."]'));
    return links.length > 0 ? links[0].href : null;
  });

  if (foundUrl) {
    targetUrl = foundUrl;
    console.log(`[Marketplace Scraper] Auto-discovered benchmark product URL: ${targetUrl}`);
  } else {
    // Fallback to eBay direct search
    targetUrl = `https://www.ebay.com/sch/i.html?_nkw=${encodeURIComponent(query)}&_sacat=0`;
    console.log(`[Marketplace Scraper] Falling back to eBay search: ${targetUrl}`);
  }
}

if (!targetUrl) {
  console.error(`[Marketplace Scraper] No target URL or query provided.`);
  process.exit(1);
}

console.log(`[Marketplace Scraper] Scraping product benchmark from: ${targetUrl}`);
await page.goto(targetUrl, { waitUntil: "domcontentloaded", timeout: 45000 });
await page.waitForTimeout(4000);

const screenshotPath = path.join(outDir, 'benchmark_listing_snapshot.png');
await page.screenshot({ path: screenshotPath });
console.log(`[Marketplace Scraper] Saved listing snapshot: ${screenshotPath}`);

// Extract high-resolution image assets and product metadata
const productData = await page.evaluate(() => {
  const title = document.querySelector('h1')?.innerText?.trim() || document.title;
  const price = document.querySelector('.x-price-primary, [itemprop="price"], .a-price .a-offscreen')?.innerText?.trim() || "";
  
  // High-res image filtering (eBay, Amazon, Shopify)
  const allImages = Array.from(document.querySelectorAll('img'))
    .map(i => i.src || i.getAttribute('data-src') || i.getAttribute('data-zoom-src'))
    .filter(Boolean);

  const cleanImages = allImages.map(src => {
    // eBay high-res upgrade
    if (src.includes('ebayimg.com/images/g/')) {
      return src.replace(/s-l\d+\./, 's-l1600.');
    }
    // Amazon high-res upgrade
    if (src.includes('images-amazon.com/images/I/') || src.includes('m.media-amazon.com/images/I/')) {
      return src.replace(/\._AC_[^.]+\./, '._AC_SL1500.');
    }
    return src;
  });

  // Extract tabular specifics if available
  const specifics = Array.from(document.querySelectorAll('.ux-layout-section-evo__item, .ux-labels-values, #productDetails_techSpec_section_1 tr, .prod-spec-table tr')).map(el => {
    return el.innerText.trim();
  }).filter(Boolean);

  return {
    title,
    price,
    images: [...new Set(cleanImages)].slice(0, 8),
    specifics: specifics.slice(0, 20)
  };
});

productData.scrapedUrl = targetUrl;
productData.snapshot = screenshotPath;

const outJsonPath = path.join(outDir, 'product_data.json');
fs.writeFileSync(outJsonPath, JSON.stringify(productData, null, 2), 'utf-8');
console.log(`[Marketplace Scraper] Saved parsed product data: ${outJsonPath}`);
console.log(`[Marketplace Scraper] Found ${productData.images.length} high-res candidate images.`);
