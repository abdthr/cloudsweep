import boto3

LOG_STORAGE_PRICE_PER_GB = 0.03
BYTES_PER_GB = 1024 * 1024 * 1024


def find_log_groups_without_retention(region: str) -> list[dict]:
    """Return log groups that keep their logs forever and have data stored."""
    logs = boto3.client("logs", region_name=region)
    paginator = logs.get_paginator("describe_log_groups")
    findings = []

    for page in paginator.paginate():
        for group in page["logGroups"]:
            if "retentionInDays" in group:
                continue
            if group["storedBytes"] == 0:
                continue

            stored_gb = group["storedBytes"] / BYTES_PER_GB

            findings.append({
                "resource": "Log group",
                "id": group["logGroupName"],
                "region": region,
                "details": f"{stored_gb:.2f} GB, never expires",
                "monthly_cost": round(stored_gb * LOG_STORAGE_PRICE_PER_GB, 2),
            })

    return findings