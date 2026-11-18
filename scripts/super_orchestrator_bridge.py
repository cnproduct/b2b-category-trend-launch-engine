#!/usr/bin/env python3
"""
scripts/super_orchestrator_bridge.py

Bi-directional integration bridge between:
1. b2b-category-trend-launch-engine (Tactical Category Trend Radar & Rapid Launch)
2. b2b-export-site-super-orchestrator (Macro Master Site-Lifecycle & MA-DPP Governance)

Enables on-demand activation of:
- Whole-site 8-stage lifecycle evaluations & stage gate audits
- MA-DPP EU ESPR 2024/1781 & ISO 15459 Node 100015 Digital Product Passport generation
- 60-day Tri-Platform (LinkedIn + Facebook + Reddit) social media growth flywheel
- Multi-domain fleet health audit across 28 global brand sites
- Fleet-wide Google Search Console (GSC) 6-cause automated remediation
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any

# Candidate resolution paths for b2b-export-site-super-orchestrator
CANDIDATE_PATHS = [
    Path(os.environ.get("SUPER_ORCHESTRATOR_PATH", "")),
    Path.home() / ".gemini" / "config" / "skills" / "b2b-export-site-super-orchestrator",
    Path("/Users/happy/Library/CloudStorage/GoogleDrive-cnproduct@gmail.com/我的云端硬盘/WPS同步盘/耐科AI创新小组/naikewebistes/b2b-export-site-super-orchestrator"),
    Path(__file__).resolve().parent.parent.parent / "b2b-export-site-super-orchestrator"
]


def resolve_super_orchestrator() -> Optional[Path]:
    """Finds the installed b2b-export-site-super-orchestrator root directory."""
    for path in CANDIDATE_PATHS:
        if path and path.exists() and (path / "SKILL.md").exists():
            return path.resolve()
    return None


class SuperOrchestratorBridge:
    def __init__(self, orchestrator_root: Optional[Path] = None):
        self.root = orchestrator_root or resolve_super_orchestrator()
        self.available = self.root is not None and self.root.exists()
        if self.available:
            self.scripts_dir = self.root / "scripts"
            self.templates_dir = self.root / "templates"
        else:
            self.scripts_dir = None
            self.templates_dir = None

    def get_status(self) -> Dict[str, Any]:
        """Returns the readiness and version status of the Super Orchestrator."""
        if not self.available:
            return {
                "available": False,
                "error": "b2b-export-site-super-orchestrator not found in candidates.",
                "candidate_paths": [str(p) for p in CANDIDATE_PATHS if p]
            }

        git_hash = "unknown"
        try:
            res = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=str(self.root),
                capture_output=True,
                text=True,
                check=False
            )
            if res.returncode == 0:
                git_hash = res.stdout.strip()
        except Exception:
            pass

        return {
            "available": True,
            "root_path": str(self.root),
            "git_commit": git_hash,
            "subsystems": {
                "ma_dpp_passport_engine": "ma-dpp-certification-master",
                "social_flywheel_engine": "b2b-ma-dpp-social-publisher",
                "lifecycle_state_machine": "templates/site-lifecycle.json",
                "fleet_site_auditor": "scripts/fleet_site_auditor.py",
                "gsc_fleet_operator": "scripts/gsc_fleet_operator.js",
                "breadcrumb_injector": "scripts/inject_geo_breadcrumbs.py"
            }
        }

    def run_fleet_audit(self, target_domain: Optional[str] = None) -> int:
        """Executes fleet health audit across 28 global sites or single site."""
        if not self.available:
            print("❌ [Bridge Error] b2b-export-site-super-orchestrator is not available.")
            return 1
        script = self.scripts_dir / "fleet_site_auditor.py"
        if not script.exists():
            print(f"❌ [Bridge Error] Script missing: {script}")
            return 1

        print(f"🌐 [Super Orchestrator Bridge] Executing fleet audit (Target: {target_domain or 'All 28 Fleet Sites'})...")
        cmd = [sys.executable, str(script)]
        return subprocess.run(cmd).returncode

    def run_dpp_flywheel(self, domain: str, industry: str = "general", days: int = 60, mode: str = "full") -> int:
        """
        Activates MA-DPP EU Digital Product Passport & 60-Day Tri-Platform Social Flywheel.
        Modes: passport, social, full, status
        """
        if not self.available:
            print("❌ [Bridge Error] b2b-export-site-super-orchestrator is not available.")
            return 1
        script = self.scripts_dir / "orchestrate_ma_dpp.py"
        if not script.exists():
            print(f"❌ [Bridge Error] Script missing: {script}")
            return 1

        print(f"🛡️ [Super Orchestrator Bridge] Activating MA-DPP Subsystem (Mode: {mode}, Domain: {domain}, Days: {days})...")
        cmd = [
            sys.executable, str(script),
            "--mode", mode,
            "--domain", domain,
            "--industry", industry,
            "--days", str(days)
        ]
        return subprocess.run(cmd).returncode

    def run_gsc_fleet(self, target_domains: Optional[List[str]] = None) -> int:
        """Invokes fleet-wide Google Search Console automated 6-cause remediation."""
        if not self.available:
            print("❌ [Bridge Error] b2b-export-site-super-orchestrator is not available.")
            return 1
        script = self.scripts_dir / "gsc_fleet_operator.js"
        if not script.exists():
            print(f"❌ [Bridge Error] Script missing: {script}")
            return 1

        print(f"🔍 [Super Orchestrator Bridge] Invoking Fleet GSC Operator via Ego Lite...")
        cmd = ["node", str(script)]
        if target_domains:
            cmd.extend(["--domains", ",".join(target_domains)])
        return subprocess.run(cmd).returncode

    def run_breadcrumb_injection(self, target_file_or_dir: str) -> int:
        """Injects WAI-ARIA breadcrumbs and BreadcrumbList JSON-LD into target HTML files."""
        if not self.available:
            print("❌ [Bridge Error] b2b-export-site-super-orchestrator is not available.")
            return 1
        script = self.scripts_dir / "inject_geo_breadcrumbs.py"
        if not script.exists():
            print(f"❌ [Bridge Error] Script missing: {script}")
            return 1

        print(f"🍞 [Super Orchestrator Bridge] Injecting GEO Breadcrumbs into {target_file_or_dir}...")
        cmd = [sys.executable, str(script), "--path", target_file_or_dir]
        return subprocess.run(cmd).returncode


def main():
    parser = argparse.ArgumentParser(
        description="Super Orchestrator Bridge for b2b-category-trend-launch-engine"
    )
    subparsers = parser.add_subparsers(dest="command", help="Bridge commands")

    # status command
    subparsers.add_parser("status", help="Check Super Orchestrator availability and version")

    # audit command
    audit_parser = subparsers.add_parser("audit", help="Run fleet or site audit")
    audit_parser.add_argument("--domain", help="Optional specific domain to audit")

    # dpp command
    dpp_parser = subparsers.add_parser("dpp", help="Activate MA-DPP Passport & Social Flywheel")
    dpp_parser.add_argument("--domain", required=True, help="Target site domain (e.g. wishtimetoys.com)")
    dpp_parser.add_argument("--industry", default="general", help="Industry vertical")
    dpp_parser.add_argument("--mode", default="full", choices=["passport", "social", "full", "status"])
    dpp_parser.add_argument("--days", type=int, default=60, help="Flywheel duration in days")

    # gsc-fleet command
    gsc_parser = subparsers.add_parser("gsc-fleet", help="Run Fleet GSC Operator")
    gsc_parser.add_argument("--domains", help="Comma-separated domains to process")

    # breadcrumbs command
    bc_parser = subparsers.add_parser("breadcrumbs", help="Inject GEO Breadcrumbs")
    bc_parser.add_argument("--path", required=True, help="Target HTML file or directory")

    args = parser.parse_args()

    bridge = SuperOrchestratorBridge()

    if args.command == "status" or not args.command:
        status = bridge.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
        sys.exit(0 if status.get("available") else 1)

    elif args.command == "audit":
        sys.exit(bridge.run_fleet_audit(args.domain))

    elif args.command == "dpp":
        sys.exit(bridge.run_dpp_flywheel(args.domain, args.industry, args.days, args.mode))

    elif args.command == "gsc-fleet":
        dom_list = [d.strip() for d in args.domains.split(",")] if args.domains else None
        sys.exit(bridge.run_gsc_fleet(dom_list))

    elif args.command == "breadcrumbs":
        sys.exit(bridge.run_breadcrumb_injection(args.path))


if __name__ == "__main__":
    main()
