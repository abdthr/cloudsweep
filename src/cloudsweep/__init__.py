import json
import sys
from importlib.metadata import version

import boto3
import typer
from botocore.exceptions import ClientError
from rich.console import Console
from rich.table import Table

from cloudsweep.ebs import find_unattached_volumes
from cloudsweep.eip import find_unused_elastic_ips
from cloudsweep.logs import find_log_groups_without_retention
from cloudsweep.regions import get_enabled_regions

app = typer.Typer(
    help="Find forgotten AWS resources that are costing you money.",
    no_args_is_help=True,
)


def cost_for_sorting(finding: dict) -> float:
    """Unknown costs count as 0, so they end up at the bottom."""
    if finding["monthly_cost"] is None:
        return 0.0
    return finding["monthly_cost"]


def print_message(text: str) -> None:
    """Print progress and warnings to stderr, so they never mix with the results."""
    print(text, file=sys.stderr)


def print_table(findings: list[dict]) -> None:
    if not findings:
        print("No forgotten resources found.")
        return

    table = Table()
    table.add_column("Region")
    table.add_column("Resource")
    table.add_column("ID", no_wrap=True)
    table.add_column("Details")
    table.add_column("Monthly cost", justify="right")

    total = 0.0
    for f in findings:
        cost = f["monthly_cost"]
        cost_text = "unknown" if cost is None else f"${cost:.2f}"
        table.add_row(f["region"], f["resource"], f["id"], f["details"], cost_text)
        if cost is not None:
            total += cost

    Console().print(table)
    print(f"Potential savings: ${total:.2f}/month")


def show_version(value: bool) -> None:
    if value:
        print(f"cloudsweep {version('cloudsweep')}")
        raise typer.Exit()


@app.callback()
def main(
    version_flag: bool = typer.Option(
        False, "--version", callback=show_version, is_eager=True, help="Show the version and exit."
    ),
) -> None:
    pass


@app.command()
def scan(
    region: str | None = typer.Option(
        None, "--region", "-r", help="AWS region to scan. Defaults to your AWS CLI region."
    ),
    all_regions: bool = typer.Option(
        False, "--all-regions", help="Scan every region enabled for your account."
    ),
    output: str = typer.Option(
        "table", "--output", "-o", help="How to show the results: table or json."
    ),
) -> None:
    """Scan for forgotten resources and estimate what they cost per month."""
    if output not in ["table", "json"]:
        print_message(f"Unknown output format '{output}'. Use table or json.")
        raise typer.Exit(code=2)

    if region is None:
        region = boto3.Session().region_name
    if region is None:
        print_message("No region given. Use --region, or set one with: aws configure set region <region>")
        raise typer.Exit(code=2)

    if all_regions:
        regions_to_scan = get_enabled_regions(region)
    else:
        regions_to_scan = [region]

    findings = []
    skipped = []
    for r in regions_to_scan:
        print_message(f"Scanning {r}...")
        try:
            for f in find_unattached_volumes(r):
                findings.append(f)
            for f in find_unused_elastic_ips(r):
                findings.append(f)
            for f in find_log_groups_without_retention(r):
                findings.append(f)
        except ClientError as error:
            code = error.response["Error"]["Code"]
            print_message(f"  Skipped {r}: {code}")
            skipped.append(r)

    if skipped:
        print_message(f"Warning: could not scan {len(skipped)} region(s): {', '.join(skipped)}")

    findings = sorted(findings, key=cost_for_sorting, reverse=True)

    if output == "json":
        print(json.dumps(findings, indent=2))
    else:
        print_message("")
        print_table(findings)