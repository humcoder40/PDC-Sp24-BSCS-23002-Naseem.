from fastapi import FastAPI, Request, HTTPException
import asyncio
import time

app = FastAPI()

@app.middleware("http")
async def add_student_id_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Student-ID"] = "BSCS-23002"
    return response

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 2, recovery_timeout: int = 15):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"

    def get_state(self):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
        return self.state

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=15)

async def mock_llm_call():
    await asyncio.sleep(60)
    return {"message": "LLM finally responded."}

@app.get("/api/chat")
async def chat_endpoint():
    state = breaker.get_state()
    
    if state == "OPEN":
        return {
            "error": "Circuit Breaker OPEN: The LLM API is currently down.",
            "fallback": "Here is a cached/default response so the app doesn't crash."
        }

    try:
        result = await asyncio.wait_for(mock_llm_call(), timeout=2.0)
        breaker.record_success()
        return result
    except asyncio.TimeoutError:
        breaker.record_failure()
        raise HTTPException(status_code=504, detail="LLM Request Timed Out")
