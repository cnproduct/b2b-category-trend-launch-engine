#!/usr/bin/env python3
"""
scripts/reorder_engine.py

B2B Organic Reorder & Natural Repurchase Acceleration Engine for 36 Antigravity Global Sites.
Turns initial customer acquisitions into predictable, high-margin, recurring replenishment orders by:
1. Identifying high-frequency consumables & wear-and-tear accessory SKUs for each industry vertical.
2. Establishing 30-60-90 Day Reorder Procurement Windows.
3. Enforcing Zero-Friction Returning Buyer Incentives (0 Tooling fees, 10-14 day fast turnaround, volume rebate).
4. Generating automated replenishment alert templates for purchasing committees.
5. Providing full-fleet auditing of reorder infrastructure (Fast Reorder Portal, DPP Reorder QR, Reorder FAQ).
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
REPORTS_DIR = BASE_DIR / "reports"

from run_global_ecosystem_pipeline import GLOBAL_ECOSYSTEM_FLEET

INDUSTRY_REORDER_PROFILES = {
    "toys": {
        "cycle_days": 30,
        "cadence": "Monthly Blind Box Replenishment & Seasonal Series Restock",
        "key_consumables": ["Blind Mystery Bags (Seasonal Assortments)", "Replacement Bag Charm Hooks & Clips", "Branded PDQ Display Counter Trays", "Squeeze Sensory Refill Packs"],
        "reorder_incentives": "0 New Mold Cost on Existing Shapes, 10-Day Rapid Repeat Run, Batch Color Consistency Guarantee",
        "repeat_discount": "3% - 6% off base FOB for recurring monthly orders > 5,000 pcs"
    },
    "shoes": {
        "cycle_days": 60,
        "cadence": "Bi-Monthly Corporate Workwear & Seasonal Footwear Replenishment",
        "key_consumables": ["Orthopedic Anti-Fatigue Insoles (High wear)", "Anti-Slip High-Abrasion Outsole Units", "Flame-Retardant Kevlar Laces", "Waterproof Breathable Boot Liners"],
        "reorder_incentives": "Free Custom Logo Embossing on Reorders, 15-Day Fast Production Lane, Volume Rebate -5%",
        "repeat_discount": "5% off FOB on repeat 500+ pair runs with zero setup charges"
    },
    "tactical_boots": {
        "cycle_days": 60,
        "cadence": "Quarterly Military & Law Enforcement Uniform Contract Restocking",
        "key_consumables": ["Tactical Combat Insoles with Poron Cushioning", "Nylon Fast-Lace Hardware Replacement Kits", "Oil-Resistant Rubber Outsole Blocks"],
        "reorder_incentives": "Zero Die-Cutting Setup Fee, Guaranteed MIL-SPEC Standard Continuity, 14-Day Delivery",
        "repeat_discount": "Volume rebate ladder up to 7% for recurring defense contract supply"
    },
    "cork_footwear": {
        "cycle_days": 45,
        "cadence": "Seasonal Resort Drops & Spring/Summer Birkenstock-Style Restock",
        "key_consumables": ["Natural Cork Footbeds with Arch Support", "Replacement EVA Outsole Sheets", "Adjustable Metal Buckles & Straps"],
        "reorder_incentives": "Free Laser Engraving on Cork Footbed, 12-Day Production Lane, Mixed-Size Flexibility",
        "repeat_discount": "4% reorder incentive on repeat container loads"
    },
    "sportswear": {
        "cycle_days": 45,
        "cadence": "Seasonal Athletic Capsule Drops & Fitness Gym Uniform Reorders",
        "key_consumables": ["Silicone Heat-Transfer Logo Badges", "Custom Drawstrings & Metal Aglets", "Replacement YKK Water-Resistant Zippers"],
        "reorder_incentives": "Zero Screen-Printing Setup Fee, Dye-Lot Match Guarantee, Priority Fabric Inventory Lock",
        "repeat_discount": "5% volume credit applied directly to next production invoice"
    },
    "tactical_gear": {
        "cycle_days": 60,
        "cadence": "Bimonthly Tactical Bags & Equipment Reorders",
        "key_consumables": ["MOLLE Quick-Release Buckles & D-Rings", "Cordura Fabric Repair Patches", "Custom Tactical Patch Badges"],
        "reorder_incentives": "Free Barcode & Hangtag Customization on Reorders, 15-Day Fast Ship",
        "repeat_discount": "Tiered reorder pricing starting at 200 pcs"
    },
    "hygiene": {
        "cycle_days": 30,
        "cadence": "Monthly Rolling Container Replenishment (1x40HQ Recurring Orders)",
        "key_consumables": ["Sumitomo SAP Superabsorbent Polymer Cores", "Ultra-Soft Air-Through Nonwoven Sheets", "Elastic Ear Tabs & Frontal Tapes"],
        "reorder_incentives": "Pre-Allocated Monthly Production Slot, Raw Material Price-Lock, 15-Day Container Dispatch",
        "repeat_discount": "1.5% - 3.0% margin return on scheduled annual 12-container contracts"
    },
    "lunch_box": {
        "cycle_days": 45,
        "cadence": "Quarterly Gifting, Back-to-School & Office Catering Restock",
        "key_consumables": ["Food-Grade Silicone Replacement Gasket Rings", "Modular Removable Divider Inserts", "Cutlery Straps & Portable Utensils", "Custom Insulated Cooler Bags"],
        "reorder_incentives": "Zero Tooling Fee for Established Sizes, 12-Day Rapid Batch Run, Free Laser Logo Engraving",
        "repeat_discount": "5% discount on orders repeating within 60 days"
    },
    "stone_machinery": {
        "cycle_days": 45,
        "cadence": "45-Day Diamond Consumables & 12-Month Fleet Machine Expansion",
        "key_consumables": ["Segmented Diamond Saw Blades (Granite/Marble/Quartz)", "Quarry Diamond Wire Beads (Per Meter)", "Resin Edge-Polishing Abrasives", "CNC Vacuum Suction Pads"],
        "reorder_incentives": "VIP Air Express for Critical Spare Parts (Dispatch within 48h), Multi-Unit Expansion Discount -8%",
        "repeat_discount": "8% equipment credit on spare parts packages when upgrading machine fleet"
    },
    "stone": {
        "cycle_days": 60,
        "cadence": "Commercial Architectural Project Phasing & Landscape Paver Reorders",
        "key_consumables": ["Matching Quarry Batch Paver Bundles", "Coping Stones & Step Treads", "Joint Grout & Anti-Stain Sealers"],
        "reorder_incentives": "Guaranteed Quarry Vein & Tone Color Match, Crate-Level Traceability, Free Replacement of Broken Tiles",
        "repeat_discount": "Free sea freight insurance + 4% rebate on repeat container bookings"
    },
    "bathware": {
        "cycle_days": 60,
        "cadence": "Plumbing Maintenance Supplies & Multi-Phase Hotel/Apartment Installs",
        "key_consumables": ["Sedal Ceramic Disc Cartridges", "Neoperl Pressure-Compensating Aerators", "Braided Stainless Supply Lines (EPDM)", "Silicon Valve Washers"],
        "reorder_incentives": "Zero Core Casting Charge on Standard Shapes, 100% Pressure Test Pass Warranty, Free Gasket Kits",
        "repeat_discount": "Free replacement cartridge kit (1:20 ratio) included with all repeat wholesale orders"
    },
    "semiconductor": {
        "cycle_days": 60,
        "cadence": "Factory BOM Scheduled Replenishment & Buffer Stock Release",
        "key_consumables": ["Pin-Compatible Alternates", "Evaluation Demo Boards", "Burn-in Test Sockets", "Surface-Mount Tape & Reel Pack Refills"],
        "reorder_incentives": "12-Month Contract Price-Lock, Wafer Buffer Reservation, 48-Hour Sample Cross-Reference Turnaround",
        "repeat_discount": "Tiered volume rebate up to 10% on scheduled blanket purchase orders"
    },
    "energy_storage": {
        "cycle_days": 90,
        "cadence": "Substation Cluster Scaling & Annual Maintenance Pack Procurement",
        "key_consumables": ["Liquid Coolant Refill Drums", "Aerosol Fire Suppression Canister Replacements", "High-Voltage DC Fuses (500A/1000V)", "HVAC Intake Filters"],
        "reorder_incentives": "Free Cloud EMS Remote Upgrade, Priority Factory Acceptance Testing (FAT), Cluster Expansion Rebate -6%",
        "repeat_discount": "6% off expansion battery cabinets for existing operational sites"
    },
    "titanium": {
        "cycle_days": 60,
        "cadence": "High-End Outdoor Lifestyle Drops & OEM Reorders",
        "key_consumables": ["Laser-Etched Titanium Cutlery Accessories", "Ultralight Carabiner Clips", "Silicone Insulating Grips & Sleeves"],
        "reorder_incentives": "Zero Laser-Marking Setup Fee, Guaranteed Grade-1 Pure Titanium Standard, 10-Day Small-Batch Run",
        "repeat_discount": "5% discount for verified repeat distributor accounts"
    },
    "gifts": {
        "cycle_days": 45,
        "cadence": "Quarterly Trade Show & Corporate Swag Restock",
        "key_consumables": ["Custom Lanyards & ID Badges", "Branded Hard-Enamel Lapel Pins", "Velvet Gift Pouches", "Presentation Magnetic Boxes"],
        "reorder_incentives": "Mold Stored Free for 3 Years, 7-Day Rapid Reorder Production, Zero Artwork Setup Fee",
        "repeat_discount": "Free mold retention + 5% repeat discount on orders over $1,500"
    },
    "general": {
        "cycle_days": 60,
        "cadence": "Quarterly General Industrial Sourcing Replenishment",
        "key_consumables": ["Replacement Wear Accessories", "Maintenance Kits", "Seasonal Packaging Sleeves"],
        "reorder_incentives": "Zero Tooling Fee on Repeat PO, Priority 14-Day Production Queue",
        "repeat_discount": "3% - 5% reorder discount on repeat orders"
    }
}


class FleetReorderEngine:
    def __init__(self):
        self.fleet = GLOBAL_ECOSYSTEM_FLEET
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    def analyze_fleet_reorder_readiness(self) -> Dict[str, Any]:
        """Analyzes all 36 sites and generates specific natural reorder strategies."""
        blueprint = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_sites": len(self.fleet),
            "theme": "B2B Organic Reorder & Natural Repurchase Architecture (使用好了，自然就会复购)",
            "core_principles": [
                "1. 极速翻单零摩擦 (Fast Reorder 1-Click PO): 0 Tooling fee, 10-14 days turnaround",
                "2. 耗材与易损配件饱和曝光 (Consumables Saturation): 30-60-90天高频消耗品矩阵",
                "3. MA-DPP 溯源护照翻单入口 (Passport Reorder Gateway): 扫包装二维码一键直达翻单",
                "4. 自动化补货召回飞轮 (Automated Nurture Cadence): 采购周期节点精准触达"
            ],
            "sites": []
        }

        for site in self.fleet:
            dom = site["domain"]
            ind = site["industry"]
            name = site["name"]
            profile = INDUSTRY_REORDER_PROFILES.get(ind, INDUSTRY_REORDER_PROFILES["general"])

            site_plan = {
                "domain": dom,
                "name": name,
                "industry": ind,
                "reorder_cycle_days": profile["cycle_days"],
                "procurement_cadence": profile["cadence"],
                "key_consumables_matrix": profile["key_consumables"],
                "returning_buyer_incentives": profile["reorder_incentives"],
                "repeat_discount_policy": profile["repeat_discount"],
                "dpp_reorder_url": f"https://www.{dom}/ma-dpp#reorder",
                "sample_reorder_subject": f"[PO Restock Alert] Priority Replenishment Window for {name} ({dom})",
                "reorder_nurture_timing": {
                    "day_30": "QA Check-in & Consumables Inspection",
                    "day_60": "Container Booking & Lead-Time Forecast Alert",
                    "day_90": "Quarterly Rebate Lock & Mold Reservation Notice"
                }
            }
            blueprint["sites"].append(site_plan)

        # Save JSON Blueprint
        out_json = REPORTS_DIR / "fleet_reorder_blueprint.json"
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(blueprint, f, indent=2, ensure_ascii=False)

        # Save Markdown Summary
        out_md = REPORTS_DIR / "fleet_reorder_blueprint.md"
        self._write_markdown_report(blueprint, out_md)

        return blueprint

    def _write_markdown_report(self, data: Dict[str, Any], path: Path):
        md_lines = [
            "# 🔄 B2B 36 站群「自然复购」全链路加速引擎蓝图",
            "",
            "> **核心法则**：*“对所有出海独立站使用好了，自然就会复购。”*  ",
            "> 外贸出海独立站不仅是第一次获取询盘的展示窗口，更是**锁定老客户、缩短翻单链路、提高复购毛利的数字化工作台**。",
            "",
            "---",
            "",
            "## 🎯 自然复购四大核心支柱 (The 4 Pillars of Organic B2B Reorders)",
            "",
            "1. **⚡ 极速翻单专属通道 (1-Click Fast Reorder Portal)**：",
            "   - 老客户输入旧 PO# 或 MA-DPP 批次编码，系统自动拉取历史模具、打样色号、刀模图纸及包装条码，**0 重新开模费、0 摩擦排产**；",
            "   - 承诺 **10–14 天极速交期通道**（比首单定制快 50%）。",
            "",
            "2. **📦 耗材与易损配件矩阵饱和曝光 (Consumables Saturation)**：",
            "   - 在产品详情页下方与 MA-DPP 护照大厅常驻【原厂易损配件与消耗补给】选购区（如便当盒硅胶圈、石材锯片、安全鞋减震鞋垫、玩具补充包）；",
            "   - 将单次交易转化为 30–60 天高频细水长流的长青订单。",
            "",
            "3. **🛡️ MA-DPP 欧盟数字产品护照一键扫码翻单 (Passport Reorder Gateway)**：",
            "   - 印刷在纸箱和外壳上的 ISO/IEC 15459 追溯二维码，海外仓管和采购主管手机一扫即进 `/dpp/{sku}#reorder`；",
            "   - 直通原厂合规质检报告与翻单协议，彻底切断客户被竞品截胡的可能。",
            "",
            "4. **📅 30-60-90 天采购周期自动化温情召回 (Nurture Cadence)**：",
            "   - 契合国际海运船期与生产排期，在关键时间节点推送贴心提醒，锁定下一季度集装箱柜位。",
            "",
            "---",
            "",
            "## 📊 36 出海站群高复购配件矩阵与翻单策略全览",
            "",
            "| 序号 | 站点域名 | 企业/品牌 | 垂直行业 | 最佳翻单周期 | 核心高复购耗材/配件矩阵 | 老买家翻单权益与阶梯返点 |",
            "|:---:|---|---|---|---|---|---|"
        ]

        for i, s in enumerate(data["sites"], 1):
            dom = s["domain"]
            name = s["name"]
            ind = s["industry"]
            cycle = f"{s['reorder_cycle_days']} 天"
            consumables = "<br>• ".join([""] + s["key_consumables_matrix"][:3])
            incentives = s["returning_buyer_incentives"]
            md_lines.append(f"| **{i:02d}** | `https://www.{dom}` | {name} | {ind} | {cycle} | {consumables} | {incentives} |")

        md_lines.extend([
            "",
            "---",
            "",
            "## 📩 老客户 30-60-90 天温情补货召回模版 (InMail / Email Templates)",
            "",
            "### 30 天：质检满意度与易损耗材关怀 (Day 30 QA & Consumables Check)",
            "```text",
            "Subject: [PO Restock Alert] How is your first batch of {{PRODUCT_NAME}} performing? (Traceability ID: {{MA_DPP_CODE}})",
            "",
            "Hi {{BUYER_NAME}},",
            "",
            "Checking in to see how the recent container shipment of {{PRODUCT_NAME}} arrived at your distribution center.",
            "Full SGS test reports and ISO 15459 inspection ledger are securely archived at: https://www.{{DOMAIN}}/ma-dpp",
            "",
            "Tip: For seasonal replenishment, our returning buyer lane offers 12-day rapid production with 0 tooling charges.",
            "If your inventory requires replacement accessories ({{CONSUMABLES_LIST}}), reply to lock in this month's production slot.",
            "",
            "Best regards,",
            "{{BRAND_NAME}} Factory Direct Engineering Team",
            "```",
            "",
            "### 60 天：海运船期与排产锁单预警 (Day 60 Lead-Time & Container Lock)",
            "```text",
            "Subject: Sea Freight & Container Allocation Alert for Q2 Procurement ({{BRAND_NAME}})",
            "",
            "Hi {{BUYER_NAME}},",
            "",
            "With seasonal shipping capacity tightening, ocean transit to your target port currently requires 25–35 days.",
            "To ensure zero out-of-stock risk on your retail/wholesale shelves, we have reserved production capacity for {{BRAND_NAME}} repeat orders.",
            "",
            "⚡ Returning Buyer Priority:",
            "• Turnaround: 12–14 business days",
            "• Tooling / Setup fee: $0 (Pre-calibrated molds active)",
            "• Volume credit: 5% applied directly to current repeat PO",
            "",
            "Access 1-Click Fast Reorder: https://www.{{DOMAIN}}/ma-dpp#reorder",
            "```",
            "",
            "---",
            "Generated automatically by `b2b-category-trend-launch-engine/scripts/reorder_engine.py`."
        ])

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))


def main():
    print("=" * 80)
    print("🔄 B2B Fleet Reorder & Natural Repurchase Acceleration Engine (36 Sites)")
    print("=" * 80)
    engine = FleetReorderEngine()
    print("\n🔍 Analyzing fleet repeat-order infrastructure across all 36 sites...")
    data = engine.analyze_fleet_reorder_readiness()
    print(f"✅ Generated comprehensive fleet reorder blueprint for {data['total_sites']} sites:")
    print(f"  • JSON Blueprint: {REPORTS_DIR / 'fleet_reorder_blueprint.json'}")
    print(f"  • Markdown Report: {REPORTS_DIR / 'fleet_reorder_blueprint.md'}")
    print("\n" + "=" * 80)
    print("🏁 Natural Repurchase Engine Execution Completed.")
    print("=" * 80)


if __name__ == "__main__":
    main()
