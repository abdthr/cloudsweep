from importlib.metadata import version

import boto3
import typer
from botocore.exceptions import ClientError

from cloudsweep.ebs import find_unattached_volumes
from cloudsweep.regions import get_enabled_regions

app = typer.Typer(
    help="Find forgotten AWS resources that are costing you money.",
    no_args_is_help=True,
)


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
) -> None:
    """Scan for forgotten resources and estimate what they cost per month."""
    if region is None:
        region = boto3.Session().region_name
    if region is None:
        print("No region given. Use --region, or set one with: aws configure set region <region>")
        raise typer.Exit(code=2)

    if all_regions:
        regions_to_scan = get_enabled_regions(region)
    else:
        regions_to_scan = [region]

    findings = []
    skipped = []
    for r in regions_to_scan:
        print(f"Scanning {r}...")
        try:
            for f in find_unattached_volumes(r):
                findings.append(f)
        except ClientError as error:
            code = error.response["Error"]["Code"]
            print(f"  Skipped {r}: {code}")
            skipped.append(r)

    if skipped:
        print(f"\nWarning: could not scan {len(skipped)} region(s): {', '.join(skipped)}")

    if not findings:
        print("\nNo unattached EBS volumes found.")
        return

    print()
    total = 0.0
    for f in findings:
        cost = f["monthly_cost"]
        cost_text = "unknown" if cost is None else f"${cost:.2f}/month"
        print(f"{f['region']}  {f['id']}  {f['type']}  {f['size_gb']} GB  {cost_text}")
        if cost is not None:
            total += cost

    print(f"\nPotential savings: ${total:.2f}/month")