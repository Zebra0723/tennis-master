from utils import ensure_reports_dir, report_path, utc_now
from stars import build_stars_section
from gear import build_gear_section
from improvement import build_improvement_section

def main():
    ensure_reports_dir()
    path = report_path()

    report = []
    report.append("# 🎾 Daily Tennis Intelligence Report\n")
    report.append(f"- Date (UTC): {utc_now()}")
    report.append("- Region: UK")
    report.append("- Status: Pipeline ran successfully\n")
    report.append(build_stars_section())
    report.append(build_gear_section())
    report.append(build_improvement_section())

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(report))

    print(f"Report written to {path}")

if __name__ == "__main__":
    main()
