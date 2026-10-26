from importlib.metadata import version

import boto3
import typer

from cloudsweep.ebs import find_unattached_volumes

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
) -> None:
    """Scan for forgotten resources and estimate what they cost per month."""
    if region is None:
        region = boto3.Session().region_name
    if region is None:
        print("No region given. Use --region, or set one with: aws configure set region <region>")
        raise typer.Exit(code=2)

    findings = find_unattached_volumes(region)

    if not findings:
        print(f"No unattached EBS volumes found in {region}.")
        return

    total = 0.0
    for f in findings:
        cost = f["monthly_cost"]
        cost_text = "unknown" if cost is None else f"${cost:.2f}/month"
        print(f"{f['id']}  {f['type']}  {f['size_gb']} GB  {cost_text}")
        if cost is not None:
            total += cost

    print(f"\nPotential savings: ${total:.2f}/month")