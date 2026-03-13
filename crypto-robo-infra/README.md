# Crypto Robo Infrastructure

This repository holds the Terraform for the crypto robo MVP.

## Design Goals

- Lowest practical AWS cost for a personal-use trading system
- Dedicated account with separate `dev` and `prod` stacks
- Lambda-first runtime without a VPC by default
- Step Functions only for the weekly rebalance and execution path
- GitHub Actions deployment through GitHub OIDC instead of long-lived credentials

## Layout

```text
envs/
|-- dev/
`-- prod/
modules/
|-- github_oidc/
`-- platform/
```

## Bootstrap Order

1. Apply `envs/dev` with a CI-built package path or temporary S3 artifact reference.
2. Configure GitHub environment secrets and variables.
3. Push the runtime repository so CI can build and deploy the Lambda package automatically.
4. Review the Terraform outputs, CloudWatch logs, and Step Functions state machine.
5. Apply `envs/prod` when you are ready to promote.
