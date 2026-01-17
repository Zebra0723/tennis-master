from utils import ensure_reports_dir, report_path, utc_now_iso_min
from stars import build_stars_section
from gear import build_gear_section
from improvement import build_improvement_section

def build_report() -> str:
    parts = []
    parts.append("# 🎾 Daily Tennis Intelligence Report\n")
    parts.append(f"- Date (UTC): {utc_now_iso_min()}")
    parts.append("- Region: UK")
    parts.append("- Status: Pipeline ran successfully\n")

    parts.append(build_stars_section())
    parts.append(build_gear_section())
    parts.append(build_improvement_section())

    return "\n".join(parts).strip() + "\n"

def main():
    ensure_reports_dir()
    path = report_path(prefix="tennis_report")
    report_md = build_report()

    with open(path, "w", encoding="utf-8") as f:
        f.write(report_md)

    print(f"Report written to {path}")

if __name__ == "__main__":
    main()
