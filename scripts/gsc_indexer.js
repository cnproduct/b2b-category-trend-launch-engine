#!/usr/bin/env node
/**
 * GSC Indexer - Automated Google Search Console Sitemap & URL Indexing
 * Powered by Ego Lite (`ego-browser`)
 * 
 * Usage:
 *   ego-browser nodejs scripts/gsc_indexer.js --resourceId "sc-domain:wishtimetoys.com" --url "https://wishtimetoys.com/products/..." --sitemap "sitemap-products.xml"
 */

import { parseArgs } from 'node:util';
import path from 'node:path';

const { values } = parseArgs({
  options: {
    resourceId: { type: 'string', required: true },
    url: { type: 'string', required: true },
    sitemap: { type: 'string', default: 'sitemap-products.xml' },
    outDir: { type: 'string', default: './gsc_proofs' }
  },
  allowPositionals: true
});

const resourceId = values.resourceId;
const targetUrl = values.url;
const sitemapName = values.sitemap;
const outDir = path.resolve(process.cwd(), values.outDir);

console.log(`[GSC Indexer] Starting GSC indexing automation for: ${targetUrl}`);
console.log(`[GSC Indexer] Resource ID: ${resourceId}`);

const space = await taskSpace(`gsc-${Date.now()}`);
const page = space.page("p1");

// 1. Submit Sitemap
const sitemapsUrl = `https://search.google.com/search-console/sitemaps?resource_id=${encodeURIComponent(resourceId)}`;
console.log(`[GSC Indexer] Navigating to Sitemaps: ${sitemapsUrl}`);
await page.goto(sitemapsUrl, { waitUntil: "domcontentloaded", timeout: 45000 });
await page.waitForTimeout(4000);

await page.evaluate((sm) => {
  const input = document.querySelector('input[aria-label*="sitemap" i], input[placeholder*="sitemap" i], input[type="text"]');
  if (input) {
    input.focus();
    input.value = sm;
    input.dispatchEvent(new Event('input', { bubbles: true }));
  }
}, sitemapName);
await page.waitForTimeout(1000);

await page.evaluate(() => {
  const btns = Array.from(document.querySelectorAll('button, div[role="button"]'));
  const submitBtn = btns.find(b => b.innerText?.trim().toUpperCase() === "SUBMIT");
  if (submitBtn) submitBtn.click();
});
await page.waitForTimeout(4000);

// Close confirmation modal
await page.evaluate(() => {
  const btns = Array.from(document.querySelectorAll('button, div[role="button"]'));
  const gotItBtn = btns.find(b => b.innerText?.trim().toUpperCase() === "GOT IT");
  if (gotItBtn) gotItBtn.click();
});
await page.waitForTimeout(1500);

const sitemapProof = path.join(outDir, 'gsc_sitemap_submitted.png');
await page.screenshot({ path: sitemapProof });
console.log(`[GSC Indexer] Saved sitemap proof: ${sitemapProof}`);

// 2. URL Inspection & Request Indexing
console.log(`[GSC Indexer] Navigating to Overview to inspect URL: ${targetUrl}`);
const overviewUrl = `https://search.google.com/search-console?resource_id=${encodeURIComponent(resourceId)}`;
await page.goto(overviewUrl, { waitUntil: "domcontentloaded", timeout: 45000 });
await page.waitForTimeout(4000);

// Type URL in top inspection bar
const inspectInputFound = await page.evaluate((u) => {
  const inputs = Array.from(document.querySelectorAll('input'));
  const inp = inputs.find(i => {
    const ph = (i.placeholder || "").toLowerCase();
    const al = (i.getAttribute('aria-label') || "").toLowerCase();
    return ph.includes("inspect") || al.includes("inspect") || ph.includes("url") || al.includes("url");
  });
  if (inp) {
    inp.focus();
    inp.value = u;
    inp.dispatchEvent(new Event('input', { bubbles: true }));
    return true;
  }
  return false;
}, targetUrl);

if (inspectInputFound) {
  console.log(`[GSC Indexer] Found inspection input. Pressing Enter...`);
  await page.keyboard.press("Enter");
  await page.waitForTimeout(8000);

  // Click Request Indexing or Test Live URL
  const clickStatus = await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button, div[role="button"], span'));
    const req = btns.find(b => b.innerText?.trim().toUpperCase() === "REQUEST INDEXING");
    const test = btns.find(b => b.innerText?.trim().toUpperCase() === "TEST LIVE URL");
    if (req) {
      req.click();
      return "REQUEST INDEXING";
    } else if (test) {
      test.click();
      return "TEST LIVE URL";
    }
    return "NONE_FOUND";
  });
  console.log(`[GSC Indexer] Action button clicked: ${clickStatus}`);

  // Wait for submission confirmation
  for (let i = 0; i < 12; i++) {
    await page.waitForTimeout(5000);
    const status = await page.evaluate(() => {
      const text = document.body.innerText;
      return text.includes("Indexing requested") || text.includes("priority crawl queue") || text.includes("Quota exceeded");
    });
    if (status) break;
  }

  const indexingProof = path.join(outDir, 'gsc_indexing_confirmed.png');
  await page.screenshot({ path: indexingProof });
  console.log(`[GSC Indexer] Saved indexing proof: ${indexingProof}`);
} else {
  console.warn(`[GSC Indexer] Inspection top bar input not found.`);
}
