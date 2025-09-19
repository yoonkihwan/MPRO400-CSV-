MPRO400 CSV 그래프 뷰어 — 최종 인수인계/요구사항 문서 (vFinal)
0) 한줄 요약

MPRO400 CSV(세미콜론 구분, 메타+측정 2단 구조)를 최대 20개까지 불러와 토크–각도 단일 모드로 중첩 비교한다. 기준 토크(각도 영점 보정), 토크/각도/시간 범위 필터, 한국어 UI/그래프, 초보자 가이드(첫 실행), 색상/라인스타일 수동 지정, **이미지 저장(PNG/JPG)**을 제공한다. 메타데이터 패널은 우측, 측정 데이터 테이블·보고서·판정·스파크라인·모드 전환은 없다.

1) 범위(Scope)
포함

CSV 로드(동시 최대 20개), 파싱·정규화, 파일별 on/off

토크–각도(Torque–Angle) 단일 모드 그래프 중첩

기준 토크(영점 보정) + 토크/각도/시간 범위 필터

색상/라인스타일 수동 지정(미지정 시 자동)

한국어 고정(메뉴·라벨·축/범례)

초보자 가이드(첫 실행 1회)

이미지 저장(PNG/JPG)

제외(명시)

모드 전환(토크–시간, 각도–시간) ❌

보고서(PDF/Excel) ❌

그래프 분석 마커/선 오버레이 ❌

합/불 판정 ❌

측정 데이터 테이블 ❌

미니 스파크라인 ❌

스무딩/샘플링 ❌

2) 데이터 사양 & 파싱 규칙
2.1 CSV 예시 (실제 샘플 기반)
Station;
Date;12.09.25
Time;08:57:47
Workpiece;
Tool;01
Application;01
Minimum Total Angle;-3340
Maximum Total Angle;133
Angle;Torque;Window ID
0,00;0,01;
1,00;0,01;
...

2.2 파싱 규칙

구분자: ;

소수점: ,(콤마) → pandas decimal=','

메타영역: 키;값 연속 → dict 수집(빈 값 허용)

데이터영역 시작: Angle;Torque;... 헤더 라인(문자열 탐지)

필수 컬럼: Angle, Torque
(있으면 사용) Time/Window ID는 선택

인코딩: utf-8 → 실패 시 cp949 재시도

오류 행: on_bad_lines='skip' (파일 크래시 방지)

3) 주요 기능 설계
3.1 그래프(단일 모드: 토크–각도)

X축: 각도(°), Y축: 토크(N·m)

다중 파일 중첩, 각 파일 별도 색상/라인 스타일

범례(파일명 기본, 사용자 라벨 입력 가능 옵션)

줌/팬/툴팁(좌표값) 기본 제공

라벨 고정(한국어): X축 “각도(°)”, Y축 “토크(N·m)”

3.2 기준 토크(각도 영점 보정)

입력: 기준 토크(N·m)

파일별로 처음 해당 토크에 도달(또는 초과)한 인덱스 idx0 탐색
angle0 = df.loc[idx0, 'Angle']
보정: Angle' = Angle - angle0

기준 토크 미입력/0 → 보정 비활성

도달 실패 파일 처리: 해당 파일 표시 제외 + 좌측 목록에 “기준 토크 미달” 툴팁/뱃지

3.3 범위 필터

토크 범위: [Tmin, Tmax] (N·m)

각도 범위: [Amin, Amax] (°) — 보정 후 각도 기준

시간 범위: [tmin, tmax] (ms/s) — CSV에 Time 있을 때만 활성

파이프라인 순서

로드/정규화 → 2) (선택) 기준토크 보정 → 3) (선택) 범위 필터 → 4) 플로팅

3.4 스타일 지정

좌측 파일목록에서 색상(ColorInput), 라인스타일(실선/점선/도트) 선택

미지정 시 자동 팔레트(최대 20개 구분)

3.5 이미지 저장

현재 플롯 PNG/JPG 저장

해상도 옵션: 1x / 2x (예: dpi=150/300)

4) UI/UX — 최종 레이아웃(캔버스 기준)

ui.md가 샘플 임 참고해서 개발할것

이미 오른쪽 캔버스의 “MPRO400 그래프 뷰어 – 최종 UI (HTML 샘플)” 상태가 기준이다.
주요 영역 배치:

상단 Topbar(QToolBar 느낌):
파일 열기 / 추가 로드 / 이미지 저장 / 그래프 그리기

컨트롤 툴바(Topbar 아래, 전폭 패널):

기준 토크 입력 + 적용 버튼

토크/각도/시간 범위 입력 + 적용/초기화

Left Dock(좌측): CSV 파일 목록

체크 on/off, 메타 요약, 색상/라인스타일 선택

Center: 그래프 뷰

한국어 라벨 고정, 범례 하단

Right Dock(오른쪽): 메타데이터 테이블

Onboarding Modal: 최초 실행 시 튜토리얼(다시 보지 않기)

PySide6에선 QMainWindow 상에서 상단 컨트롤은 중앙 위젯 상단에 QWidget+QHBoxLayout으로, 본체는 QSplitter(Left/Center/Right) 구성 추천.

5) PySide6 매핑(구현 가이드)
5.1 창/레이아웃

QMainWindow

centralWidget → QWidget(V 레이아웃)

상단 컨트롤바 QWidget(H 레이아웃)

본체 QSplitter(Qt.Horizontal)

Left: QDockWidget 대용 QFrame(파일목록)

Center: QFrame(matplotlib FigureCanvasQTAgg)

Right: QDockWidget 대용 QFrame(메타데이터 테이블)

5.2 위젯(객체명 예시)

파일 열기 버튼: btnOpen

추가 로드: btnAdd

이미지 저장: btnSave

그래프 그리기: btnDraw

기준토크 입력/적용: refTorque, btnApplyRef

범위 입력: tMin/tMax, aMin/aMax, timeMin/timeMax, btnApplyRanges, btnReset

파일목록: lstFiles(QListView 또는 커스텀 위젯; 행마다 체크박스+컬러+콤보)

메타테이블: tblMeta(QTableView)

플롯: FigureCanvasQTAgg + NavigationToolbar2QT(줌/팬)

5.3 시그널/슬롯

btnOpen.clicked → 파일 다중 선택 → 로드 → 목록 갱신 → 플롯 갱신

btnAdd.clicked → 추가 로드

btnSave.clicked → 현재 Figure 저장 대화상자 → PNG/JPG

btnDraw.clicked → 파이프라인 실행 → 플롯

btnApplyRef.clicked → 기준토크 보정 → 플롯

btnApplyRanges.clicked → 범위 필터 적용 → 플롯

btnReset.clicked → 기준토크/범위 초기화 → 플롯

파일목록 각 항목: 체크 변경/색상/라인스타일 변경 → 즉시 플롯 갱신

6) 데이터/로직 설계
6.1 데이터 모델
class FileEntry:
    path: str
    name: str
    meta: dict
    df: pd.DataFrame       # columns: Angle, Torque [, Time]
    color: str             # '#RRGGBB'
    linestyle: str         # 'solid' | 'dash' | 'dot'
    visible: bool          # 체크 on/off
    ref_ok: bool           # 기준토크 도달 여부

6.2 매니저
class DataManager:
    files: list[FileEntry]
    ref_torque: Optional[float]
    ranges: dict  # {'torque':(min,max), 'angle':(min,max), 'time':(min,max)}

6.3 파이프라인(의사코드)
def plot_all():
    selected = [f for f in files if f.visible]
    plotted = []
    for fe in selected:
        df = fe.df.copy()

        # 1) 기준토크 보정
        if ref_torque and ref_torque > 0:
            idxs = df.index[df['Torque'] >= ref_torque]
            if len(idxs) == 0:
                fe.ref_ok = False
                continue
            fe.ref_ok = True
            angle0 = df.loc[idxs[0], 'Angle']
            df['Angle'] = df['Angle'] - angle0

        # 2) 범위 필터 (존재하는 축만 적용)
        if ranges['torque']: df = df[(df['Torque']>=tmin)&(df['Torque']<=tmax)]
        if ranges['angle']:  df = df[(df['Angle']>=amin)&(df['Angle']<=amax)]
        if 'Time' in df and ranges['time']:
            df = df[(df['Time']>=tim)&(df['Time']<=tix)]

        if df.empty: continue

        # 3) 그리기
        ax.plot(df['Angle'], df['Torque'], color=fe.color, linestyle=map_style(fe.linestyle), label=fe.name)
        plotted.append(fe.name)

    ax.set_xlabel('각도(°)'); ax.set_ylabel('토크(N·m)')
    ax.legend() if plotted else ax.legend_.remove()
    canvas.draw_idle()

7) 스타일(QSS) & 폰트

다크 테마 톤은 HTML 목업의 색감에 맞춰 QSS 작성(assets/style.qss)

폰트: 시스템 폰트 기본, matplotlib는 한글 표시 위해 Noto Sans CJK 또는 시스템 한글 폰트 지정

matplotlib.rcParams['axes.unicode_minus']=False (한글 + 음수 기호 깨짐 방지)

8) 성능/안정성/배포

성능: 20파일 × 각 10k 행 기준 원활한 줌/팬
(라인 샘플링/스무딩 미사용 → 그리기 호출 최소화, 재그리기 단일축)

안정성: 잘못된 파일은 개별 실패 처리(앱 크래시 금지)

호환성: Windows 10/11

배포: PyInstaller onefile 또는 디렉토리. 버전 1회 배포(업데이트 없음)

로그: ./logs/app.log (INFO/ERROR 회전 가능)

설정: ~/.mpro400_analyzer/config.json
{"show_onboarding": true/false, "last_dir": "...", ...}

9) 예외/엣지

기준 토크 미달: 해당 파일 비표시 + 목록에 회색/툴팁 “기준 토크 미달”

Time 미존재: 시간 범위 입력칸 비활성

필터 결과 0행: 토스트/상태바 “표시할 데이터가 없습니다”

Angle/Torque 누락: 로드 실패 목록에 표시

인코딩 실패: cp949 재시도 후 실패 시 경고 다이얼로그

10) 테스트(권장 시나리오)

파싱: 다양한 샘플(utf-8/cp949, 빈 메타값, 잡음 행) → DF/메타 정상 생성

보정: ref=1.5 N·m 설정 시 각 파일 Angle=0 기준 이동/미달 파일 제외

필터: 토크/각도/시간 조합 필터 적용, 해제 시 원복

스타일: 색상/라인 변경 즉시 반영

이미지 저장: PNG/JPG 파일 생성, dpi 옵션 반영

온보딩: 첫 실행만 표시, 체크 시 재실행 숨김

11) 디렉토리 구조
mpro400_analyzer/
├─ README.md
├─ requirements.txt
├─ app/
│  ├─ main.py             # QApplication, MainWindow
│  ├─ config.py           # 설정 로드/저장
│  └─ __init__.py
├─ data/
│  ├─ csv_loader.py       # 세미콜론+decimal=',' 파서
│  ├─ data_manager.py     # 파일 목록, 파이프라인 관리
│  └─ __init__.py
├─ plots/
│  ├─ plotter.py          # FigureCanvas, draw/update
│  ├─ styles.py           # 팔레트/라인스타일 매핑
│  └─ __init__.py
├─ ui/
│  ├─ main_window.py      # 레이아웃(Topbar/Controls/Splitter)
│  ├─ file_loader_widget.py   # 파일 목록 행(체크/색/라인)
│  ├─ plot_viewer_widget.py   # 캔버스/네비게이션툴바
│  ├─ meta_viewer_widget.py   # 메타 테이블
│  ├─ range_controls_widget.py# 기준토크/범위 입력 UI
│  ├─ guide_dialog.py          # 온보딩
│  └─ __init__.py
├─ export/
│  ├─ export_image.py     # PNG/JPG 저장
│  └─ __init__.py
├─ assets/
│  ├─ icons/
│  ├─ style.qss
│  └─ guide_text.md
└─ tests/
   ├─ test_csv_loader.py
   ├─ test_pipeline.py
   └─ test_plotter.py

12) 수용 기준(Acceptance Criteria)

 20개 CSV 동시 로드, 토크–각도 중첩 정상

 기준 토크 보정: 도달 파일만 표시, 보정 각도 0 기준 일치

 범위 필터: 토크/각도/시간(있을 때만) 정상 적용/해제

 한국어 라벨/메뉴 고정, 툴팁/상태 메시지 한글

 색상/라인 스타일 수동 변경 즉시 반영

 이미지 저장 PNG/JPG 정상

 Time 미존재면 시간 필터 비활성

 오류 파일 개별 실패, 앱 크래시 없음

13) 배포 메모

requirements.txt: PySide6, pandas, matplotlib, (optional) chardet

PyInstaller:

onefile 권장: pyinstaller -F -n MPRO400_Viewer app/main.py

assets/style.qss, assets/guide_text.md는 data로 포함

실행 첫 화면에서 온보딩 표시 → “다시 보지 않기” 저장

14) 구현 체크리스트(개발 AI용)

 파서: 세미콜론, decimal=',' 처리

 헤더 탐지 후 skiprows 동적 계산

 기준토크 보정 로직 & 미달 처리

 범위 필터 파이프라인

 matplotlib 캔버스 + 한글 폰트 + unicode_minus

 파일 목록 커스텀 행(체크/색/라인)

 메타테이블 우측 도크

 온보딩 다이얼로그 + config 저장

 저장 대화상자(PNG/JPG)

 로그/에러 핸들링

참고

현재 오른쪽 캔버스의 HTML 샘플이 UI의 시각 기준이다. PySide6로 이식 시 배치는 동일, 스타일은 QSS로 근접 재현.