# MPRO400 CSV 그래프 뷰어

MPRO400 시스템에서 생성된 세미콜론(`;`) 기반 CSV 데이터를 불러와 싱글/멀티 플롯을 생성하고, 특정 플롯 데이터 및 통계 데이터를, PNG/JPG 이미지 익스포트 기능을 제공하는 데스크톱 애플리케이션입니다. UI는 PySide6 기반이며, 최대 20개의 데이터 파일을 동시에 플로팅 할 수 있습니다.

## 주요 기능
- 최대 20개 CSV 파일 로드 및 그래프 활성/비활성, 삭제, 색 스타일 변경
- 특정 플롯 데이터 및 통계 데이터 표시
- 싱글/멀티/시간 동기 플로팅 (시간 동기화는 데이터에 따라 자동 비활성)
- 메타데이터 뷰, 그래프 확대/이동 인터랙션, PNG/JPG 익스포트 (150/300dpi)
- 다크/라이트 테마 다이얼로그 및 사용자 설정 (`~/.mpro400_analyzer/config.json`) 저장

## 설치 및 실행
1. 의존성 설치:
   ```bash
   pip install -r requirements.txt
   ```
2. 애플리케이션 실행:
   ```bash
   python -m app.main
   ```

### PyInstaller 패키징
실행 파일 생성 시 아래를 이용합니다.
```bash
pyinstaller -F -n MPRO400_Viewer app/main.py
```
실행 후 `assets/style.qss` 및 `assets/guide_text.md` (필요 시)을 dist에 복사하세요.

## 테스트
PySide6, pandas, matplotlib 이 설치되어 있다면 테스트를 실행할 수 있습니다.
```bash
pytest
```

## 로그 & 설정
- 애플리케이션 로그: `./logs/app.log`
- 사용자 설정: `~/.mpro400_analyzer/config.json`

## 프로젝트 구조
```
mpro400_analyzer/
  app/                # 엔트리포인트 및 메인 로직
  data/               # CSV 로더, 데이터 매니저
  plots/              # Matplotlib 기반 플로팅 처리
  ui/                 # PySide6 기반 UI 위젯
  export/             # 이미지 익스포트 유틸리티
  assets/             # QSS 스타일, 가이드 등 자산
  tests/              # 단위 테스트 + 샘플 CSV
```