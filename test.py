import asyncio
import httpx
import time

async def make_request(client, req_id):
    print(f"Sending request {req_id}...")
    start_time = time.time()
    try:
        response = await client.get("http://127.0.0.1:8000/api/chat", timeout=10.0)
        elapsed = time.time() - start_time
        
        student_id = response.headers.get("X-Student-ID", "MISSING")
        print(f"Req {req_id} done in {elapsed:.2f}s | Status: {response.status_code} | Header: {student_id} | Body: {response.json()}")
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"Req {req_id} failed in {elapsed:.2f}s | Error: {e}")

async def main():
    async with httpx.AsyncClient() as client:
        print("--- Sending Batch 1 (Will timeout and trip breaker) ---")
        tasks_1 = [make_request(client, i) for i in range(1, 3)]
        await asyncio.gather(*tasks_1)
        
        print("\n--- Sending Batch 2 (Should fail fast with fallback) ---")
        tasks_2 = [make_request(client, i) for i in range(3, 6)]
        await asyncio.gather(*tasks_2)

if __name__ == "__main__":
    asyncio.run(main())
