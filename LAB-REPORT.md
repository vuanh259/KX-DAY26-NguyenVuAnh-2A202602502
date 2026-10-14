# Báo cáo Lab Day 26

**Sinh viên:** Nguyễn Vũ Anh — **MSSV:** 2A202602502.
**Ngày thực hiện:** 14/10/2026, giờ Việt Nam (UTC+7).

## Kết quả thực hành

| Phần | Kết quả quan sát |
|---|---|
| Function Calling | Gemini yêu cầu `get_weather` cho Hà Nội và Đà Nẵng; app thực thi hàm rồi gửi kết quả để model trả lời |
| MCP stdio | `list_tools` công bố `get_weather`; client gọi thành công Hanoi, Danang, Haiphong |
| Authentication | Token hợp lệ gọi tool được; `wrong-token` bị từ chối với HTTP 401 |
| Registry | Tìm hai weather tools, chọn `get_weather_v2` v2.0.0 rồi gọi server đúng |
| Versioning | Đọc `server://info`, biết v1 deprecated; v1 vẫn trả chuỗi, v2 trả JSON có forecast |
| Weather MCP | Handshake HTTP, khám phá ba tools và health check thành công tại cổng 8085 |
| ADK hiện tại | Gọi `get_current_weather("Hanoi")`, trả 32,9°C, cảm giác như 35,4°C, độ ẩm 47%, UV 6,9, cập nhật 11:45 ngày 14/10/2026 |
| ADK dự báo | Gọi `get_forecast` với ba ngày; trả bảng dưới đây |

| Ngày | Cao / thấp (°C) | Khả năng mưa |
|---|---|---|
| 14/10/2026 | 34,4 / 24,9 | 5% |
| 15/10/2026 | 33,8 / 24,7 | 6% |
| 16/10/2026 | 33,7 / 24,3 | 9% |

Các số liệu trên là kết quả WeatherAPI tại lần chạy, không phải dự báo cập
nhật liên tục. Hai câu hỏi ADK có sự kiện gọi tool và câu trả lời trong ảnh.

## Điều rút ra

Function Calling là khả năng model sinh tên hàm và tham số. Model không tự
chạy Python: ở bước 1, `result = get_weather(**fc.args)` trong app mới là
nơi thực thi. MCP chuẩn hóa khám phá và gọi tool ở một server riêng; bước 2
chạy được mà không cần model. Trong Lab 04, ADK lo vòng lặp gọi model/tool,
MCP server kết nối tới WeatherAPI bằng REST để lấy dữ liệu thật.

Auth nằm ở tầng HTTP, độc lập với logic thời tiết. Registry giúp chọn tool
theo capability và version. Giữ tool v1 song song với v2 và thêm tham số có
default giúp client cũ tiếp tục hoạt động.

## Các sửa đổi để chạy trên Windows

- Đọc `registry.json` bằng UTF-8.
- `run-demo.ps1` dùng interpreter `.venv` và chuyển đúng thư mục làm việc.
- `run-weather.ps1` đọc key từ `.env` gốc và chọn môi trường Lab 04 tương ứng.
- `verify_setup.py` che key, kiểm tra giao thức MCP và `health_check` thật.
- Cập nhật Gemini SDK trong lockfile client; Gemini key đã được cập nhật và
  ADK chạy thành công sau khi khởi động lại.

## Bằng chứng

Đủ chín ảnh ở [screenshots/](screenshots/), được liên kết trong README.
Bảy ảnh CLI chụp trang trình duyệt hiển thị output nguyên văn của tiến trình
thật (kèm lệnh, exit code và thời điểm chạy); không phải cửa sổ terminal.
Hai ảnh ADK chụp trực tiếp giao diện chat. Output gốc đi kèm ở [evidence/](evidence/).

Cloud Run là phần tùy chọn và không triển khai.
