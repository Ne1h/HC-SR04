# main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import csv
import json
import os
import asyncio
from datetime import datetime


class Upload(BaseModel):
    distance: float
    timestamp: int


app = FastAPI()


# Constants
CSV_FILE_PATH = "/app/data/data.csv"  # Đường dẫn đến tập tin CSV
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

# Hàm trợ giúp để đọc dữ liệu từ tập tin CSV


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


@app.put("/upload")
async def upload_csv(upload: Upload):
    print(f"{upload.distance} at {upload.timestamp}")
    # Kiểm tra xem file đã tồn tại hay không
    if not os.path.isfile(CSV_FILE_PATH):
        # Nếu file không tồn tại, tạo file mới và ghi dữ liệu vào nó
        with open(CSV_FILE_PATH, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["distance", "timestamp"])
            writer.writerow([upload.distance, upload.timestamp])
    else:
        # Nếu file đã tồn tại, chèn dữ liệu mới vào cuối file
        with open(CSV_FILE_PATH, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([upload.distance, upload.timestamp])
    return {"status": "ok"}


@app.get("/download")
async def download_csv():
    content = ""
    with open(CSV_FILE_PATH, "r") as file:
        content = file.read().replace('\r', '')
    return Response(content=content, media_type="text/csv")

# Chạy nhiệm vụ đọc dữ liệu CSV định kỳ và gửi cập nhật đến các client WebSocket


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(read_csv_data_and_send_updates())
