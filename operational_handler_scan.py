import boto3
import time
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('InventoryLedger')

def process_order_lookup():
    start_time = time.time()
    try:
        # ⚠️ CRITICAL FLAW: Table-wide full table scan under parallel traffic spikes
        response = table.scan(
            FilterExpression=Attr('ClientID').eq('CLIENT-4013')
        )
        records = response.get('Items', [])
        duration = time.time() - start_time
        print(f"✔️ [FETCH SUCCESS] Retracted {len(records)} ledger line nodes. Execution: {duration:.4f}s")
    except Exception as e:
        print(f"[PIPELINE CRASH] Upstream Service Error: {e}")

if __name__ == '__main__':
    process_order_lookup()
