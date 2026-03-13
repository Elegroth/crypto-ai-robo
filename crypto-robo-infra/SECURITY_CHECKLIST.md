# Security Checklist

- Use a dedicated AWS account for this platform.
- Require GitHub OIDC for deployments; do not store long-lived AWS keys in CI.
- Keep exchange API keys in Secrets Manager and scope IAM access to read-only where possible.
- Start with `LIVE_TRADING=false` in `dev` and verify paper flows before promoting.
- Alert on Lambda errors, Step Functions failures, and repeated blocked rebalances.
- Review CloudWatch logs and DynamoDB audit entries after each deploy and each weekly run.
- Rotate exchange credentials on a schedule and after any suspected exposure.
- Keep stablecoins and fiat as quote assets only unless a cash-management rule is explicitly reviewed.
- Require manual GitHub environment approval for `prod` promotion.
