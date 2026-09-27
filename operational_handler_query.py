import boto3
import time
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('InventoryLedger')

def process_order_lookup():
    start_time = time.time()
    try:
        # THE STABILIZATION PATHWAY: Pointing directly to our active GSI shortcut lane
        response = table.query(
            IndexName='ClientID-Core-Index',
            KeyConditionExpression=Key('ClientID').eq('CLIENT-4013')
        )
        records = response.get('Items', [])
        duration = time.time() - start_time
        print(f"⚡ [QUERY STABILIZED] Fetched {len(records)} client nodes via ClientID-Core-Index. Execution: {duration:.4f}s")
    except Exception as e:
        print(f"[PIPELINE CRASH] Upstream Service Error: {e}")

if __name__ == '__main__':
    process_order_lookup()
