# cloudsweep

Find forgotten AWS resources that are costing you money.

You delete an EC2 instance, but its disk stays behind. It's attached to nothing,
nobody remembers it exists and it shows up on your bill every month. Cloudsweep
finds that kind of leftover and tells you roughly what it's costing you.

```
$ cloudsweep scan --all-regions
...
eu-north-1  vol-0e01dd418b516f0ab  gp3  100 GB  $8.00/month
us-east-1   vol-0a7c3f19e2b84d561  gp2  500 GB  $50.00/month

Potential savings: $58.00/month
```

For now cloudsweep only looks for unattached EBS volumes. It can scan a single
region or every region your account has enabled.

## How it behaves

Cloudsweep is read-only. It lists what it finds and leaves the decision to you,
because an "unused" volume might be someone's backup. If it can't price something,
it still shows it and marks the cost as `unknown` instead of hiding it.

If a region can't be scanned (for example because a policy blocks it), cloudsweep
skips it, tells you which ones it missed and carries on with the rest.

Costs are estimates based on approximate US prices, so treat them as a rough guide.

## Usage

You'll need [uv](https://docs.astral.sh/uv/) and AWS credentials (for example from `aws login`).

```bash
git clone https://github.com/abdthr/cloudsweep.git
cd cloudsweep
uv run cloudsweep scan                     # uses your default AWS region
uv run cloudsweep scan --region us-east-1
uv run cloudsweep scan --all-regions       # every region enabled for your account
uv run cloudsweep --help
```

It only needs two read permissions: `ec2:DescribeVolumes` and `ec2:DescribeRegions`.

## Tests

The tests use [moto](https://github.com/getmoto/moto) to fake AWS, so they don't
need an account or cost anything.

```bash
uv run pytest
```

## What's next

- Find other things people forget about, like unused public IPs and old snapshots
- Publish it so you can `pip install cloudsweep`

## License

MIT
