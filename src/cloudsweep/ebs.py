import boto3

EBS_PRICE_PER_GB = {
    "gp3": 0.08,
    "gp2": 0.10,
    "io2": 0.125,
    "st1": 0.045,
    "sc1": 0.015,
}


def find_unattached_volumes(region: str) -> list[dict]:
    ec2 = boto3.client("ec2", region_name=region)
    findings = []

    for volume in ec2.describe_volumes()["Volumes"]:
        if volume["State"] != "available":
            continue

        price = EBS_PRICE_PER_GB.get(volume["VolumeType"])
        if price is None:
            monthly_cost = None
        else:
            monthly_cost = round(volume["Size"] * price, 2)

        findings.append({
            "id": volume["VolumeId"],
            "type": volume["VolumeType"],
            "size_gb": volume["Size"],
            "monthly_cost": monthly_cost,
        })

    return findings