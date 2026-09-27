import concurrent.futures
import operational_handler_scan
import operational_handler_query
import sys

def execute_concurrent_workload(target_module):
    # Force-pools 60 simultaneous parallel workers to overwhelm provisioned capacity
    with concurrent.futures.ThreadPoolExecutor(max_workers=60) as executor:
        if target_module == "legacy":
            jobs = [executor.submit(operational_handler_scan.process_order_lookup) for _ in range(80)]
        else:
            jobs = [executor.submit(operational_handler_query.process_order_lookup) for _ in range(80)]
        
        # Gather execution threads to observe standard performance output loops
        for future in concurrent.futures.as_completed(jobs):
            try:
                future.result()
            except Exception as error:
                print(f"[INFRASTRUCTURE BREAK] Multi-tenant thread failed: {error}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "optimized":
        print("Driving production load over optimized Global Secondary Indices...")
        execute_concurrent_workload("optimized")
    else:
        print("⚠️ Unleashing destructive parallel scans over legacy unindexed routes...")
        execute_concurrent_workload("legacy")
