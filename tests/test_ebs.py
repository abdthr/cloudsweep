import boto3
import pytest
from moto import mock_aws

from cloudsweep.ebs import find_unattached_volumes

REGION = "eu-north-1"
ZONE = "eu-north-1a"


@pytest.fixture
def ec2():
    """A fake EC2 service. Nothing here touches real AWS."""
    with mock_aws():
        yield boto3.client("ec2", region_name=REGION)


def test_no_volumes_means_no_findings(ec2):
    assert find_unattached_volumes(REGION) == []


def test_finds_unattached_volume_with_cost(ec2):
    volume = ec2.create_volume(AvailabilityZone=ZONE, Size=100, VolumeType="gp3")

    findings = find_unattached_volumes(REGION)

    assert findings == [
        {"id": volume["VolumeId"], "type": "gp3", "size_gb": 100, "monthly_cost": 8.0}
    ]


def test_ignores_attached_volumes(ec2):
    image_id = ec2.describe_images()["Images"][0]["ImageId"]
    instance = ec2.run_instances(ImageId=image_id, MinCount=1, MaxCount=1)["Instances"][0]
    volume = ec2.create_volume(AvailabilityZone=instance["Placement"]["AvailabilityZone"], Size=10)
    ec2.attach_volume(VolumeId=volume["VolumeId"], InstanceId=instance["InstanceId"], Device="/dev/sdf")

    found_ids = [f["id"] for f in find_unattached_volumes(REGION)]

    assert volume["VolumeId"] not in found_ids


def test_unknown_volume_type_is_reported_with_unknown_cost(ec2):
    ec2.create_volume(AvailabilityZone=ZONE, Size=10, VolumeType="standard")

    findings = find_unattached_volumes(REGION)

    assert len(findings) == 1
    assert findings[0]["monthly_cost"] is None


def test_finds_every_volume_in_a_large_account(ec2):
    for _ in range(250):
        ec2.create_volume(AvailabilityZone=ZONE, Size=1)

    assert len(find_unattached_volumes(REGION)) == 250