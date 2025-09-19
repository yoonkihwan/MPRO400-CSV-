from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)


class GuideDialog(QDialog):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("MPRO400 그래프 뷰어 시작 가이드")
        self.setModal(True)
        self.resize(520, 380)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 16)
        layout.setSpacing(12)

        layout.addWidget(QLabel("빠른 시작"))

        body = QTextBrowser()
        body.setReadOnly(True)
        body.setOpenExternalLinks(False)
        body.setHtml(
            """
            <ol style='margin:0;padding-left:20px;'>
              <li><b>파일 열기</b> 버튼으로 MPRO400 CSV 측정값을 불러오세요.</li>
              <li>필요하다면 <b>기준 토크</b>를 입력해 각도를 0°로 맞출 수 있습니다.</li>
              <li><b>토크/각도/시간 범위</b> 필터로 원하는 구간만 분석하세요.</li>
              <li>좌측 목록에서 <b>선 색상/스타일</b>을 조절해 비교 시인성을 높입니다.</li>
              <li><b>이미지 내보내기</b>로 PNG/JPG 결과를 저장할 수 있습니다.</li>
            </ol>
            """
        )
        layout.addWidget(body, stretch=1)

        self.dont_show = QCheckBox("다시 보지 않기")
        layout.addWidget(self.dont_show, alignment=Qt.AlignLeft)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def skip_requested(self) -> bool:
        return self.dont_show.isChecked()
