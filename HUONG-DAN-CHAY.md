# Chạy các phần chưa cần WeatherAPI key trên Windows

Mở terminal PowerShell tại thư mục gốc repo. Môi trường `.venv` đã được cài.
Không cần kích hoạt virtualenv: `run-demo.ps1` dùng đúng Python trong `.venv`.

```powershell
cd E:\VinUni20K\TRACK3\DAY26\KX-DAY26-NguyenVuAnh-2A202602502
```

## Function Calling — cần Gemini key trong `.env`

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run-demo.ps1 function
```

Script đọc `GEMINI_API_KEY` từ `.env` mà không in key. Kết quả cần có
`[model yêu cầu]`, `[app thực thi]` và `Trả lời:`. Dữ liệu thời tiết là mock.
Chụp terminal thành `screenshots/01-function-calling.png`.

## MCP cơ bản — không cần key

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run-demo.ps1 mcp
```

Client tự khởi động server qua stdio. Kết quả có danh sách tool và thời tiết
Hanoi, Danang, Haiphong. Chụp thành `screenshots/02-mcp-client.png`.

## Registry và versioning — không cần key

Chạy từng lệnh rồi chụp output trước khi chạy lệnh tiếp theo:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run-demo.ps1 registry
powershell -NoProfile -ExecutionPolicy Bypass -File .\run-demo.ps1 versioning
```

Registry chọn `get_weather_v2 v2.0.0`: lưu `screenshots/03b-registry.png`.
Versioning gọi được cả v1 và v2, có `api_version: 2.0` cùng forecast:
lưu `screenshots/03c-versioning.png`.

## Authentication — cần hai terminal, không cần API key

Terminal 1, tại thư mục gốc repo:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run-demo.ps1 auth-server
```

Giữ server chạy. Terminal 2, cũng tại thư mục gốc repo:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run-demo.ps1 auth-ok
```

Kết quả có `Tools (có auth)` và `Hanoi: 29°C, trời mưa`.
Lưu ảnh `screenshots/03a-auth-ok.png`. Sau đó chạy:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run-demo.ps1 auth-fail
```

Traceback/error là kết quả mong đợi vì token sai bị từ chối.
Log server ghi HTTP 401 ở phiên bản SDK đang cài. Lưu ảnh client và log server
thành `screenshots/03a-auth-fail.png`.
Cuối cùng nhấn **Ctrl+C trong terminal 1** để giải phóng cổng 8000 cho ADK.

`ExecutionPolicy Bypass` trong các lệnh chỉ áp dụng cho tiến trình PowerShell
được mở để chạy script này, không thay đổi chính sách lưu trên máy.

## Kết quả đã kiểm tra ngày 14/10/2026

- Function Calling: Gemini yêu cầu tool cho Hà Nội và Đà Nẵng, app chạy tool,
  model tổng hợp câu trả lời thành công.
- MCP: khám phá `get_weather`, gọi thành công cho ba thành phố.
- Registry: tìm hai weather tools, chọn v2 và gọi thành công.
- Versioning: đọc metadata, gọi v1 và v2 có forecast thành công.
- Auth: token mặc định gọi tool thành công; token sai bị từ chối.

Các bước trên dùng dữ liệu mock. Output thật được lưu tại `evidence/`,
và ảnh chụp trang hiển thị output được lưu tại `screenshots/`.

## Lab 04 — WeatherAPI thật và Google ADK

Mở hai terminal tại thư mục gốc repo. Key được đọc từ `.env` ở gốc, không
cần dán key vào terminal.

Terminal 1:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run-weather.ps1 server
```

Terminal 2, kiểm tra trước rồi khởi động web:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run-weather.ps1 verify
powershell -NoProfile -ExecutionPolicy Bypass -File .\run-weather.ps1 web
```

Mở http://127.0.0.1:8000, chọn `weather_agent`, tạo New Session rồi hỏi:

- `Dùng get_current_weather cho Hanoi. Trả lời tiếng Việt với nhiệt độ,
  cảm giác như, độ ẩm, UV và thời điểm cập nhật.`
- `Dùng get_forecast cho Hanoi với days=3. Nêu từng ngày với nhiệt độ
  cao/thấp và khả năng mưa.`

Cần thấy sự kiện gọi tool và dữ liệu thật trong câu trả lời.
Nếu Gemini trả 401 thì cập nhật `GEMINI_API_KEY` và khởi động lại terminal 2.
Xong thì nhấn Ctrl+C trong cả hai terminal để dừng dịch vụ.

Khi cài lại môi trường, chạy `uv sync --python 3.12` trong từng thư mục
`04-lab/mcp-server` và `04-lab/mcp-client`. Script kiểm tra xác nhận handshake
MCP, danh sách ba tools và gọi `health_check` thay vì chỉ kiểm tra GET HTTP.
