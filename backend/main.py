from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import uvicorn
from contextlib import asynccontextmanager
from couch import Couch
from typing import Optional

class UIManager:
    websocket: Optional[WebSocket] = None

    async def send(self, data: dict):
        if not self.websocket:
            print("No websocket connection")
            return
        await self.websocket.send_json(data)

@asynccontextmanager
async def lifespan(app: FastAPI):
    ui_manager = UIManager()
    app.state.ui_manager = ui_manager
    couch = Couch(ui_manager)
    couch.start()
    yield
    couch.stop()

app = FastAPI(lifespan=lifespan)

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
        app.state.ui_manager.websocket = websocket
        while True:
            await asyncio.sleep(1)
    except Exception as e:
        print(f"Error accepting websocket: {e}")
        app.state.ui_manager.websocket = None
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)