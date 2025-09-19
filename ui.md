<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>MPRO400 그래프 뷰어 – 최종 UI 샘플</title>
  <style>
    :root{
      --bg:#0f1115; --panel:#151a23; --panel2:#0f1420; --line:#222b3a; --text:#e9eef6; --muted:#9aa6b2; --accent:#4aa8ff;
      --radius:14px; --shadow:0 10px 30px rgba(0,0,0,.35);
    }
    *{box-sizing:border-box}
    html,body{height:100%}
    body{margin:0; background:var(--bg); color:var(--text); font:14px/1.45 system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial}

    /* Topbar */
    .topbar{position:sticky; top:0; z-index:50; height:56px; display:flex; align-items:center; gap:12px; padding:0 16px; background:linear-gradient(180deg,#111522,#0f1115); border-bottom:1px solid var(--line)}
    .logo{font-weight:700; letter-spacing:.2px}
    .menu{display:flex; gap:8px}
    .btn{height:32px; padding:0 12px; border-radius:10px; background:#121828; color:var(--text); border:1px solid #20283a; cursor:pointer}
    .btn:hover{background:#172134}
    .btn.primary{background:linear-gradient(180deg,#2a69ff,#1987ff); border:none}

    /* Layout: 좌측 파일목록, 가운데 그래프, 우측 메타데이터 */
    .wrap{height:calc(100% - 56px); display:grid; grid-template-columns: 300px 1fr 280px; grid-template-rows: auto 1fr; gap:12px; padding:12px}
    .panel{background:var(--panel); border:1px solid var(--line); border-radius:var(--radius); box-shadow:var(--shadow)}

    /* Toolbar */
    .toolbar{grid-column: 1 / span 3; display:flex; align-items:center; flex-wrap:wrap; gap:16px; padding:10px 12px}
    .field{display:flex; align-items:center; gap:8px}
    .field input[type="number"], .field input[type="text"]{width:84px; height:30px; padding:0 8px; border-radius:10px; border:1px solid #243048; background:#0f1523; color:var(--text)}
    .field .unit{color:var(--muted); font-size:12px}
    .divider{height:28px; width:1px; background:var(--line)}

    /* Left list */
    .left{display:flex; flex-direction:column; overflow:hidden}
    .left header{padding:12px 12px 8px; border-bottom:1px solid var(--line); display:flex; justify-content:space-between; align-items:center}
    .left .list{padding:8px; overflow:auto}
    .file{display:grid; grid-template-columns: 20px 1fr; gap:10px; padding:10px; border-radius:12px; border:1px solid transparent}
    .file:hover{background:var(--panel2); border-color:#1f2737}
    .file input{accent-color:var(--accent)}
    .meta{font-size:12px; color:var(--muted)}
    .row{display:flex; gap:8px; margin-top:6px}
    select{height:30px; border-radius:10px; border:1px solid #243048; background:#0f1523; color:var(--text); padding:0 8px}
    .color{height:30px; width:44px; border-radius:10px; border:1px solid #243048; background:#0f1523}

    /* Plot */
    .plot{display:flex; flex-direction:column; overflow:hidden}
    .plot .canvas{flex:1; margin:12px; border-radius:12px; border:1px dashed #2a3550; background:repeating-linear-gradient(45deg,#0f1523,#0f1523 10px,#121a2d 10px,#121a2d 20px); display:grid; place-items:center; color:#a9b2c2}
    .legend{margin:0 12px 12px; padding:8px 10px; background:#0f1523; border:1px solid #223049; border-radius:12px; font-size:12px}
    .chip{display:flex; align-items:center; gap:8px; margin:4px 0}
    .sw{width:10px; height:10px; border-radius:999px; background:#4aa8ff}

    /* Meta table (오른쪽) */
    .meta-panel{display:flex; flex-direction:column; overflow:auto}
    .meta-panel header{padding:10px 12px; border-bottom:1px solid var(--line)}
    table{width:100%; border-collapse:collapse; font-size:13px}
    th,td{padding:8px 10px; border-bottom:1px solid #22304a}
    th{background:#10182a; position:sticky; top:0}

    /* Guide modal */
    .modal{position:fixed; inset:0; background:rgba(0,0,0,.55); display:none; place-items:center}
    .modal.active{display:grid}
    .guide{width:640px; max-width:92vw; background:#121827; border:1px solid #243048; border-radius:16px; box-shadow:0 30px 80px rgba(0,0,0,.45)}
    .guide header{padding:16px; border-bottom:1px solid #243048; font-weight:600}
    .guide .body{padding:16px; color:#cbd5e1}
    .guide .body ol{margin:0; padding-left:20px}
    .guide footer{display:flex; justify-content:space-between; align-items:center; padding:12px 16px; border-top:1px solid #243048}
    .checkbox{display:flex; align-items:center; gap:8px; color:#a8b3c2}
  </style>
</head>
<body>
  <div class="topbar">
    <div class="logo">MPRO400 그래프 뷰어</div>
    <div class="menu">
      <button class="btn" id="btnOpen">파일 열기</button>
      <button class="btn" id="btnAdd">추가 로드</button>
      <button class="btn" id="btnSave">이미지 저장</button>
      <button class="btn primary" id="btnDraw">그래프 그리기</button>
    </div>
  </div>

  <div class="wrap">
    <!-- Toolbar: reference torque + ranges -->
    <section class="panel toolbar" aria-label="컨트롤">
      <div class="field">
        <label for="refTorque">기준 토크</label>
        <input id="refTorque" type="number" placeholder="예: 1.5" step="0.01" />
        <span class="unit">N·m</span>
        <button class="btn" id="btnApplyRef">적용</button>
      </div>
      <div class="divider"></div>
      <div class="field">
        <label>토크 범위</label>
        <input id="tMin" type="number" placeholder="최소" step="0.01" />
        ~
        <input id="tMax" type="number" placeholder="최대" step="0.01" />
        <span class="unit">N·m</span>
      </div>
      <div class="field">
        <label>각도 범위</label>
        <input id="aMin" type="number" placeholder="최소" step="0.1" />
        ~
        <input id="aMax" type="number" placeholder="최대" step="0.1" />
        <span class="unit">°</span>
      </div>
      <div class="field" title="CSV에 시간 데이터가 없으면 비활성화">
        <label>시간 범위</label>
        <input id="timeMin" type="number" placeholder="최소" step="1" disabled />
        ~
        <input id="timeMax" type="number" placeholder="최대" step="1" disabled />
        <span class="unit">ms</span>
      </div>
      <button class="btn" id="btnApplyRanges">범위 적용</button>
      <button class="btn" id="btnReset">초기화</button>
    </section>

    <!-- Left: file list -->
    <aside class="panel left" aria-label="파일 목록">
      <header>
        <strong>CSV 파일 목록</strong>
        <button class="btn" id="btnClear">모두 해제</button>
      </header>
      <div class="list" id="fileList">
        <div class="file" role="listitem">
          <input type="checkbox" checked />
          <div>
            <div>01010072.csv</div>
            <div class="meta">날짜 12.09.25 • 툴 01 • 앱 01</div>
            <div class="row">
              <input class="color" type="color" value="#4aa8ff" title="색상" />
              <select title="라인 스타일">
                <option value="solid">실선</option>
                <option value="dash">점선</option>
                <option value="dot">도트</option>
              </select>
            </div>
          </div>
        </div>
        <div class="file" role="listitem">
          <input type="checkbox" checked />
          <div>
            <div>01010073.csv</div>
            <div class="meta">날짜 12.09.25 • 툴 01 • 앱 01</div>
            <div class="row">
              <input class="color" type="color" value="#7bd87b" title="색상" />
              <select title="라인 스타일">
                <option value="solid">실선</option>
                <option value="dash">점선</option>
                <option value="dot">도트</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </aside>

    <!-- Plot (center) -->
    <main class="panel plot" aria-label="그래프">
      <div class="canvas" id="canvas">
        <div>여기에 <b>토크–각도</b> 한국어 그래프가 표시됩니다</div>
      </div>
      <div class="legend" id="legend">
        <div class="chip"><span class="sw" style="background:#4aa8ff"></span>01010072.csv</div>
        <div class="chip"><span class="sw" style="background:#7bd87b"></span>01010073.csv</div>
      </div>
    </main>

    <!-- Meta table (오른쪽) -->
    <section class="panel meta-panel" aria-label="메타데이터">
      <header><strong>메타데이터</strong></header>
      <div style="overflow:auto">
        <table>
          <thead><tr><th>키</th><th>값</th></tr></thead>
          <tbody>
            <tr><td>날짜</td><td>12.09.25</td></tr>
            <tr><td>시간</td><td>08:57:47</td></tr>
            <tr><td>툴</td><td>01</td></tr>
            <tr><td>어플리케이션</td><td>01</td></tr>
            <tr><td>최소 총 각도</td><td>-3340</td></tr>
            <tr><td>최대 총 각도</td><td>133</td></tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>

  <!-- Onboarding Modal -->
  <div class="modal active" id="guide">
    <div class="guide" role="dialog" aria-modal="true">
      <header>처음 오셨나요? – 빠른 시작 가이드</header>
      <div class="body">
        <ol>
          <li><b>파일 열기</b> 버튼으로 MPRO400 CSV를 불러오세요.</li>
          <li>필요하면 <b>기준 토크</b>를 입력해 각도 0° 기준을 맞추세요.</li>
          <li><b>토크/각도/시간 범위</b>를 입력해 원하는 구간만 보세요.</li>
          <li>좌측 목록에서 <b>색상/라인 스타일</b>을 바꿔 가독성을 높이세요.</li>
          <li><b>이미지 저장</b> 버튼으로 결과를 PNG/JPG로 저장하세요.</li>
        </ol>
      </div>
      <footer>
        <label class="checkbox"><input type="checkbox" id="dontShow" /> 다시 보지 않기</label>
        <div>
          <button class="btn" id="closeGuide">닫기</button>
        </div>
      </footer>
    </div>
  </div>

  <script>
    const guide = document.getElementById('guide');
    document.getElementById('closeGuide').onclick = () => { guide.classList.remove('active'); };
  </script>
</body>
</html>
