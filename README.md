# cloudsweep

Find forgotten AWS resources that are costing you money.

You delete an EC2 instance, but its disk stays behind. It's attached to nothing,
nobody remembers it exists and it shows up on your bill every month. Cloudsweep
finds that kind of leftover and tells you roughly what it's costing you.

```
$ cloudsweep scan --region us-east-1
vol-0e01dd418b516f0ab  gp3  100 GB  $8.00/month
vol-0a7c3f19e2b84d561  gp2  500 GB  $50.00/month

Potential savings: $58.00/month
```

For now cloudsweep only looks for unattached EBS volumes, one region
at a time.

## How it behaves

Cloudsweep is read-only. It lists what it finds and leaves the decision to you,
because an "unused" volume might be someone's backup. If it can't price something,
it still shows it and marks the cost as `unknown` instead of hiding it.

Costs are estimates based on approximate US prices, so treat them as a rough guide.

## Usage

You'll need [uv](https://docs.astral.sh/uv/) and AWS credentials (for example from `aws login`).

```bash
git clone https://github.com/abdthr/cloudsweep.git
cd cloudsweep
uv run cloudsweep scan                     # uses your default AWS region
uv run cloudsweep scan --region us-east-1
uv run cloudsweep --help
```

The only permission it needs is `ec2:DescribeVolumes`.

## Tests

The tests use [moto](https://github.com/getmoto/moto) to fake AWS, so they don't
need an account or cost anything.

```bash
uv run pytest
```

## What's next

- Scan every region in one go
- Find other things people forget about, like unused public IPs and old snapshots
- Publish it so you can `pip install cloudsweep`

## License

MIT
