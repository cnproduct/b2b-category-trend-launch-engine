#!/usr/bin/env node
/**
 * Trend Radar - Google Trends Automated Category Scout
 * Powered by Ego Lite (`ego-browser`)
 * 
 * Usage:
 *   ego-browser nodejs scripts/trend_radar.js --category "toys" --geo "US" --time "now 7-d"
 */

import { parseArgs } from 'node:util';
import fs from 'node:fs';
import path from 'node:path';

const { values } = parseArgs({
  options: {
    category: { type: 'string', default: 'toys' },
    geo: { type: 'string', default: 'US' },
    time: { type: 'string', default: 'now 7-d' },
    output: { type: 'string', default: 'trends_report.json' }
  },
  allowPositionals: true
});

const category = values.category;
const geo = values.geo;
const timeRange = encodeURIComponent(values.time);
const outPath = values.output;

console.log(`[Trend Radar] Scanning Google Trends for category: "${category}" (Geo: ${geo}, Time: ${values.time})...`);

const space = await taskSpace(`trend-radar-${Date.now()}`);
const page = space.page("p1");

const trendsUrl = `https://trends.google.com/trends/explore?date=${timeRange}&geo=${geo}&q=${encodeURIComponent(category)}`;
console.log(`[Trend Radar] Navigating to: ${trendsUrl}`);

try {
  await page.goto(trendsUrl, { waitUntil: "domcontentloaded", timeout: 45000 });
  await page.waitForTimeout(5000);

  const screenshotPath = path.resolve(process.cwd(), `trends_${category.replace(/\s+/g, '_')}_${geo}.png`);
  await page.screenshot({ path: screenshotPath });
  console.log(`[Trend Radar] Saved visual proof screenshot: ${screenshotPath}`);

  // Extract Top & Rising Queries
  const trendsData = await page.evaluate(() => {
    const tables = Array.from(document.querySelectorAll('widget[type="item_list"], .trends-widget, [class*="widget"]'));
    const risingItems = [];
    const topItems = [];

    // Parse list items
    const rows = Array.from(document.querySelectorAll('div[role="row"], li, tr, div[class*="item"]'));
    rows.forEach(r => {
      const text = r.innerText?.trim() || "";
      const lines = text.split('\n').map(s => s.trim()).filter(Boolean);
      if (lines.length >= 2) {
        const query = lines[0];
        const growth = lines[1];
        if (growth.includes('+') || growth.includes('%') || growth.toLowerCase().includes('breakout')) {
          risingItems.push({ query, growth });
        }
      }
    });

    return {
      title: document.title,
      rising: risingItems.slice(0, 20),
      url: window.location.href
    };
  });

  const report = {
    category,
    geo,
    time: values.time,
    timestamp: new Date().toISOString(),
    trendsUrl,
    screenshot: screenshotPath,
    data: trendsData
  };

  fs.writeFileSync(outPath, JSON.stringify(report, null, 2), 'utf-8');
  console.log(`[Trend Radar] Successfully generated trend report: ${outPath}`);
  console.log(`[Trend Radar] Top Rising Queries:`, JSON.stringify(trendsData.rising.slice(0, 5), null, 2));

} catch (err) {
  console.error(`[Trend Radar] Error during Trends exploration:`, err);
  process.exit(1);
}
