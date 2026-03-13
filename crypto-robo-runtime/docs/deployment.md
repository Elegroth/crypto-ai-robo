# Runtime Deployment Notes

## Build Output

The runtime CI installs the package, runs linting and tests, and is intended to publish a Lambda package artifact to S3 in a later build step.

## Environment Expectations

- `develop` deploys automatically to `dev`
- `prod` is promoted manually through the `promote-prod` workflow
- One active exchange is configured per environment through `ACTIVE_EXCHANGE`
- Research overlays are bounded by `AI_RISK_MIN`, `AI_RISK_MAX`, and `AI_DEFAULT_MULTIPLIER`

## Operational Checks

- Confirm the DynamoDB table and S3 report bucket names match the Terraform outputs.
- Confirm the Step Functions state machine exists and the weekly EventBridge rule targets it.
- Confirm preview-only behavior in `dev` before enabling live execution in `prod`.
