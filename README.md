# 주소록 정리 v1.3.0

한국 휴대폰 번호(010) 정리 및 비교 전문 데스크톱 애플리케이션

![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 목차
1. [프로그램 개요](#프로그램-개요)
2. [주요 기능](#주요-기능)
3. [다운로드 및 설치](#다운로드-및-설치)
4. [사용 방법](#사용-방법)
5. [프로그램 구조](#프로그램-구조)
6. [핵심 로직 설명](#핵심-로직-설명)
7. [개발 환경 설정](#개발-환경-설정)
8. [빌드 방법](#빌드-방법)
9. [기술 스택](#기술-스택)
10. [라이선스](#라이선스)

---

## 프로그램 개요

**주소록 정리**는 CSV/Excel 파일에서 한국 휴대폰 번호(010)를 자동으로 추출하고, 정규화하며, 중복 제거 및 대조 작업을 수행하는 데스크톱 애플리케이션입니다.

### 개발 배경
- 다양한 형식의 전화번호 데이터를 통일된 형식(`010-XXXX-XXXX`)으로 변환
- 여러 주소록 파일을 비교하여 중복 연락처 찾기
- 대조 결과를 시각적으로 표시(O/X/△ 마커)
- 대조된 파일들을 병합하여 최종 주소록 생성

### 주요 특징
- **자동 컬럼 감지**: 이름/전화번호 컬럼을 자동으로 찾아냄
- **다양한 형식 지원**: CSV, Excel(.xlsx, .xls) 파일 처리
- **지능형 정규화**: 국제번호(+82), 공백, 하이픈 등 다양한 형식 자동 변환
- **GUI 기반**: 직관적인 3탭 구조(정리/대조/병합)
- **실시간 로그**: 모든 처리 과정을 UI 로그창에 실시간 표시
- **결과 파일 자동 스타일링**: Excel 출력 시 색상, 테두리, 헤더 자동 적용

---

## 주요 기능

### 1. 정리 (Clean)
여러 주소록 파일에서 유효한 010 번호를 추출하고 중복 제거

**처리 과정:**
```
입력 파일(들) → 컬럼 자동 감지 → 전화번호 정규화 → 중복 제거 → Excel 출력
```

**출력:**
- `{원본파일명}_변환결과_{타임스탬프}.xlsx`
- 컬럼: 연번, 이름, 휴대폰번호, 추천1~4, 검증, 파일명

**예시:**
```
입력: 홍길동_주소록.csv (이름, 전화번호 컬럼 포함)
      - 010 1234 5678
      - +82-10-1234-5678
      - 01012345678
      
출력: 홍길동_주소록_변환결과_260122-0930.xlsx
      - 모두 010-1234-5678 형식으로 통일
      - 중복 번호는 1개만 남김
```

### 2. 대조 (Compare)
두 주소록 세트를 비교하여 매칭 여부를 O/X/△로 표시

**처리 과정:**
```
비교 주소록(들) + 대조 대상(들) → 전화번호 기준 매칭 → O/X/△ 마킹 → Excel 출력
```

**마커 의미:**
- **O**: 전화번호가 양쪽 모두 존재 (이름 유사)
- **X**: 대조 대상에만 존재 (비교 주소록에 없음)
- **△**: 전화번호만 일치하지만 이름이 다름 / 유효하지 않은 번호

**출력:**
- `주소록_{비교파일명}_대조결과_{타임스탬프}.xlsx`
- `주소록_{대조파일명}_대조결과_{타임스탬프}.xlsx`

**예시:**
```
비교 주소록: 홍길동_주소록.xlsx (100개 연락처)
대조 대상: 김아무개_주소록.xlsx (100개 연락처, 30% 중복)

출력:
- 주소록_홍길동_대조결과.xlsx → 홍길동 관점에서 본 결과
- 주소록_김아무개_대조결과.xlsx → 김아무개 관점에서 본 결과
  - O 마크: 30개 (중복 연락처)
  - X 마크: 70개 (김아무개만 가진 연락처)
```

### 3. 병합 (Merge)
여러 대조결과 파일(`주소록_*_대조결과.xlsx`)을 하나로 병합

**처리 과정:**
```
대조결과 파일들 → 휴대폰번호 기준 중복 제거 → 정렬 → Excel 출력
```

**출력:**
- `병합결과_{타임스탬프}.xlsx`
- 휴대폰번호 기준으로 중복 제거 (동일 번호는 1개만 유지)

**예시:**
```
입력:
- 주소록_홍길동_대조결과.xlsx (150개)
- 주소록_김아무개_대조결과.xlsx (120개)
- 주소록_박철수_대조결과.xlsx (90개)

출력: 병합결과_260122-0945.xlsx
      - 총 360개 중 중복 제거 후 240개 최종 연락처
```

---

## 다운로드 및 설치

### 일반 사용자 (비개발자)

1. [GitHub Releases](https://github.com/stevenahhh/contact-cleaner/releases) 페이지로 이동
2. 최신 버전의 `주소록정리_v1.3.0.exe` 다운로드
3. 다운로드한 `.exe` 파일을 더블클릭하여 실행
4. **별도 설치 불필요** - 단일 실행 파일로 바로 사용 가능

### 시스템 요구사항
- **OS**: Windows 10/11 (64비트)
- **용량**: 약 15MB
- **권한**: 관리자 권한 불필요

---

## 사용 방법

### 1. 정리 탭 사용하기

1. 프로그램 실행 후 **"정리"** 탭 선택
2. **"파일 추가"** 버튼 클릭
3. 정리할 CSV/Excel 파일 선택 (여러 파일 선택 가능)
4. 파일 목록에서 불필요한 파일은 **"선택 파일 제거"**로 삭제
5. **"정리 시작"** 버튼 클릭
6. 처리 완료 후 로그창에 출력 파일 경로 표시 (클릭 시 폴더 열림)

### 2. 대조 탭 사용하기

1. **"대조"** 탭 선택
2. **"비교 주소록"** 섹션에 기준이 되는 파일 추가
3. **"대조 대상"** 섹션에 비교할 파일 추가
4. **"대조 시작"** 버튼 클릭
5. 두 개의 대조결과 파일이 생성됨

### 3. 병합 탭 사용하기

1. **"병합"** 탭 선택
2. **"파일 추가"** 버튼 클릭
3. `주소록_*_대조결과.xlsx` 형식의 파일들 선택
4. **"병합 시작"** 버튼 클릭
5. 최종 병합결과 파일 생성

### 출력 파일 위치
모든 결과 파일은 프로그램 실행 파일과 같은 폴더의 `작업결과/` 디렉토리에 저장됩니다.

---

## 프로그램 구조

```
contact_cleaner/
├── core/                   # 핵심 비즈니스 로직
│   ├── processor.py        # 파일 처리 메인 로직
│   ├── detector.py         # 컬럼 자동 감지
│   ├── normalizer.py       # 전화번호 정규화
│   └── comparator.py       # 대조 로직
├── gui/                    # 사용자 인터페이스
│   ├── app.py              # 메인 애플리케이션 (3탭 구조)
│   ├── widgets.py          # 커스텀 위젯 (파일 리스트, 로그, 진행바)
│   └── theme.py            # sv_ttk 테마 설정
├── utils/                  # 유틸리티
│   └── file_utils.py       # Excel 저장, 스타일링
└── main.py                 # 프로그램 진입점
```

### 주요 모듈 설명

#### `core/processor.py` - ContactProcessor
- **역할**: 파일 읽기 → 컬럼 감지 → 정규화 → 결과 생성
- **핵심 메서드**:
  - `process()`: 파일 전체 처리 파이프라인
  - `_find_all_valid_phones_in_row()`: 행의 모든 컬럼에서 유효한 010 번호 추출
  - `_read_excel_rows()` / `_read_csv_rows()`: 파일 타입별 읽기

#### `core/detector.py` - ColumnDetector
- **역할**: 이름/전화번호 컬럼을 자동으로 찾기
- **감지 방법**:
  1. 패턴 매칭: `이름`, `성명`, `전화번호`, `연락처` 등
  2. 샘플 데이터 분석: 실제 값에서 010 번호 개수 세기
  3. 정규식 매칭: `010-XXXX-XXXX` 패턴 찾기

#### `core/normalizer.py` - normalize_phone_number()
- **역할**: 다양한 형식의 전화번호를 `010-XXXX-XXXX`로 변환
- **처리 규칙**:
  - 국제번호 변환: `+82-10-1234-5678` → `010-1234-5678`
  - 공백/하이픈 제거: `010 1234 5678` → `010-1234-5678`
  - 앞자리 복원: `10-1234-5678` → `010-1234-5678`
  - 유효성 검사: 11자리 숫자, 010으로 시작
- **필터링**:
  - 지역번호(02, 031 등) 제외
  - 인터넷전화(070) 제외
  - 서비스번호(1588, 080 등) 제외
  - 구형 이동전화(011, 016 등) 제외

#### `utils/file_utils.py`
- **save_styled_excel()**: Excel 파일에 스타일 적용
  - 헤더: 회색 배경, 가운데 정렬, 테두리
  - 검증 컬럼: 노란색 배경
  - 폰트: Malgun Gothic
  - 컬럼 너비 자동 조정

---

## 핵심 로직 설명

### 1. 전화번호 정규화 흐름

```
입력: "010 1234 5678"
  ↓
공백/하이픈 제거: "01012345678"
  ↓
국제번호 처리: +82 → 0 추가
  ↓
앞자리 복원: 10... → 010...
  ↓
유효성 검증:
  - 010으로 시작?
  - 11자리 숫자?
  - 지역번호/서비스번호 아님?
  ↓
포맷팅: "010-1234-5678"
```

### 2. 대조 로직 (Compare)

```python
# 비교 주소록과 대조 대상의 전화번호를 비교
for 대조_대상_연락처 in 대조_대상:
    전화번호 = 대조_대상_연락처["휴대폰번호"]
    
    if 전화번호 in 비교_주소록:
        이름_유사 = 이름_비교(대조_대상_연락처["이름"], 비교_주소록[전화번호]["이름"])
        
        if 이름_유사:
            마크 = "O"  # 전화번호 + 이름 모두 일치
        else:
            마크 = "△"  # 전화번호만 일치 (이름 다름)
    else:
        마크 = "X"  # 비교 주소록에 없음
```

### 3. 병합 로직 (Merge)

```python
# 여러 대조결과 파일에서 중복 제거
연락처_딕셔너리 = {}

for 파일 in 대조결과_파일들:
    for 행 in 파일.read():
        전화번호 = 행["휴대폰번호"]
        
        # 휴대폰번호를 키로 사용 → 중복 자동 제거
        if 전화번호 not in 연락처_딕셔너리:
            연락처_딕셔너리[전화번호] = 행
        else:
            # 이미 존재하면 이름 우선순위로 선택
            기존_이름 = 연락처_딕셔너리[전화번호]["이름"]
            새_이름 = 행["이름"]
            
            if len(새_이름) > len(기존_이름):
                연락처_딕셔너리[전화번호] = 행

# 최종 리스트로 변환
최종_연락처 = list(연락처_딕셔너리.values())
```

---

## 개발 환경 설정

### 요구사항
- **Python**: 3.12 이상
- **패키지 관리자**: conda (권장) 또는 pip

### 설치 단계

#### 1. 저장소 클론
```bash
git clone https://github.com/stevenahhh/contact-cleaner.git
cd contact-cleaner
```

#### 2. Conda 환경 생성 (권장)
```bash
conda create -n contact_cleaner python=3.12 -y
conda activate contact_cleaner
```

#### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

**requirements.txt 내용:**
```
openpyxl>=3.1.0
sv-ttk>=2.6.0
darkdetect>=0.8.0
pyinstaller>=6.0.0
```

#### 4. 개발 모드 실행
```bash
python contact_cleaner/main.py
```

---

## 빌드 방법

### PyInstaller로 단일 실행 파일 생성

```bash
# Git Bash (Windows)
cd /c/Users/User/Desktop/ws
source ~/miniconda3/etc/profile.d/conda.sh
conda activate contact_cleaner

# PyInstaller 빌드
pyinstaller --onefile \
  --windowed \
  --name "주소록정리_v1.3.0" \
  --add-data "contact_cleaner;contact_cleaner" \
  --hidden-import openpyxl \
  contact_cleaner/main.py \
  --noconfirm
```

### 빌드 옵션 설명
- `--onefile`: 단일 .exe 파일로 패키징
- `--windowed`: 콘솔 창 숨김 (GUI만 표시)
- `--name`: 출력 파일명 지정
- `--add-data`: 런타임에 필요한 파일/폴더 포함
- `--hidden-import`: 동적 import로 인해 자동 감지 안 되는 모듈 명시
- `--noconfirm`: 기존 빌드 결과 자동 덮어쓰기

### 출력
- **빌드 폴더**: `build/주소록정리_v1.3.0/`
- **실행 파일**: `dist/주소록정리_v1.3.0.exe` (약 13MB)

---

## 기술 스택

### 언어
- **Python 3.12**: 메인 개발 언어

### GUI
- **tkinter**: 내장 GUI 프레임워크
- **sv-ttk**: Sun Valley 테마 적용 (모던한 외관)
- **darkdetect**: 시스템 다크모드 자동 감지

### 데이터 처리
- **openpyxl**: Excel 파일(.xlsx) 읽기/쓰기
- **csv** (내장): CSV 파일 처리

### 배포
- **PyInstaller**: Python 코드를 단일 .exe로 패키징

### 주요 의존성 없는 라이브러리
- **pathlib**: 파일 경로 처리
- **re**: 정규식 (전화번호 패턴 매칭)
- **collections.Counter**: 컬럼 감지 시 통계
- **typing**: 타입 힌팅 (코드 가독성 향상)

---

## 파일 형식 예시

### 입력 파일 예시 (CSV)
```csv
이름,전화번호,이메일
홍길동,010-1234-5678,hong@example.com
김철수,+82-10-2345-6789,kim@example.com
이영희,010 3456 7890,lee@example.com
박영수,01045678901,park@example.com
```

### 정리 결과 파일 (Excel)
| 연번 | 이름 (휴대폰에 저장될 이름) | 휴대폰번호 | 추천1(DW) | 추천2 | 추천3(비교대상과체크) | 추천4 | 휴대폰 저장파일명 |
|------|----------------------------|------------|-----------|-------|----------------------|-------|-------------------|
| 1    | 홍길동                     | 010-1234-5678 |           |       |                      |       |                   |
| 2    | 김철수                     | 010-2345-6789 |           |       |                      |       |                   |
| 3    | 이영희                     | 010-3456-7890 |           |       |                      |       |                   |
| 4    | 박영수                     | 010-4567-8901 |           |       |                      |       |                   |

### 대조 결과 파일 (Excel)
같은 형식이지만 **추천3(비교대상과체크)** 컬럼에 O/X/△ 마커 추가
- **O**: 비교 주소록에 존재
- **X**: 비교 주소록에 없음
- **△**: 번호만 일치

---

## 개발 과정 (Development Journey)

### v1.0.0 - 초기 버전
- CSV 파일 처리 기본 기능 구현
- 단순 정리 기능만 제공

### v1.1.0 - 대조 기능 추가
- 두 파일 비교 기능 구현
- O/X/△ 마커 시스템 도입

### v1.2.0 - Excel 지원
- openpyxl 통합
- Excel 파일 읽기/쓰기 지원
- 스타일링 기능 추가

### v1.3.0 - 병합 기능 및 UI 개선 (현재)
- 병합 탭 추가 (여러 대조결과 합치기)
- 창 크기 1150x950 고정 (DPI 스케일링 1.25x)
- 로그창 클릭 가능한 파일 경로
- sv-ttk 테마 적용
- 테스트 데이터 생성 스크립트 추가
- PyInstaller 6.18.0으로 빌드

### 개발 시 고려사항
1. **인코딩 문제**: CSV 파일의 다양한 인코딩(utf-8, cp949, euc-kr) 자동 감지
2. **DPI 스케일링**: Windows 고해상도 디스플레이 지원 (1.25x 배율)
3. **비동기 처리**: GUI가 멈추지 않도록 파일 처리는 별도 스레드에서 실행
4. **에러 핸들링**: 잘못된 파일 형식, 빈 파일, 헤더 없는 파일 등 예외 처리
5. **UI/UX**: 실시간 진행 상태 표시, 클릭 가능한 로그, 색상 코딩

---

## 트러블슈팅

### Q1: 프로그램이 실행되지 않아요
**A**: Windows Defender나 백신 소프트웨어에서 차단될 수 있습니다. 예외 목록에 추가해주세요.

### Q2: 컬럼을 잘못 인식해요
**A**: 파일의 첫 행에 `이름`, `전화번호` 같은 명확한 헤더가 있는지 확인하세요. 없다면 수동으로 추가 후 실행하세요.

### Q3: 전화번호가 변환되지 않아요
**A**: 010으로 시작하는 11자리 숫자만 유효합니다. 지역번호(02, 031 등)나 서비스번호(1588 등)는 자동 제외됩니다.

### Q4: 병합 시 중복이 남아있어요
**A**: 병합은 **휴대폰번호**를 기준으로 중복 제거합니다. 이름은 중복 제거 기준이 아닙니다.

### Q5: Excel 파일이 깨져 보여요
**A**: Excel 2016 이상 버전을 사용하세요. 또는 LibreOffice Calc에서 열어보세요.

---

## 기여 방법

1. 이 저장소를 Fork하세요
2. 새 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 Push (`git push origin feature/amazing-feature`)
5. Pull Request 생성

---

## 라이선스

MIT License

Copyright (c) 2026 stevenahhh

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 연락처

프로젝트 링크: [https://github.com/stevenahhh/contact-cleaner](https://github.com/stevenahhh/contact-cleaner)

버그 리포트 및 기능 제안: [Issues](https://github.com/stevenahhh/contact-cleaner/issues)
