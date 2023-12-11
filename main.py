# main.py

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import csv
import json
import os
import asyncio
from datetime import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Constants
CSV_FILE_PATH = "data.csv"  # Đường dẫn đến tập tin CSV
UPDATE_INTERVAL = 5  # Khoảng thời gian cập nhật dữ liệu (giây)

# WebSocket manager để theo dõi các client kết nối
class WebSocketManager:
    def __init__(self):
        self.clients = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.clients.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.clients.remove(websocket)

    async def send_data_to_clients(self, data):
        for client in self.clients:
            await client.send_text(data)

manager = WebSocketManager()

# Đọc dữ liệu từ tập tin CSV và gửi cập nhật đến các client WebSocket định kỳ
async def read_csv_data_and_send_updates():
    while True:
        data = read_csv_data()  # Thực hiện logic của bạn để đọc dữ liệu từ tập tin CSV
        await manager.send_data_to_clients(json.dumps(data))
        await asyncio.sleep(UPDATE_INTERVAL)

# Hàm trợ giúp để đọc dữ liệu từ tập tin CSV (thay thế với logic của bạn)
def read_csv_data():
    data = []
    if os.path.exists(CSV_FILE_PATH):
        with open(CSV_FILE_PATH, "r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
    return data

# Định nghĩa endpoint WebSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Lắng nghe các tin nhắn từ client nếu cần
            data = await websocket.receive_text()
            print(f"Nhận tin nhắn từ client: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Định nghĩa endpoint để xử lý tải lên CSV (cho mục đích kiểm thử)
@app.post("/upload")
async def upload_csv():
    # Thực hiện logic của bạn để lưu dữ liệu từ yêu cầu vào CSV
    return {"message": "Dữ liệu CSV đã được tải lên thành công"}

# Endpoint để phục vụ trang HTML cho kiểm thử WebSocket
@app.get("/", response_class=HTMLResponse)
async def read_item():
    return templates.TemplateResponse("index.html", {"request": None})

# Chạy nhiệm vụ đọc dữ liệu CSV định kỳ và gửi cập nhật đến các client WebSocket
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(read_csv_data_and_send_updates())
