from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import random
import uvicorn

app = FastAPI()

# Allow CORS for local frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Dummy data generation
            data = {
                "speed": random.randint(0, 60),           # mph
                "battery": random.randint(20, 100),       # %
                "wattage": random.randint(-1200, 2000),   # W
                "range": random.randint(10, 40),          # mi
                "voltage": round(random.uniform(44, 54), 1), # V
                "speedMode": random.randint(0, 4),        # index
                "gear": random.randint(0, 3),             # index
            }
            await websocket.send_json(data)
            await asyncio.sleep(0.5)  # 2 Hz update rate
    except Exception:
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)