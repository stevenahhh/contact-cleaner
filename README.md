# 주소록 정리 v1.2.0

한국 휴대폰 번호(010) 정리 및 비교 도구

## 기능

- **주소록 정리**: CSV/Excel 파일에서 010 번호 추출 및 정규화 (`010-XXXX-XXXX`)
- **데이터 대조**: 두 파일을 비교하여 매칭 결과 분류
  - **O**: 이름 유사 + 번호 일치
  - **△**: 번호만 일치 (이름 다름)
  - **X**: 매칭 없음

## 다운로드

[Releases](https://github.com/YOUR_USERNAME/contact_cleaner/releases)에서 최신 실행 파일 다운로드

## 개발 환경 설정

### 요구사항
- Python 3.12+
- conda (권장)

### 설치

```bash
# conda 환경 생성
conda create -n contact_cleaner python=3.12 -y
conda activate contact_cleaner

# 의존성 설치
pip install -r requirements.txt
```

### 실행

```bash
python contact_cleaner/main.py
```

### 빌드

```bash
pyinstaller --onefile --windowed --name "주소록정리_v1.2.0" \
  --add-data "contact_cleaner;contact_cleaner" \
  --hidden-import openpyxl \
  contact_cleaner/main.py
```

실행 파일: `dist/주소록정리_v1.2.0.exe`

## 프로젝트 구조

```
contact_cleaner/
├── core/           # 핵심 로직 (전화번호 정규화, 컬럼 탐지)
├── gui/            # GUI (tkinter)
├── utils/          # 유틸리티 (파일 입출력, Excel 스타일링)
└── main.py         # 진입점
```

## 라이선스

MIT

