import os
import subprocess
import sys

if __package__ in (None, ""):
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from app.collectors.system import collect_system_info
from app.collectors.hardware import collect_hardware_info
from app.collectors.logs import collect_error_logs
from app.collectors.service_diagnostics import get_service_diagnostics

from app.analyzers.log_parser import parse_log_line
from app.analyzers.log_filter import group_logs
from app.analyzers.service_analyzer import analyze_service_error
from app.analyzers.root_cause import find_root_cause

from app.rules.service_rules import get_service_rule
from app.repair.repair_engine import get_repair


def ask_confirmation():
    answer = input("Onarım uygulansın mı? [E/h]: ").strip().lower()
    return answer in ("", "e", "evet", "y")


def print_system_info(system, hardware):
    print("\n[SYSTEM]")

    for key, value in system.items():
        print(f"{key}: {value}")

    print("\n[HARDWARE]")

    for key, value in hardware.items():
        print(f"{key}: {value}")


def parse_logs(raw_logs):
    parsed_logs = []

    for raw_log in raw_logs:
        parsed = parse_log_line(raw_log)

        if parsed:
            parsed_logs.append(parsed)

    return parsed_logs


def process_group(group):
    """
    Tek bir problem grubunu analiz eder.
    """

    category = group.get("category", "unknown")
    unit = group.get("unit")

    if unit:
        diagnostics = get_service_diagnostics(unit)
    else:
        diagnostics = {
            "success": False,
            "status": "",
            "logs": "",
            "error": ""
        }

    analysis = analyze_service_error(
        group,
        diagnostics
    )

    analysis["category"] = category

    root_cause = find_root_cause(
        analysis,
        diagnostics
    )

    if root_cause["cause"] != "unknown":
        analysis["problem"] = root_cause["cause"]
        analysis["confidence"] = root_cause["confidence"]
        analysis["category"] = root_cause.get(
            "category",
            analysis.get("category", "unknown")
        )

    rule = get_service_rule(analysis)

    return analysis, root_cause, rule


def print_diagnostic(
    group,
    analysis,
    root_cause,
    rule
):
    print("\n--------------------")

    print("Category:", analysis.get("category", "unknown"))
    print("Problem:", analysis.get("problem", "unknown"))
    print("Service:", analysis.get("service"))
    print("Unit:", analysis.get("unit"))
    print("Count:", group.get("count", 1))
    print("Severity:", analysis.get("severity", "low"))
    print("Confidence:", analysis.get("confidence", 0.30))

    print("Root Cause:", root_cause["cause"])
    print("Explanation:", root_cause["explanation"])

    print("Action:", rule["action"])


def run_command(command):
    """
    Repair komutunu gerçekten çalıştırır.
    """

    try:
        result = subprocess.run(
            command,
            shell=True,
            check=False
        )

        return result.returncode

    except Exception as e:
        print(f"Komut çalıştırılırken hata oluştu: {e}")
        return -1


def handle_repair(analysis, rule):
    """
    Repair Engine sonucunu işler ve gerekli durumda
    kullanıcı onayından sonra komutu çalıştırır.
    """

    category = analysis.get("category", "unknown")
    solution_id = rule.get("action")

    # Onarım gerektirmeyen durumlar
    if solution_id in (None, "ignore"):
        print("Repair: Bu problem için onarım gerekmiyor.")
        return

    repair = get_repair(
        category,
        solution_id
    )

    if not repair["success"]:
        print("Repair Engine:", repair["error"])
        return

    solution = repair["solution"]

    print("Solution:", solution["description"])

    # Bilgi amaçlı birden fazla komut
    if "commands" in solution:

        print("Commands:")

        for command in solution["commands"]:
            print(f"  {command}")

        print(
            "Requires Confirmation:",
            "Yes"
            if solution.get("requires_confirmation")
            else "No"
        )

        return

    # Tek komut
    command = solution.get("command")

    if command:
        print("Command:", command)

    requires_confirmation = solution.get(
        "requires_confirmation",
        False
    )

    print(
        "Requires Confirmation:",
        "Yes"
        if requires_confirmation
        else "No"
    )

    # Değişiklik yapan komut
    if requires_confirmation and command:

        print("\nBu işlem sisteminizde değişiklik yapabilir.")

        if ask_confirmation():

            print("\nOnarım onaylandı.")
            print("Komut:", command)
            print("\nKomut çalıştırılıyor...\n")

            return_code = run_command(command)

            if return_code == 0:
                print("\nOnarım başarıyla tamamlandı.")
            else:
                print(
                    f"\nOnarım komutu hata koduyla tamamlandı: "
                    f"{return_code}"
                )

        else:
            print("\nOnarım iptal edildi.")

    elif command:
        print("\nBilgi amaçlı komut:", command)


def main():

    # ------------------------------------------------
    # COLLECT
    # ------------------------------------------------

    system = collect_system_info()
    hardware = collect_hardware_info()
    logs = collect_error_logs()

    print("=== Pardus Diagnostic Engine ===")

    print_system_info(
        system,
        hardware
    )

    # ------------------------------------------------
    # LOG CHECK
    # ------------------------------------------------

    if not logs["success"]:
        print(
            f"\nLog alınamadı: {logs['error']}"
        )
        return

    # ------------------------------------------------
    # PARSE
    # ------------------------------------------------

    parsed_logs = parse_logs(
        logs["logs"]
    )

    # ------------------------------------------------
    # GROUP
    # ------------------------------------------------

    groups = group_logs(
        parsed_logs
    )

    print("\n[DIAGNOSTIC]")

    # ------------------------------------------------
    # ANALYZE
    # ------------------------------------------------

    for group in groups:

        analysis, root_cause, rule = process_group(
            group
        )

        print_diagnostic(
            group,
            analysis,
            root_cause,
            rule
        )

        # ------------------------------------------------
        # REPAIR
        # ------------------------------------------------

        handle_repair(
            analysis,
            rule
        )

if __name__ == "__main__":
    main()
