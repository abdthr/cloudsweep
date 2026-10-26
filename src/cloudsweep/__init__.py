import sys
from importlib.metadata import version

from cloudsweep.ebs import find_unattached_volumes

REGION = "eu-north-1"


def main() -> None:
    if "--version" in sys.argv:
        v = version("cloudsweep")
        print(f"cloudsweep {v}")
        return

    findings = find_unattached_volumes(REGION)

    if not findings:
        print(f"No unattached EBS volumes found in {REGION}.")
        return

    total = 0.0
    for f in findings:
        cost = f["monthly_cost"]
        cost_text = "unknown" if cost is None else f"${cost:.2f}/month"
        print(f"{f['id']}  {f['type']}  {f['size_gb']} GB  {cost_text}")
        if cost is not None:
            total += cost

    print(f"\nPotential savings: ${total:.2f}/month")