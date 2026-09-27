import boto3
import random

# Initialize the DynamoDB resource targeting your deployment region
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('InventoryLedger')

print("Initializing enterprise datastore seeding process...")
with table.batch_writer() as batch:
    for i in range(1000):
        client_id = f"CLIENT-401{random.randint(1, 5)}"
        batch.put_item(
            Item={
                'OrderID': f"ORD-2026-{i:04d}",
                'ClientID': client_id,
                'TransactionDate': f"2026-09-{random.randint(1, 26):02d}",
                'FulfillmentStatus': random.choice(['FULFILLED', 'PROCESSING', 'QUEUED']),
                'InvoiceTotal': str(round(random.uniform(150.0, 4500.0), 2))
            }
        )
print("Data seeding completed. 1,000 ledger nodes populated into 'InventoryLedger'.")
