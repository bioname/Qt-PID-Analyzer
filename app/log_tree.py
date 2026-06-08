from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDragLeaveEvent, QDropEvent, QFont
from PyQt6.QtWidgets import QAbstractItemView, QTreeWidget, QTreeWidgetItem

_VALID_SUFFIXES = {".BBL", ".BFL", ".bbl", ".bfl"}

_STYLE_NORMAL = """
QTreeWidget {
    background: #121b25;
    border: none;
    border-right: 1px solid #1f2c3b;
    color: #aebdcb;
    font-size: 13px;
    outline: 0;
}
QTreeWidget::item {
    padding: 4px 6px;
    border-radius: 4px;
}
QTreeWidget::item:selected {
    background: #1f3a5f;
    color: #e6edf4;
}
QTreeWidget::item:hover:!selected {
    background: #1a2e47;
    color: #c9d8e6;
}
QTreeWidget::branch:has-children:!has-siblings:closed,
QTreeWidget::branch:closed:has-children:has-siblings {
    image: url(none);
}
"""

_STYLE_DRAG_OVER = _STYLE_NORMAL.replace(
    "background: #121b25;",
    "background: #0d2035; border: 1px dashed #4d8fc4;",
)


class LogTree(QTreeWidget):
    """
    Left-panel tree widget.
    ─ Accepts .BBL / .BFL drag-and-drop.
    ─ Emits file_dropped(Path) when a valid file is dropped.
    ─ Emits session_selected(Path) when user clicks a session node.
    """

    file_dropped = pyqtSignal(Path)
    session_selected = pyqtSignal(Path)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.setColumnCount(1)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DropOnly)
        self.setIndentation(14)
        self.setAnimated(True)
        self.setStyleSheet(_STYLE_NORMAL)

        date_font = QFont()
        date_font.setBold(True)
        self._date_font = date_font

        self.itemClicked.connect(self._on_item_clicked)

    # ── Drag & drop ───────────────────────────────────────────────────

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet(_STYLE_DRAG_OVER)
        else:
            event.ignore()

    def dragMoveEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event: QDragLeaveEvent) -> None:
        self.setStyleSheet(_STYLE_NORMAL)
        super().dragLeaveEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        self.setStyleSheet(_STYLE_NORMAL)
        for url in event.mimeData().urls():
            path = Path(url.toLocalFile())
            if path.suffix in _VALID_SUFFIXES and path.is_file():
                self.file_dropped.emit(path)
                break          # one file at a time
        event.acceptProposedAction()

    # ── Tree population ───────────────────────────────────────────────

    def load_sessions(self, sessions: list[tuple[str, str, str, Path]]) -> None:
        """Populate tree from scan_sessions() result."""
        self.clear()
        date_items: dict[str, QTreeWidgetItem] = {}
        for date_str, time_str, stem, session_dir in sessions:
            date_item = self._ensure_date_item(date_str, date_items)
            self._make_session_item(date_item, time_str, stem, session_dir)

    def add_session(
        self, date_str: str, time_str: str, stem: str, session_dir: Path
    ) -> None:
        """Insert a new session at the top of its date group."""
        # Find existing date item (linear scan is fine — few dates expected)
        date_items: dict[str, QTreeWidgetItem] = {}
        for i in range(self.topLevelItemCount()):
            it = self.topLevelItem(i)
            date_items[it.text(0)] = it

        date_item = self._ensure_date_item(date_str, date_items, prepend=True)
        child = self._make_session_item(date_item, time_str, stem, session_dir)
        date_item.insertChild(0, date_item.takeChild(date_item.indexOfChild(child)))
        self.setCurrentItem(child)

    # ── Internals ─────────────────────────────────────────────────────

    def _ensure_date_item(
        self,
        date_str: str,
        cache: dict[str, QTreeWidgetItem],
        prepend: bool = False,
    ) -> QTreeWidgetItem:
        if date_str in cache:
            return cache[date_str]
        item = QTreeWidgetItem([date_str])
        item.setFont(0, self._date_font)
        item.setForeground(0, Qt.GlobalColor.white)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        item.setExpanded(True)
        if prepend:
            self.insertTopLevelItem(0, item)
        else:
            self.addTopLevelItem(item)
        cache[date_str] = item
        return item

    def _make_session_item(
        self,
        parent: QTreeWidgetItem,
        time_str: str,
        stem: str,
        session_dir: Path,
    ) -> QTreeWidgetItem:
        label = f"{time_str}   {stem}" if time_str else stem
        child = QTreeWidgetItem([label])
        child.setData(0, Qt.ItemDataRole.UserRole, session_dir)
        child.setToolTip(0, str(session_dir))
        parent.addChild(child)
        return child

    def _on_item_clicked(self, item: QTreeWidgetItem, _col: int) -> None:
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(data, Path):
            self.session_selected.emit(data)
