# SiliconSoul

Ngôn ngữ:

- 简体中文 (Mặc định): README.md
- 简体中文: README.zh-CN.md
- 繁體中文: README.zh-TW.md
- English: README.en.md
- Русский: README.ru.md
- Tiếng Việt: README.vi.md
- Français: README.fr.md
- Español: README.es.md
- Italiano: README.it.md
- 日本語: README.ja.md
- 한국어: README.ko.md
- ᠮᠠᠨᠵᡠ ᡤᡳᠰᡠᠨ (Manchu): README.mnc.md
- ᠮᠣᠩᠭᠣᠯ ᠬᠡᠯᠡ (Mongolian, traditional script): README.mn.md
- العربية: README.ar.md

> Trạng thái cập nhật (2026-04-08): PRD Phase 1 (đợt 5) bổ sung chấm điểm rủi ro chuỗi và sắp xếp đa tiêu chí (latest/risk/depth/activity) cho workspace.

## Mục đích / Giá trị / Định vị / Khác biệt

SiliconSoul là một nguyên mẫu sản phẩm hỗ trợ ra quyết định đa tác nhân (MOE) cho founder, operator, nhà đầu tư và CFO. Hệ thống kết hợp đầu vào nhiều tài liệu (PDF/Excel/PPT/Word) với suy luận song song của nhiều “chuyên gia” để tạo ra kết luận có dẫn chứng, danh sách thiếu dữ liệu có cấu trúc, và lịch sử có thể phát lại để rà soát.

### Giá trị

- Nhiều tài liệu → đầu ra tái sử dụng: kết luận + bằng chứng + cần bổ sung gì tiếp theo
- Phân tích theo tiểu ngành/tiểu sản phẩm với kiểm tra “phạm vi/khẩu kính” và phân bổ chi phí
- Quy trình có thể replay: history, replay, diff và xuất báo cáo

### Định vị sản phẩm

- Công cụ phân tích & rà soát, không phải hệ thống kế toán và không thay thế ERP/BI
- Phù hợp cho DD, review ngân sách, phân tích vận hành, phân tích theo segment, hỗ trợ nghiên cứu đầu tư

### Điểm khác biệt

- Upload hàng loạt + gắn nhãn mục đích tài liệu (tài chính / doanh thu segment / chi phí / phân bổ / KPI / hợp đồng & định giá), bằng chứng được nhóm theo mục đích
- Khi tài liệu chưa đủ, trả về needs_structured (checklist) kèm mức ưu tiên
- Main site History hỗ trợ lọc CFO + replay/diff/download
- Bảo mật nghiêm ngặt: không commit token/private key/app id; chạy kiểm tra an toàn trước khi push

Hệ thống hỗ trợ ra quyết định đa tác nhân (MOE), bao gồm:

- Backend API Python (aiohttp) + điều phối chuyên gia
- Trang chính React (Dashboard / Portfolio / KnowledgeBase / History)
- Trang CFO Streamlit (tải nhiều tài liệu, phân tích tiểu ngành/tiểu sản phẩm, xuất báo cáo)

## Bắt đầu nhanh (Docker Compose)

```bash
docker compose up -d siliconsoul siliconsoul-web siliconsoul-cfo
```

- Web (React): thường là http://localhost:3000
- API: thường là http://localhost:8000/api
- CFO (Streamlit): http://localhost:8501 (mở từ trang chính qua liên kết ngoài)

## Phát triển cục bộ

### Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest
```

### Frontend

```bash
cd frontend
npm install
npm start
```

## Cấu hình & Bảo mật

Kho mã này KHÔNG được chứa token / private key / app id. Hãy cấu hình qua biến môi trường hoặc file cấu hình cục bộ.

- Không commit: `.env*`, `data/`, `logs/`, `*.db`, `*.key`, `*.pem` (đã được ignore trong .gitignore)
- Khuyến nghị trước khi push: `./scripts/security_check.sh`
- Ví dụ cấu hình frontend: `frontend/.env.example`
- Biến môi trường thường dùng (chỉ tên, không commit giá trị):
  - `TUSHARE_TOKEN`: token Tushare
  - `SILICONSOUL_API_TOKENS`: map token xác thực backend (cho `/api/me` và truy cập bảo vệ)
  - `REACT_APP_API_URL`: base url API cho trang chính
  - `REACT_APP_CFO_URL`: url trang CFO (liên kết ngoài)
  - `CFO_API_URL`: base url API cho trang CFO

## Tài liệu

- [Kịch bản CFO](docs/cfo.md)
- [Tài liệu API](docs/api.md)
- [Hướng dẫn phát triển](docs/development.md)
