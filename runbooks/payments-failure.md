---
id: payments-failure
title: Payments Failure Runbook
services:
  - payments-api
categories:
  - payments
severities:
  - critical
  - high
---
# Payments Failure Runbook

1. Confirm payment provider health and error rates.
2. Compare failures with the latest payments deployment.
3. Roll back the suspected change if failures began after deployment.
4. Verify successful payment volume has recovered.