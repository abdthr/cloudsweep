import boto3


def get_enabled_regions(region: str) -> list[str]:
    """Return the names of all regions enabled for this AWS account."""
    ec2 = boto3.client("ec2", region_name=region)
    response = ec2.describe_regions()

    regions = []
    for r in response["Regions"]:
        regions.append(r["RegionName"])

    return regions