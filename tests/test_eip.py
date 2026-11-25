import boto3
import pytest
from moto import mock_aws

from cloudsweep.eip import find_unused_elastic_ips

REGION = "eu-north-1"


@pytest.fixture
def ec2():
    """A fake EC2 service. Nothing here touches real AWS."""
    with mock_aws():
        yield boto3.client("ec2", region_name=REGION)


def test_finds_unused_elastic_ip_with_cost(ec2):
    address = ec2.allocate_address(Domain="vpc")

    findings = find_unused_elastic_ips(REGION)

    assert findings == [
        {
            "resource": "Elastic IP",
            "id": address["AllocationId"],
            "region": REGION,
            "details": address["PublicIp"],
            "monthly_cost": 3.65,
        }
    ]


def test_ignores_elastic_ip_attached_to_a_server(ec2):
    image_id = ec2.describe_images()["Images"][0]["ImageId"]
    instance = ec2.run_instances(ImageId=image_id, MinCount=1, MaxCount=1)["Instances"][0]
    address = ec2.allocate_address(Domain="vpc")
    ec2.associate_address(AllocationId=address["AllocationId"], InstanceId=instance["InstanceId"])

    assert find_unused_elastic_ips(REGION) == []