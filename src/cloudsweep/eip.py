import boto3

PUBLIC_IP_PRICE_PER_HOUR = 0.005
HOURS_PER_MONTH = 730


def find_unused_elastic_ips(region: str) -> list[dict]:
    """Return Elastic IPs in a region that aren't attached to anything."""
    ec2 = boto3.client("ec2", region_name=region)
    response = ec2.describe_addresses()
    findings = []

    for address in response["Addresses"]:
        if "AssociationId" in address:
            continue

        findings.append({
            "resource": "Elastic IP",
            "id": address["AllocationId"],
            "region": region,
            "details": address["PublicIp"],
            "monthly_cost": round(PUBLIC_IP_PRICE_PER_HOUR * HOURS_PER_MONTH, 2),
        })

    return findings