# cloudsweep
[![Tests](https://github.com/abdthr/cloudsweep/actions/workflows/tests.yml/badge.svg)](https://github.com/abdthr/cloudsweep/actions/workflows/tests.yml)

Find forgotten AWS resources that are costing you money.

You delete an EC2 instance, but its disk stays behind. It's attached to nothing,
nobody remembers it exists and it shows up on your bill every month. Cloudsweep
finds that kind of leftover and tells you roughly what it's costing you.

```
$ cloudsweep scan --all-regions
...
┏━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Region     ┃ Resource   ┃ ID                         ┃ Details     ┃ Monthly cost ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ us-east-1  │ EBS volume │ vol-0a7c3f19e2b84d561      │ gp2, 500 GB │       $50.00 │
│ eu-north-1 │ EBS volume │ vol-0e01dd418b516f0ab      │ gp3, 100 GB │        $8.00 │
│ us-east-1  │ Elastic IP │ eipalloc-07d4c1e9a2b3f5a68 │ 3.91.24.17  │        $3.65 │
└────────────┴────────────┴────────────────────────────┴─────────────┴──────────────┘
Potential savings: $61.65/month
```

It can scan a single region or every region your account has enabled.

## What it finds

| Resource | Why it costs money |
|---|---|
| Unattached EBS volumes | Disks are billed per GB every month, even when nothing uses them |
| Unused Elastic IPs | AWS charges for every public IPv4 address by the hour, attached or not |
| Log groups that never expire | CloudWatch keeps logs forever by default, and you pay for every GB stored |

## How it behaves

Cloudsweep is read-only. It lists what it finds and leaves the decision to you,
because an "unused" volume might be someone's backup. If it can't price something,
it still shows it and marks the cost as `unknown` instead of hiding it.

If a region can't be scanned (for example because a policy blocks it), cloudsweep
skips it, tells you which ones it missed and carries on with the rest.

Costs are estimates based on approximate US prices, so treat them as a rough guide.

## Install

```bash
pip install cloudsweep-aws
```

You'll need AWS credentials (for example from `aws login`).

## Usage

```bash
cloudsweep scan                     # uses your default AWS region
cloudsweep scan --region us-east-1
cloudsweep scan --all-regions       # every region enabled for your account
cloudsweep scan --output json       # machine-readable, for scripts
cloudsweep --help
```

It only needs read permissions: `ec2:DescribeVolumes`, `ec2:DescribeAddresses`,
`ec2:DescribeRegions` and `logs:DescribeLogGroups`.

## Development

You'll need [uv](https://docs.astral.sh/uv/). The tests use [moto](https://github.com/getmoto/moto)
to fake AWS, so they don't need an account or cost anything.

```bash
git clone https://github.com/abdthr/cloudsweep.git
cd cloudsweep
uv run pytest
uv run cloudsweep scan
```

## License

MIT
