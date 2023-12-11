# Dockerfile

# Sử dụng hình ảnh cơ sở với Python và FastAPI
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# Đặt thư mục làm việc
WORKDIR /app

# Sao chép mã nguồn vào thư mục làm việc
COPY . /app

# Cài đặt các phụ thuộc từ requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port cho FastAPI
EXPOSE 80

# Lệnh để chạy máy chủ FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
