# How to Debug Silent DynamoDB Latency Spikes with Amazon CloudWatch Omni

This repository contains the complete replication lab and simulation engine used to investigate database latency surges and OpenTelemetry configuration gaps inside **Amazon CloudWatch Omni**.

## Architecture Overview
<img width="1280" height="720" alt="omni" src="https://github.com/user-attachments/assets/e9e42611-6f18-40a6-9fd4-055ebed35ad9" />

The testing layout simulates a high-concurrency enterprise microservice workflow executing queries against a provisioned data tier:

* **Compute Layer:** AWS CloudShell acting as the compute engine driving high parallel thread loops.
* **Datastore Tier:** Amazon DynamoDB (`InventoryLedger` table) capped at 5 RCUs to surface silent queue delays safely inside the Free Tier bounds.
* **Observability Engine:** Amazon CloudWatch Omni Space utilizing conversational AI triage routines.

## Getting Started & Replication Steps

### 1. Initialize Workspace & Deploy Datastore
Launch AWS CloudShell in your preferred AWS Region (e.g., `us-east-1`) and execute the infrastructure setup sequence:

```bash
# Clone or create directory
mkdir -p ~/internal-order-pipeline && cd ~/internal-order-pipeline

# Deploy the DynamoDB Infrastructure Table
aws dynamodb create-table \
    --table-name InventoryLedger \
    --attribute-definitions AttributeName=OrderID,AttributeType=S \
    --key-schema AttributeName=OrderID,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
```
<img width="1470" height="834" alt="Screenshot 2026-09-26 at 12 48 04 PM" src="https://github.com/user-attachments/assets/46ebcdf1-03da-4bdc-a81c-411a8dfb561f" />

### 2. Seed Data & Trigger the Anomaly Workload
Run the seeder module to populate the table with 1,000 corporate ledger lines:
```bash
python3 datastore_seeder.py
```

Now, unleash the destructive parallel load simulator script to force full table scans across the restricted 5 RCU limit:
```bash
python3 traffic_load_simulator.py
```
<img width="2940" height="1214" alt="image" src="https://github.com/user-attachments/assets/d96f871b-6940-490a-88e5-bd6566860944" />

*Observe your terminal performance metrics bloat from single-digit milliseconds up to 1.4-second queue delays as `boto3` retries engage behind the scenes.*

### 3. Triage inside CloudWatch Omni
1. Access your account's newly configured **CloudWatch Omni Space**.
2. Issue the natural language question to the chat console panel:
   > *"Show me a list of all metrics and anomalies for the InventoryLedger table over the last 15 minutes. Identify why requests are experiencing latency degradation up to 1.4 seconds."*
3. Observe how Omni returns an empty data matrix ("Complete Signal Coverage — All Empty"), isolating the core lesson: **Amazon CloudWatch Omni requires explicit OpenTelemetry (OTel) metrics streaming or ADOT collectors to map serverless code paths.**

### 4. Deploy the Performance Mitigation Fix
Attach an optimized shortcut pathway lane (GSI) to your live infrastructure table:
```bash
aws dynamodb update-table \
    --table-name InventoryLedger \
    --attribute-definitions AttributeName=ClientID,AttributeType=S \
    --global-secondary-index-updates \
    "[{\"Create\": {\"IndexName\": \"ClientID-Core-Index\", \"KeySchema\": [{\"AttributeName\": \"ClientID\", \"KeyType\": \"HASH\"}], \"Projection\": {\"ProjectionType\": \"ALL\"}, \"ProvisionedThroughput\": {\"ReadCapacityUnits\": 5, \"WriteCapacityUnits\": 5}}}]"
```
<img width="1470" height="835" alt="Screenshot 2026-09-26 at 1 19 03 PM" src="https://github.com/user-attachments/assets/17fa6a30-5f30-46b2-baf3-909c517dce51" />

Verify index state via `aws dynamodb describe-table --table-name InventoryLedger --query "Table.GlobalSecondaryIndexes[*].IndexStatus"`. Once it returns `["ACTIVE"]`, run the optimized workflow:
```bash
python3 traffic_load_simulator.py optimized
```
<img width="1470" height="835" alt="Screenshot 2026-09-26 at 1 25 21 PM" src="https://github.com/user-attachments/assets/42161775-4b21-4d7e-9ea0-d01a1a992866" />

---

## What is CloudWatch Omni

<img width="1470" height="837" alt="Screenshot 2026-09-26 at 1 03 32 PM" src="https://github.com/user-attachments/assets/ea5c7549-40c0-47eb-9757-440a984a0120" />

Amazon CloudWatch Omni is an AI-powered, collaborative observability environment built directly on open telemetry standards.Unlike the legacy AWS CloudWatch console—which relies on engineers manually constructing separate dashboards, running complex log insight queries, and manually mapping cross-resource relationships—Omni acts as an automated, conversational DevOps co-pilot.

## What It Does
It eliminates the friction of writing manual queries. You can query your logs, infrastructure traces, application metrics, and AI agent token runaways simultaneously by simply asking questions in plain English.

## How We Used 
It in This LabIn our replication workspace, we launched a dedicated CloudWatch Omni Space named OrderPipelineAnalytics and linked it directly to our account's us-east-1 dataset integration engine.Instead of opening traditional graph filters, we used Omni's conversational prompt bar as our primary incident response room. We intentionally threw a massive parallel traffic surge at our code to see if the Omni AI agent could intercept the resulting database throttling logs, diagnose the hidden database scanning bottleneck, and write out a remediation path autonomously using raw conversational queries.

<img width="1470" height="542" alt="Screenshot 2026-09-26 at 1 15 56 PM" src="https://github.com/user-attachments/assets/19eefe95-c21d-4723-8458-431347ff8276" />

<img width="1470" height="837" alt="Screenshot 2026-09-26 at 1 16 17 PM" src="https://github.com/user-attachments/assets/d1165e75-76bb-42ab-97db-ce743271a09a" />


## Resource Teardown Clean-up
To prevent ongoing charges, remove the deployed assets cleanly:
```bash
aws dynamodb delete-table --table-name InventoryLedger
```


