---
id: database-incident
title: Database Incident Runbook
services:
  - orders-api
categories:
  - database
severities:
  - critical
  - high
---
# Database Incident Runbook

1. Check database availability and connection saturation.
2. Review slow queries and recent schema changes.
3. Roll back the suspected database change if safe.
4. Verify application database errors have recovered.
