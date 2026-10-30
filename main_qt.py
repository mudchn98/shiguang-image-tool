# -*- coding: utf-8 -*-
import sys, os
import logging
from datetime import datetime

def _data_dir():
    """exe 所在目录（打包后）/ 源码目录（开发时），用于存放版本标记等运行期文件"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


APP_VERSION = "5.2"


LOG_DIR = os.path.join(os.path.expanduser("~"), "拾光日志")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"拾光_{datetime.now().strftime('%Y%m%d')}.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8")]
)
log = logging.getLogger("拾光")
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QListWidgetItem,
    QFileDialog, QFrame, QStatusBar, QSizePolicy, QStackedWidget,
    QMenu, QMessageBox, QInputDialog, QSlider, QSpinBox, QGridLayout,
    QScrollArea, QButtonGroup, QRadioButton, QCheckBox, QLineEdit,
    QProgressBar, QGroupBox, QDialog, QComboBox, QAbstractSpinBox
)
from PySide6.QtCore import Qt, QSize, QPoint, QRect
from PySide6.QtGui import (
    QIcon, QPixmap, QAction, QImage, QPainter, QPen, QColor, QBrush,
    QLinearGradient, QRadialGradient, QPalette, QPainterPath, QPolygonF, QFont
)
from PySide6.QtCore import Qt, QSize, QPoint, QRect, QPointF, QRectF, QEasingCurve, QPropertyAnimation, QTimer
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QGraphicsBlurEffect, QFrame
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
import io
import math

def _app_icon_path():
    """在 exe 目录、_MEIPASS、源码目录里依次查找 icon.ico，避免换目录启动时图标丢失"""
    cands = []
    if getattr(sys, "_MEIPASS", None):
        cands.append(sys._MEIPASS)
    try:
        cands.append(os.path.dirname(os.path.abspath(sys.executable)))
    except Exception:
        pass
    cands.append(os.path.dirname(os.path.abspath(__file__)))
    for d in cands:
        p = os.path.join(d, "icon.ico")
        if os.path.exists(p):
            return p
    return "icon.ico"


# ═══════════════════════════════════════════════════════════
# 玻璃背景组件 — 绘制大椭圆渐变光晕
# ═══════════════════════════════════════════════════════════
class GlassBackground(QWidget):
    """背景 + 多层径向渐变光晕（大椭圆）+ 圆角，支持深色/浅色主题"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(False)
        self._theme = "dark"
        self._flat_color = None   # 实验皮肤：纯色背景（关闭光晕），None=沿用玻璃渐变
        self._orbs_dark = [
            {"x": 0.15, "y": 0.20, "rx": 380, "ry": 280, "color": QColor(111, 111, 255, 50)},
            {"x": 0.85, "y": 0.75, "rx": 320, "ry": 240, "color": QColor(39, 210, 191, 35)},
            {"x": 0.50, "y": 0.50, "rx": 500, "ry": 350, "color": QColor(75, 63, 227, 25)},
            {"x": 0.75, "y": 0.15, "rx": 250, "ry": 200, "color": QColor(138, 43, 226, 30)},
        ]
        self._orbs_light = [
            {"x": 0.15, "y": 0.20, "rx": 380, "ry": 280, "color": QColor(111, 111, 255, 28)},
            {"x": 0.85, "y": 0.75, "rx": 320, "ry": 240, "color": QColor(39, 210, 191, 22)},
            {"x": 0.50, "y": 0.50, "rx": 500, "ry": 350, "color": QColor(75, 63, 227, 15)},
            {"x": 0.75, "y": 0.15, "rx": 250, "ry": 200, "color": QColor(138, 43, 226, 18)},
        ]

    def set_theme(self, theme):
        self._theme = theme
        self._flat_color = None
        self.update()

    def set_flat(self, color_hex):
        """实验皮肤：纯色平涂背景，关闭玻璃光晕；传 None 恢复玻璃"""
        self._flat_color = color_hex
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        w = self.width()
        h = self.height()
        r = 12.0

        # 纯色平涂（实验皮肤）：直接填充后只描圆角边框，不画光晕
        if self._flat_color:
            painter.fillRect(self.rect(), QColor(self._flat_color))
            clip_path = QPainterPath()
            clip_path.addRoundedRect(QRectF(0, 0, w, h), r, r)
            painter.setClipPath(clip_path)
            painter.setPen(QPen(QColor(0, 0, 0, 18), 1))
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(clip_path)
            painter.end()
            return

        if self._theme == "dark":
            base_grad = QLinearGradient(0, 0, 0, h)
            base_grad.setColorAt(0, QColor("#08081a"))
            base_grad.setColorAt(0.5, QColor("#0c0c24"))
            base_grad.setColorAt(1, QColor("#0a0a1e"))
            painter.fillRect(self.rect(), base_grad)
            orbs = self._orbs_dark
            border_color = QColor(255, 255, 255, 20)
        else:
            base_grad = QLinearGradient(0, 0, 0, h)
            base_grad.setColorAt(0, QColor("#f4f5fa"))
            base_grad.setColorAt(0.5, QColor("#eceef5"))
            base_grad.setColorAt(1, QColor("#f0f1f6"))
            painter.fillRect(self.rect(), base_grad)
            orbs = self._orbs_light
            border_color = QColor(0, 0, 0, 30)

        clip_path = QPainterPath()
        clip_path.addRoundedRect(QRectF(0, 0, w, h), r, r)
        painter.setClipPath(clip_path)

        painter.setPen(Qt.NoPen)
        for orb in orbs:
            cx = int(w * orb["x"])
            cy = int(h * orb["y"])
            rx = orb["rx"]
            ry = orb["ry"]
            color = orb["color"]

            for i in range(6):
                scale = 1.0 - i * 0.12
                alpha = int(color.alpha() * (0.15 + i * 0.15))
                if alpha > 255:
                    alpha = 255
                grad = QRadialGradient(QPointF(cx, cy), max(rx, ry) * scale)
                grad.setColorAt(0, QColor(color.red(), color.green(), color.blue(), alpha))
                grad.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 0))
                painter.setBrush(QBrush(grad))
                painter.drawEllipse(QPointF(cx, cy), rx * scale, ry * scale)

        painter.setPen(QPen(border_color, 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(clip_path)

        painter.end()


# ═══════════════════════════════════════════════════════════
# 玻璃面板 — 带模糊背景和阴影的 Frame
# ═══════════════════════════════════════════════════════════
class GlassPanel(QFrame):
    """半透明玻璃面板，带内边框光晕"""
    def __init__(self, parent=None, blur_radius=0, opacity=0.06):
        super().__init__(parent)
        self._blur_radius = blur_radius
        self._opacity = opacity
        self.setObjectName("GlassPanel")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        w = self.width()
        h = self.height()
        radius = 12.0

        # 玻璃面 — 半透明白色
        glass_color = QColor(255, 255, 255, int(self._opacity * 255))
        path = QPainterPath()
        path.addRoundedRect(QRectF(1, 1, w - 2, h - 2), radius, radius)
        painter.fillPath(path, glass_color)

        # 内边框高光（顶部更亮）
        border_grad = QLinearGradient(0, 0, 0, h)
        border_grad.setColorAt(0, QColor(255, 255, 255, 40))
        border_grad.setColorAt(0.5, QColor(255, 255, 255, 15))
        border_grad.setColorAt(1, QColor(255, 255, 255, 5))
        painter.setPen(QPen(QBrush(border_grad), 1))
        painter.drawPath(path)

        painter.end()


# ═══════════════════════════════════════════════════════════
# 动画按钮 — hover 时平滑过渡
# ═══════════════════════════════════════════════════════════
class AnimatedButton(QPushButton):
    """hover 时图形效果平滑过渡"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._shadow = QGraphicsDropShadowEffect()
        self._shadow.setBlurRadius(0)
        self._shadow.setColor(QColor(111, 111, 255, 0))
        self._shadow.setOffset(0, 2)
        self.setGraphicsEffect(self._shadow)
        self._anim = None
        self.setCursor(Qt.PointingHandCursor)

    def enterEvent(self, event):
        super().enterEvent(event)
        self._animate_shadow(12, QColor(111, 111, 255, 60))

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._animate_shadow(0, QColor(111, 111, 255, 0))

    def _animate_shadow(self, target_blur, target_color):
        if self._anim:
            self._anim.stop()
        self._anim = QPropertyAnimation(self._shadow, b"blurRadius")
        self._anim.setDuration(200)
        self._anim.setStartValue(self._shadow.blurRadius())
        self._anim.setEndValue(target_blur)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._shadow.setColor(target_color)
        self._anim.start()


# ═══════════════════════════════════════════════════════════
# 主题颜色常量 — 内联样式使用这些值
# ═══════════════════════════════════════════════════════════
THEME_COLORS = {
    "dark": {
        "text_primary": "rgba(255,255,255,0.9)",
        "text_secondary": "rgba(255,255,255,0.55)",
        "text_hint": "rgba(255,255,255,0.35)",
        "glass_bg": "rgba(255,255,255,0.03)",
        "glass_border": "rgba(255,255,255,0.06)",
        "glass_btn": "rgba(255,255,255,0.04)",
        "glass_btn_border": "rgba(255,255,255,0.06)",
        "menu_bg": "rgba(20,20,40,0.85)",
        "log_bg": "rgba(255,255,255,0.03)",
        "log_border": "rgba(255,255,255,0.08)",
        "accent": "#8B8BFF",
    },
    "light": {
        "text_primary": "rgba(0,0,0,0.8)",
        "text_secondary": "rgba(0,0,0,0.5)",
        "text_hint": "rgba(0,0,0,0.3)",
        "glass_bg": "rgba(255,255,255,0.5)",
        "glass_border": "rgba(0,0,0,0.06)",
        "glass_btn": "rgba(255,255,255,0.6)",
        "glass_btn_border": "rgba(0,0,0,0.06)",
        "menu_bg": "rgba(255,255,255,0.92)",
        "log_bg": "rgba(255,255,255,0.5)",
        "log_border": "rgba(0,0,0,0.06)",
        "accent": "#5B5BFF",
    },
}

def tc(key):
    """获取当前主题颜色值"""
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance()
    theme = getattr(app, "_current_theme", "dark") if app else "dark"
    return THEME_COLORS.get(theme, THEME_COLORS["dark"]).get(key, "")


# ═══════════════════════════════════════════════════════════
# 实验皮肤注册表（临时对比用，非正式改版）
# base: glass-dark / glass-light 走既有玻璃QSS；其余用 override 覆盖
# ═══════════════════════════════════════════════════════════
SKINS = {
    "glass-dark": {"label": "玻璃 · 深（当前）", "base": "dark"},
    "glass-light": {"label": "玻璃 · 浅", "base": "light"},
    "apple": {
        "label": "Apple HIG", "base": "light",
        "bg": "#F5F5F7", "surface": "#FFFFFF", "sidebar": "#F5F5F7",
        "text": "#1D1D1F", "sub": "#515154", "accent": "#0071E3",
        "accent_soft": "rgba(0,113,227,0.10)", "border": "rgba(0,0,0,0.09)",
        "secondary_bg": "#FFFFFF", "card_r": "12px", "btn_r": "9px",
        "primary_hover": "#0077ED", "primary_press": "#0066CC",
    },
    "material": {
        "label": "Material 3", "base": "light",
        "bg": "#F3EDF7", "surface": "#FFFFFF", "sidebar": "#F3EDF7",
        "text": "#1C1B1F", "sub": "#38363A", "accent": "#6750A4",
        "accent_soft": "rgba(103,80,164,0.14)", "border": "rgba(103,80,164,0.22)",
        "secondary_bg": "#EADDFF", "card_r": "16px", "btn_r": "20px",
        "primary_hover": "#7966B8", "primary_press": "#5A4699",
    },
    "fluent": {
        "label": "Windows Fluent", "base": "light",
        "bg": "#FAFAFA", "surface": "#FFFFFF", "sidebar": "#FFFFFF",
        "text": "#1B1B1B", "sub": "#4D4D4D", "accent": "#0078D4",
        "accent_soft": "rgba(0,120,212,0.12)", "border": "#E5E5E5",
        "secondary_bg": "#F2F2F2", "card_r": "6px", "btn_r": "6px",
        "primary_hover": "#106EBE", "primary_press": "#005A9E",
    },
}


def build_skin_override(skin):
    """实验皮肤：在 light 基础QSS之上追加覆盖样式。glass 皮肤返回空串。"""
    s = SKINS.get(skin)
    if not s or skin.startswith("glass"):
        return ""
    p = s
    r, br = p["card_r"], p["btn_r"]
    return f"""
QMainWindow {{ background: {p['bg']}; }}
QStackedWidget, QScrollArea > QWidget > QWidget {{ background: transparent; }}

/* 侧边栏 */
#SideBar {{ background: {p['sidebar']}; border-right: 1px solid {p['border']}; }}
#SideBtn {{
    text-align: left; padding: 9px 14px; border-radius: {br};
    background: transparent; color: {p['text']}; font-size: 14px; font-weight: 500;
    margin: 2px 10px; border: 1px solid transparent;
}}
#SideBtn:hover {{ background: rgba(128,128,128,0.08); color: {p['text']}; }}
#SideBtn:checked {{
    background: {p['accent_soft']}; color: {p['accent']}; font-weight: 600;
    border: 1px solid transparent;
}}

/* 按钮 */
#TopBtn {{
    background: {p['secondary_bg']}; border: 1px solid {p['border']};
    border-radius: {br}; padding: 8px 18px; color: {p['text']};
    font-size: 13px; font-weight: 500;
}}
#TopBtn:hover {{ background: {p['accent_soft']}; }}
#TopBtn:pressed {{ background: {p['accent_soft']}; }}
#TopBtnPrimary {{
    background-color: {p['accent']}; border: 1px solid transparent;
    border-radius: {br}; padding: 8px 22px; color: #FFFFFF;
    font-weight: 600; font-size: 13px;
}}
#TopBtnPrimary:hover {{ background-color: {p['primary_hover']}; }}
#TopBtnPrimary:pressed {{ background-color: {p['primary_press']}; }}

/* 面板 / 卡片 / 预览 / 分组 */
#GlassPanel, #FileList, #Preview, QGroupBox {{
    background: {p['surface']}; border: 1px solid {p['border']}; border-radius: {r};
}}
#FileList {{ padding: 8px; }}
#FileList::item {{
    padding: 9px 12px; border-radius: {br}; color: {p['text']};
    font-size: 14px; border: none; margin: 2px 4px;
}}
#FileList::item:selected {{ background: {p['accent_soft']}; color: {p['accent']}; }}
#FileList::item:hover {{ background: rgba(128,128,128,0.06); }}
#Preview {{ color: {p['sub']}; }}
#CollapsibleBtn {{
    text-align: left; font-weight: 600; padding: 10px 12px;
    border: 1px solid {p['border']}; border-radius: {r};
    background: {p['surface']}; color: {p['text']}; font-size: 13px;
}}
QGroupBox {{ margin-top: 16px; padding: 14px; font-weight: 600; color: {p['text']}; }}
QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 6px; color: {p['sub']}; }}

/* 文字 */
QLabel {{ color: {p['text']}; }}
#InfoLabel {{ color: {p['sub']}; }}
#SecondaryLabel {{ color: {p['sub']}; font-size: 13px; }}
#HintLabel {{ color: {p['sub']}; font-size: 12px; }}
#SectionLabel {{ color: {p['text']}; }}

/* 输入控件 */
QLineEdit, QSpinBox, QComboBox {{
    border: 1px solid {p['border']}; border-radius: {br}; padding: 6px 12px;
    background: #FFFFFF; color: {p['text']};
}}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{ border-color: {p['accent']}; }}
QComboBox QAbstractItemView {{ background: #FFFFFF; color: {p['text']}; border: 1px solid {p['border']}; border-radius: {br}; selection-background-color: {p['accent_soft']}; }}

/* 单选 / 复选 */
QCheckBox, QRadioButton {{ color: {p['text']}; font-size: 14px; spacing: 8px; }}
QRadioButton::indicator::checked {{ border: 2px solid {p['accent']}; background: {p['accent']}; }}
QCheckBox::indicator::checked {{ border: 2px solid {p['accent']}; background: {p['accent']}; }}

/* 滑块 */
QSlider::sub-page:horizontal {{ background: {p['accent']}; }}
QSlider::handle:horizontal {{ background: #FFFFFF; border: 2px solid {p['accent']}; }}

/* 菜单 / 状态栏 */
QMenu {{ background: {p['surface']}; border: 1px solid {p['border']}; border-radius: {r}; padding: 8px; }}
QMenu::item {{ padding: 8px 24px; border-radius: {br}; color: {p['text']}; font-size: 14px; }}
QMenu::item:selected {{ background: {p['accent_soft']}; color: {p['accent']}; }}
QStatusBar {{ background: transparent; color: {p['sub']}; border-top: 1px solid {p['border']}; }}
QStatusBar QLabel {{ color: {p['sub']}; }}
"""


def build_qss(theme="dark"):
    """根据主题生成 QSS 样式表"""
    if theme == "dark":
        return QSS_DARK
    else:
        return QSS_LIGHT

QSS_DARK = """
/* ═══════════════════════════════════════════════════════
   拾光 5.1 — Glassmorphism 2.0 Dark Theme
   深色基底 + 玻璃面板 + 紫青色调 + 微交互
   ═══════════════════════════════════════════════════════ */

QMainWindow { background: transparent; }
QPushButton { border: 1px solid transparent; outline: none; font-family: "Microsoft YaHei UI", "PingFang SC", sans-serif; }

/* ── 自定义标题栏 ── */
#TitleBar {
    background: transparent;
    border: none;
    min-height: 40px;
    max-height: 40px;
}
#TitleLabel {
    color: rgba(255, 255, 255, 0.7);
    font-size: 14px;
    font-weight: 600;
    padding-left: 14px;
}
#WinBtn, #WinBtnClose {
    background: transparent;
    border: none;
    border-radius: 6px;
    color: rgba(255, 255, 255, 0.6);
    font-size: 14px;
    min-width: 40px;
    max-width: 40px;
    min-height: 32px;
    max-height: 32px;
}
#WinBtn:hover {
    background: rgba(255, 255, 255, 0.08);
    color: rgba(255, 255, 255, 0.9);
}
#WinBtnClose:hover {
    background: #E53935;
    color: #FFFFFF;
}

/* ── 玻璃面板通用 ── */
#GlassPanel {
    background: transparent;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
}

/* ── 可折叠面板按钮 ── */
#CollapsibleBtn {
    text-align: left;
    font-weight: 600;
    padding: 10px 12px;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.04);
    color: rgba(255, 255, 255, 0.85);
    font-size: 13px;
}

/* ── 编辑页专用 ── */
#InfoLabel { color: rgba(255, 255, 255, 0.55); }
#ColorBtn { border-radius: 10px; border: 1px solid rgba(128, 128, 128, 0.3); }
#LogText {
    font-family: "Cascadia Code", Consolas, monospace;
    font-size: 12px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    color: rgba(255, 255, 255, 0.7);
}

/* ── 通用标签 ── */
#SectionLabel { font-weight: 600; color: rgba(255, 255, 255, 0.9); }
#SecondaryLabel { color: rgba(255, 255, 255, 0.55); font-size: 13px; }
#HintLabel { color: rgba(255, 255, 255, 0.35); font-size: 12px; }
#CanvasLabel {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 10px;
}

/* ── 滚动区域 viewport 透明 ── */
QScrollArea { border: none; background: transparent; }
QScrollArea > QWidget > QWidget { background: transparent; }
#CollapsibleContent { background: transparent; border: none; }

/* ── 侧边栏：深色玻璃面板 ── */
#SideBar {
    background: rgba(255, 255, 255, 0.03);
    border-right: 1px solid rgba(255, 255, 255, 0.06);
}
#SideBtn {
    text-align: left; padding: 10px 14px; border-radius: 10px;
    background: transparent; color: rgba(255, 255, 255, 0.55);
    font-size: 14px; font-weight: 500; margin: 3px 10px;
    border: 1px solid transparent;
}
#SideBtn:hover {
    background: rgba(255, 255, 255, 0.06);
    color: rgba(255, 255, 255, 0.85);
    border-color: rgba(255, 255, 255, 0.05);
}
#SideBtn:checked {
    background: rgba(111, 111, 255, 0.12);
    color: #8B8BFF;
    font-weight: 600;
    border: 1px solid rgba(111, 111, 255, 0.2);
}

/* ── 次按钮：玻璃描边按钮 ── */
#TopBtn {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px; padding: 8px 18px;
    color: rgba(255, 255, 255, 0.85); font-size: 13px; font-weight: 500;
}
#TopBtn:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.18);
}
#TopBtn:pressed { background: rgba(255, 255, 255, 0.03); }

/* ── 主按钮：紫色填充按钮 ── */
#TopBtnPrimary {
    background-color: #6F6FFF; border: 1px solid transparent;
    border-radius: 10px; padding: 8px 22px;
    color: #FFFFFF; font-weight: 600; font-size: 13px;
}
#TopBtnPrimary:hover { background-color: #5B5BFF; }
#TopBtnPrimary:pressed { background-color: #4B4BE3; }

/* ── 文件列表：玻璃卡片 ── */
#FileList {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px; padding: 8px; outline: none;
}
#FileList::item {
    padding: 10px 12px; border-radius: 8px;
    color: rgba(255, 255, 255, 0.85); font-size: 14px;
    border: none; outline: none; margin: 2px 4px;
}
#FileList::item:selected {
    background: rgba(111, 111, 255, 0.15);
    color: #8B8BFF; border: none; outline: none;
}
#FileList::item:hover {
    background: rgba(255, 255, 255, 0.04);
    border: none; outline: none;
}

/* ── 预览区：深色画布 ── */
#Preview {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    color: rgba(255, 255, 255, 0.35); font-size: 14px;
}

/* ── 状态栏 ── */
QStatusBar {
    background: #0a0a1e;
    color: rgba(255, 255, 255, 0.88);
    font-size: 12px;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    padding: 4px 12px;
}
QStatusBar::item { border: none; }
QStatusBar QLabel { color: rgba(255, 255, 255, 0.88); margin: 0 8px; }
QStackedWidget { background: transparent; }

/* ── 菜单：玻璃弹出层 ── */
QMenu {
    background: rgba(20, 20, 40, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px; padding: 8px;
}
QMenu::item { padding: 8px 24px; border-radius: 8px; color: rgba(255, 255, 255, 0.85); font-size: 14px; }
QMenu::item:selected { background: rgba(111, 111, 255, 0.15); color: #8B8BFF; }

/* ── 分组框：玻璃容器 ── */
QGroupBox {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    margin-top: 16px; padding-top: 16px; padding: 12px;
    font-weight: 600; color: rgba(255, 255, 255, 0.9);
}
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; color: rgba(255, 255, 255, 0.65); }

QCheckBox, QRadioButton { color: rgba(255, 255, 255, 0.85); font-size: 14px; spacing: 8px; }
QCheckBox::indicator, QRadioButton::indicator { width: 16px; height: 16px; }
QRadioButton::indicator::unchecked { border: 2px solid rgba(255,255,255,0.2); border-radius: 9px; background: transparent; }
QRadioButton::indicator::checked { border: 2px solid #6F6FFF; border-radius: 9px; background: #6F6FFF; }
QCheckBox::indicator::unchecked { border: 2px solid rgba(255,255,255,0.2); border-radius: 4px; background: transparent; }
QCheckBox::indicator::checked { border: 2px solid #6F6FFF; border-radius: 4px; background: #6F6FFF; }

/* ── 输入框 ── */
QLineEdit {
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px; padding: 6px 12px;
    background: rgba(255, 255, 255, 0.05);
    color: rgba(255, 255, 255, 0.9); font-size: 13px;
    font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
}
QLineEdit:focus { border-color: #6F6FFF; background: rgba(255, 255, 255, 0.08); }
QLineEdit::placeholder { color: rgba(255, 255, 255, 0.3); }

/* ── 下拉框 ── */
QComboBox {
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px; padding: 5px 12px;
    background: rgba(255, 255, 255, 0.05);
    color: rgba(255, 255, 255, 0.9); font-size: 13px;
    font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
}
QComboBox:hover { border-color: rgba(255, 255, 255, 0.18); }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    background: rgba(20, 20, 40, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px; padding: 4px;
    selection-background-color: rgba(111, 111, 255, 0.15);
    selection-text-color: #8B8BFF; color: rgba(255, 255, 255, 0.85);
}

/* ── 进度条 ── */
QProgressBar {
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px; text-align: center;
    background: rgba(255, 255, 255, 0.03);
    color: rgba(255, 255, 255, 0.6); height: 20px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6F6FFF, stop:1 #27D2BF);
    border-radius: 7px;
}

/* ── 滑块 ── */
QSlider::groove:horizontal {
    height: 4px; border-radius: 2px;
    background: rgba(255, 255, 255, 0.08);
}
QSlider::sub-page:horizontal {
    background: #6F6FFF; border-radius: 2px;
}
QSlider::handle:horizontal {
    width: 14px; height: 14px; margin: -5px 0;
    border-radius: 7px; background: #FFFFFF;
    border: 2px solid #6F6FFF;
}

/* ── 滚动条 ── */
QScrollBar:vertical { border: none; background: transparent; width: 6px; margin: 0; }
QScrollBar::handle:vertical { background: rgba(255,255,255,0.1); border-radius: 3px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: rgba(255,255,255,0.2); }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { border: none; background: transparent; height: 6px; margin: 0; }
QScrollBar::handle:horizontal { background: rgba(255,255,255,0.1); border-radius: 3px; min-width: 30px; }
QScrollBar::handle:horizontal:hover { background: rgba(255,255,255,0.2); }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ── 文本编辑 ── */
QTextEdit {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    color: rgba(255, 255, 255, 0.7);
    font-family: "Cascadia Code", "Consolas", monospace; font-size: 12px;
}

/* ── SpinBox ── */
QSpinBox {
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px; padding: 4px 10px;
    background: rgba(255, 255, 255, 0.05);
    color: rgba(255, 255, 255, 0.9); font-size: 13px;
    font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
}
QSpinBox::up-button, QSpinBox::down-button {
    border: none; background: transparent; width: 0px; height: 0px;
}

/* ── 通用标签 ── */
QLabel { color: rgba(255, 255, 255, 0.85); }

/* ── 工具提示 ── */
QToolTip {
    background: rgba(20, 20, 40, 0.9);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 6px; padding: 4px 8px;
    color: rgba(255, 255, 255, 0.9); font-size: 12px;
}

/* ── 消息框 ── */
QMessageBox { background: #12122a; }
QMessageBox QLabel { color: rgba(255, 255, 255, 0.9); }
"""

QSS_LIGHT = """
/* ═══════════════════════════════════════════════════════
   拾光 5.1 — Glassmorphism 2.0 Light Theme
   浅色基底 + 玻璃面板 + 紫青色调 + 微交互
   ═══════════════════════════════════════════════════════ */

QMainWindow { background: transparent; }
QPushButton { border: 1px solid transparent; outline: none; font-family: "Microsoft YaHei UI", "PingFang SC", sans-serif; }

/* ── 自定义标题栏 ── */
#TitleBar {
    background: transparent;
    border: none;
    min-height: 40px;
    max-height: 40px;
}
#TitleLabel {
    color: #1A1A1A;
    font-size: 14px;
    font-weight: 600;
    padding-left: 14px;
}
#WinBtn, #WinBtnClose {
    background: transparent;
    border: none;
    border-radius: 6px;
    color: #4A4A4A;
    font-size: 14px;
    min-width: 40px;
    max-width: 40px;
    min-height: 32px;
    max-height: 32px;
}
#WinBtn:hover {
    background: rgba(0, 0, 0, 0.12);
    color: #1A1A1A;
}
#WinBtnClose:hover {
    background: #E53935;
    color: #FFFFFF;
}

/* ── 玻璃面板通用 ── */
#GlassPanel {
    background: transparent;
    border: 1px solid rgba(0, 0, 0, 0.12);
    border-radius: 12px;
}

/* ── 可折叠面板按钮 ── */
#CollapsibleBtn {
    text-align: left;
    font-weight: 600;
    padding: 10px 12px;
    border: 1px solid rgba(0, 0, 0, 0.12);
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.6);
    color: #1A1A1A;
    font-size: 13px;
}

/* ── 编辑页专用 ── */
#InfoLabel { color: #4A4A4A; }
#ColorBtn { border-radius: 10px; border: 1px solid rgba(128, 128, 128, 0.3); }
#LogText {
    font-family: "Cascadia Code", Consolas, monospace;
    font-size: 12px;
    background: rgba(255, 255, 255, 0.5);
    border: 1px solid rgba(0, 0, 0, 0.12);
    border-radius: 10px;
    color: #333333;
}

/* ── 通用标签 ── */
#SectionLabel { font-weight: 600; color: #1A1A1A; }
#SecondaryLabel { color: #4A4A4A; font-size: 13px; }
#HintLabel { color: #6B6B6B; font-size: 12px; }
#CanvasLabel {
    background: rgba(255, 255, 255, 0.5);
    border: 1px solid rgba(0, 0, 0, 0.12);
    border-radius: 10px;
}

/* ── 滚动区域 viewport 透明 ── */
QScrollArea { border: none; background: transparent; }
QScrollArea > QWidget > QWidget { background: transparent; }
#CollapsibleContent { background: transparent; border: none; }

/* ── 侧边栏 ── */
#SideBar {
    background: rgba(255, 255, 255, 0.5);
    border-right: 1px solid rgba(0, 0, 0, 0.10);
}
#SideBtn {
    text-align: left; padding: 10px 14px; border-radius: 10px;
    background: transparent; color: #1A1A1A;
    font-size: 14px; font-weight: 500; margin: 3px 10px;
    border: 1px solid transparent;
}
#SideBtn:hover {
    background: rgba(0, 0, 0, 0.08);
    color: #1A1A1A;
    border-color: rgba(0, 0, 0, 0.06);
}
#SideBtn:checked {
    background: rgba(111, 111, 255, 0.1);
    color: #5B5BFF;
    font-weight: 600;
    border: 1px solid rgba(111, 111, 255, 0.2);
}

/* ── 次按钮 ── */
#TopBtn {
    background: rgba(255, 255, 255, 0.6);
    border: 1px solid rgba(0, 0, 0, 0.14);
    border-radius: 10px; padding: 8px 18px;
    color: #1A1A1A; font-size: 13px; font-weight: 500;
}
#TopBtn:hover {
    background: rgba(255, 255, 255, 0.9);
    border-color: rgba(0, 0, 0, 0.15);
}
#TopBtn:pressed { background: rgba(0, 0, 0, 0.06); }

/* ── 主按钮 ── */
#TopBtnPrimary {
    background-color: #6F6FFF; border: 1px solid transparent;
    border-radius: 10px; padding: 8px 22px;
    color: #FFFFFF; font-weight: 600; font-size: 13px;
}
#TopBtnPrimary:hover { background-color: #5B5BFF; }
#TopBtnPrimary:pressed { background-color: #4B4BE3; }

/* ── 文件列表 ── */
#FileList {
    background: rgba(255, 255, 255, 0.5);
    border: 1px solid rgba(0, 0, 0, 0.12);
    border-radius: 12px; padding: 8px; outline: none;
}
#FileList::item {
    padding: 10px 12px; border-radius: 8px;
    color: #1A1A1A; font-size: 14px;
    border: none; outline: none; margin: 2px 4px;
}
#FileList::item:selected {
    background: rgba(111, 111, 255, 0.12);
    color: #5B5BFF; border: none; outline: none;
}
#FileList::item:hover {
    background: rgba(0, 0, 0, 0.06);
    border: none; outline: none;
}

/* ── 预览区 ── */
#Preview {
    background: rgba(255, 255, 255, 0.4);
    border: 1px solid rgba(0, 0, 0, 0.12);
    border-radius: 12px;
    color: #9A9A9A; font-size: 14px;
}

/* ── 状态栏 ── */
QStatusBar {
    background: #f0f1f6;
    color: #3A3A3A;
    font-size: 12px;
    border-top: 1px solid rgba(0, 0, 0, 0.10);
    padding: 4px 12px;
}
QStatusBar::item { border: none; }
QStatusBar QLabel { color: #3A3A3A; margin: 0 8px; }
QStackedWidget { background: transparent; }

/* ── 菜单 ── */
QMenu {
    background: rgba(255, 255, 255, 0.92);
    border: 1px solid rgba(0, 0, 0, 0.14);
    border-radius: 12px; padding: 8px;
}
QMenu::item { padding: 8px 24px; border-radius: 8px; color: #1A1A1A; font-size: 14px; }
QMenu::item:selected { background: rgba(111, 111, 255, 0.12); color: #5B5BFF; }

/* ── 分组框 ── */
QGroupBox {
    background: rgba(255, 255, 255, 0.5);
    border: 1px solid rgba(0, 0, 0, 0.12);
    border-radius: 12px;
    margin-top: 16px; padding-top: 16px; padding: 12px;
    font-weight: 600; color: #1A1A1A;
}
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; color: #4A4A4A; }

QCheckBox, QRadioButton { color: #1A1A1A; font-size: 14px; spacing: 8px; }
QCheckBox::indicator, QRadioButton::indicator { width: 16px; height: 16px; }
QRadioButton::indicator::unchecked { border: 2px solid rgba(0,0,0,0.15); border-radius: 9px; background: transparent; }
QRadioButton::indicator::checked { border: 2px solid #6F6FFF; border-radius: 9px; background: #6F6FFF; }
QCheckBox::indicator::unchecked { border: 2px solid rgba(0,0,0,0.15); border-radius: 4px; background: transparent; }
QCheckBox::indicator::checked { border: 2px solid #6F6FFF; border-radius: 4px; background: #6F6FFF; }

/* ── 输入框 ── */
QLineEdit {
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 10px; padding: 6px 12px;
    background: rgba(255, 255, 255, 0.6);
    color: #1A1A1A; font-size: 13px;
    font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
}
QLineEdit:focus { border-color: #6F6FFF; background: rgba(255, 255, 255, 0.9); }
QLineEdit::placeholder { color: #9A9A9A; }

/* ── 下拉框 ── */
QComboBox {
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 10px; padding: 5px 12px;
    background: rgba(255, 255, 255, 0.6);
    color: #1A1A1A; font-size: 13px;
    font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
}
QComboBox:hover { border-color: rgba(0, 0, 0, 0.18); }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid rgba(0, 0, 0, 0.14);
    border-radius: 10px; padding: 4px;
    selection-background-color: rgba(111, 111, 255, 0.12);
    selection-text-color: #5B5BFF; color: #1A1A1A;
}

/* ── 进度条 ── */
QProgressBar {
    border: 1px solid rgba(0, 0, 0, 0.12);
    border-radius: 8px; text-align: center;
    background: rgba(0, 0, 0, 0.06);
    color: #4A4A4A; height: 20px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6F6FFF, stop:1 #27D2BF);
    border-radius: 7px;
}

/* ── 滑块 ── */
QSlider::groove:horizontal {
    height: 4px; border-radius: 2px;
    background: rgba(0, 0, 0, 0.14);
}
QSlider::sub-page:horizontal {
    background: #6F6FFF; border-radius: 2px;
}
QSlider::handle:horizontal {
    width: 14px; height: 14px; margin: -5px 0;
    border-radius: 7px; background: #FFFFFF;
    border: 2px solid #6F6FFF;
}

/* ── 滚动条 ── */
QScrollBar:vertical { border: none; background: transparent; width: 6px; margin: 0; }
QScrollBar::handle:vertical { background: rgba(0,0,0,0.1); border-radius: 3px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: rgba(0,0,0,0.2); }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { border: none; background: transparent; height: 6px; margin: 0; }
QScrollBar::handle:horizontal { background: rgba(0,0,0,0.1); border-radius: 3px; min-width: 30px; }
QScrollBar::handle:horizontal:hover { background: rgba(0,0,0,0.2); }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ── 文本编辑 ── */
QTextEdit {
    background: rgba(255, 255, 255, 0.5);
    border: 1px solid rgba(0, 0, 0, 0.12);
    border-radius: 8px;
    color: #333333;
    font-family: "Cascadia Code", "Consolas", monospace; font-size: 12px;
}

/* ── SpinBox ── */
QSpinBox {
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 10px; padding: 4px 10px;
    background: rgba(255, 255, 255, 0.6);
    color: #1A1A1A; font-size: 13px;
    font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
}
QSpinBox::up-button, QSpinBox::down-button {
    border: none; background: transparent; width: 0px; height: 0px;
}

/* ── 通用标签 ── */
QLabel { color: #1A1A1A; }

/* ── 工具提示 ── */
QToolTip {
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid rgba(0, 0, 0, 0.14);
    border-radius: 6px; padding: 4px 8px;
    color: #1A1A1A; font-size: 12px;
}

/* ── 消息框 ── */
QMessageBox { background: #f4f5fa; }
QMessageBox QLabel { color: #1A1A1A; }
"""

IMG_EXTS = ('.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff', '.tif', '.gif', '.ico')

COLLAGE_LAYOUTS = {
    "2张·横排":      {"cols": 2, "rows": 1},
    "2张·竖排":      {"cols": 1, "rows": 2},
    "3张·横排":      {"cols": 3, "rows": 1},
    "3张·竖排":      {"cols": 1, "rows": 3},
    "3张·L形":       {"cols": 2, "rows": 2, "special": "L3"},
    "4张·田字格":    {"cols": 2, "rows": 2},
    "4张·横排":      {"cols": 4, "rows": 1},
    "5张·L形":       {"cols": 2, "rows": 3, "special": "L4"},
    "5张·2×3缺一":   {"cols": 3, "rows": 2, "special": "hole5"},
    "6张·2×3":       {"cols": 3, "rows": 2},
    "6张·3×2":       {"cols": 2, "rows": 3},
    "9张·3×3":       {"cols": 3, "rows": 3},
}

def _is_image_file(path):
    return os.path.splitext(path)[1].lower() in IMG_EXTS

# ─── 浏览页 ───
class ViewerPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.current_folder = ""
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(12)

        # 顶部按钮栏
        top = QHBoxLayout(); top.setSpacing(8)
        b1 = QPushButton("打开图片"); b1.setObjectName("TopBtn")
        b2 = QPushButton("打开文件夹"); b2.setObjectName("TopBtn")
        b3 = QPushButton("上一张"); b3.setObjectName("TopBtn")
        b4 = QPushButton("下一张"); b4.setObjectName("TopBtn")
        b5 = QPushButton("复制路径"); b5.setObjectName("TopBtn")
        b_print = QPushButton("打印"); b_print.setObjectName("TopBtn")
        top.addWidget(b1); top.addWidget(b2); top.addWidget(b3); top.addWidget(b4); top.addWidget(b5); top.addWidget(b_print)
        top.addStretch()
        lay.addLayout(top)

        # 主体：左列表 + 右预览
        body = QHBoxLayout(); body.setSpacing(12)
        self.file_list = QListWidget(); self.file_list.setObjectName("FileList")
        self.file_list.setMaximumWidth(260)
        self.file_list.setIconSize(QSize(160, 160))
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self._show_context_menu)
        body.addWidget(self.file_list)

        self.preview = QLabel("打开一张图片开始浏览"); self.preview.setObjectName("Preview")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.preview.setMinimumSize(600, 400)
        body.addWidget(self.preview, stretch=1)
        lay.addLayout(body, stretch=1)

        # 底部信息栏
        self.info_label = QLabel("就绪")
        lay.addWidget(self.info_label)

        # 信号
        b1.clicked.connect(self.open_files)
        b2.clicked.connect(self.open_folder)
        b3.clicked.connect(self.prev_image)
        b4.clicked.connect(self.next_image)
        b5.clicked.connect(self.copy_path)
        b_print.clicked.connect(self.print_image)
        self.file_list.currentItemChanged.connect(self.show_image)
        self.file_list.itemDoubleClicked.connect(self._on_item_double_click)

    def _fill_folder(self, d, select=None):
        """列出目录内容：先「返回上级」、再子文件夹、最后图片。返回到图片数量。"""
        self.current_folder = d
        self.file_list.clear()
        try:
            names = sorted(os.listdir(d))
        except Exception as e:
            self.app.set_status(f"读取目录失败: {e}")
            return 0
        dirs, imgs = [], []
        for n in names:
            fp = os.path.join(d, n)
            if os.path.isdir(fp):
                dirs.append(n)
            elif os.path.isfile(fp) and _is_image_file(fp):
                imgs.append(n)
        # 返回上级
        parent = os.path.dirname(os.path.normpath(d))
        if parent and parent != os.path.normpath(d):
            it = QListWidgetItem("⬆ 返回上级")
            it.setData(Qt.UserRole, parent)
            it.setData(Qt.UserRole + 1, "up")
            self.file_list.addItem(it)
        for n in dirs:
            fp = os.path.join(d, n)
            it = QListWidgetItem("📁 " + n)
            it.setData(Qt.UserRole, fp)
            it.setData(Qt.UserRole + 1, "dir")
            self.file_list.addItem(it)
        for n in imgs:
            fp = os.path.join(d, n)
            it = QListWidgetItem(n)
            it.setData(Qt.UserRole, fp)
            it.setData(Qt.UserRole + 1, "file")
            self.file_list.addItem(it)
        # 选中目标图片
        if select:
            for i in range(self.file_list.count()):
                if self.file_list.item(i).data(Qt.UserRole) == select:
                    self.file_list.setCurrentRow(i); break
        elif imgs:
            self.file_list.setCurrentRow(self.file_list.count() - len(imgs))
        return len(imgs)

    def _on_item_double_click(self, item):
        """双击：文件夹/返回上级 进入；图片打开大图预览"""
        if item is None:
            return
        kind = item.data(Qt.UserRole + 1)
        path = item.data(Qt.UserRole)
        if kind in ("dir", "up"):
            n = self._fill_folder(path)
            self.app.set_status(f"已进入: {path}，共 {n} 张图片")
        else:
            self.show_image(item, None)

    def open_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "打开图片", "", "图片 (*.jpg *.jpeg *.png *.bmp *.webp *.gif)")
        if files:
            folder = os.path.dirname(files[0])
            n = self._fill_folder(folder, select=files[0])
            self.app.set_status(f"已加载 {n} 张图片")
    def open_folder(self):
        d = QFileDialog.getExistingDirectory(self, "打开文件夹")
        if d:
            n = self._fill_folder(d)
            if n > 0:
                self.app.set_status(f"已打开文件夹: {os.path.basename(d)}，共 {n} 张图片")
            else:
                self.app.set_status("该文件夹中没有图片")

    def show_image(self, cur, prev):
        if cur:
            if cur.data(Qt.UserRole + 1) in ("dir", "up"):
                self.info_label.setText("双击进入该文件夹")
                return
            path = cur.data(Qt.UserRole)
            pm = QPixmap(path)
            if not pm.isNull():
                scaled = pm.scaled(self.preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.preview.setPixmap(scaled)
                size = os.path.getsize(path)
                w, h = pm.width(), pm.height()
                self.info_label.setText(f"{os.path.basename(path)}  ·  {w}×{h}  ·  {size/1024:.1f} KB")
                self.app.set_status(f"查看: {os.path.basename(path)}")

    def _step_image(self, delta):
        """上/下一张：只在图片项之间移动，跳过文件夹"""
        n = self.file_list.count()
        r = self.file_list.currentRow() + delta
        while 0 <= r < n:
            if self.file_list.item(r).data(Qt.UserRole + 1) == "file":
                self.file_list.setCurrentRow(r); return
            r += delta

    def prev_image(self):
        self._step_image(-1)

    def next_image(self):
        self._step_image(1)

    def copy_path(self):
        cur = self.file_list.currentItem()
        if cur:
            path = cur.data(Qt.UserRole)
            QApplication.clipboard().setText(path)
            self.app.set_status("已复制路径到剪贴板")

    def print_image(self):
        cur = self.file_list.currentItem()
        if cur:
            path = cur.data(Qt.UserRole)
            try:
                os.startfile(path, "print")
                self.app.set_status(f"正在打印: {os.path.basename(path)}")
            except Exception as e:
                QMessageBox.warning(self, "打印", f"打印失败: {e}\n请确保系统关联了图片打印程序")

    def _show_context_menu(self, pos: QPoint):
        item = self.file_list.itemAt(pos)
        if not item:
            return
        kind = item.data(Qt.UserRole + 1)
        if kind in ("dir", "up"):
            menu = QMenu(self)
            act_enter = QAction("进入文件夹", self)
            act_copy_dir = QAction("复制路径", self)
            menu.addAction(act_enter)
            menu.addAction(act_copy_dir)
            act = menu.exec(self.file_list.mapToGlobal(pos))
            dpath = item.data(Qt.UserRole)
            if act == act_enter:
                n = self._fill_folder(dpath)
                self.app.set_status(f"已进入: {dpath}，共 {n} 张图片")
            elif act == act_copy_dir:
                QApplication.clipboard().setText(dpath)
                self.app.set_status("已复制路径到剪贴板")
            return
        menu = QMenu(self)
        # 第一组：管理操作
        act_rename = QAction("重命名", self)
        act_delete = QAction("删除", self)
        menu.addAction(act_rename)
        menu.addAction(act_delete)
        menu.addSeparator()
        # 第二组：文件操作
        act_print = QAction("打印", self)
        act_copy = QAction("复制路径", self)
        act_open_folder = QAction("打开所在文件夹", self)
        menu.addAction(act_print)
        menu.addAction(act_copy)
        menu.addAction(act_open_folder)
        menu.addSeparator()
        # 第三组：跳转操作
        act_edit = QAction("编辑", self)
        act_compress = QAction("压缩", self)
        act_collage = QAction("添加到拼图", self)
        act_batch = QAction("添加到批处理", self)
        menu.addAction(act_edit)
        menu.addAction(act_compress)
        menu.addAction(act_collage)
        menu.addAction(act_batch)
        act = menu.exec(self.file_list.mapToGlobal(pos))
        path = item.data(Qt.UserRole)
        if act == act_edit:
            self.app.stack.widget(3)._load(path)
            self.app.switch_page(3)
        elif act == act_compress:
            cpage = self.app.stack.widget(2)
            if path not in cpage.files:
                cpage.files.append(path)
                it = QListWidgetItem(os.path.basename(path))
                it.setData(Qt.UserRole, path)
                cpage.file_list.addItem(it)
                cpage._update_size()
            self.app.switch_page(2)
        elif act == act_collage:
            cpage = self.app.stack.widget(1)
            it = QListWidgetItem(os.path.basename(path))
            it.setData(Qt.UserRole, path)
            cpage.img_list.addItem(it)
            self.app.switch_page(1)
        elif act == act_batch:
            bpage = self.app.stack.widget(4)
            if not bpage.src_edit.text():
                bpage.src_edit.setText(os.path.dirname(path))
            self.app.switch_page(4)
        elif act == act_print:
            try:
                os.startfile(path, "print")
                self.app.set_status(f"正在打印: {os.path.basename(path)}")
            except Exception as e:
                QMessageBox.warning(self, "打印", f"打印失败: {e}")
        elif act == act_copy:
            QApplication.clipboard().setText(path)
            self.app.set_status("已复制路径")
        elif act == act_open_folder:
            folder = os.path.dirname(path)
            os.startfile(folder)
        elif act == act_rename:
            self._rename_item(item)
        elif act == act_delete:
            self._delete_item(item)

    def _rename_item(self, item):
        old_path = item.data(Qt.UserRole)
        old_name = os.path.basename(old_path)
        new_name, ok = QInputDialog.getText(self, "重命名", "新文件名:", text=old_name)
        if ok and new_name and new_name != old_name:
            new_path = os.path.join(os.path.dirname(old_path), new_name)
            try:
                os.rename(old_path, new_path)
                item.setText(new_name)
                item.setData(Qt.UserRole, new_path)
                self.app.set_status(f"已重命名为: {new_name}")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"重命名失败: {e}")

    def _delete_item(self, item):
        path = item.data(Qt.UserRole)
        reply = QMessageBox.question(self, "删除", f"确定删除 {os.path.basename(path)}？",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                os.remove(path)
                row = self.file_list.row(item)
                self.file_list.takeItem(row)
                self.app.set_status(f"已删除: {os.path.basename(path)}")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"删除失败: {e}")

# ─── 拼图页 ───
class CollagePage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.images = []
        self.paths = []
        self.offsets = []
        self.bg_color = "#FFFFFF"
        self.result_img = None
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(12)

        # 主体：左面板 + 右预览
        body = QHBoxLayout(); body.setSpacing(12)

        # 左面板
        left = QVBoxLayout(); left.setSpacing(12)
        # 布局选择
        lay_label = QLabel("选择布局"); lay_label.setObjectName("SectionLabel")
        left.addWidget(lay_label)
        self.layout_group = QButtonGroup(self)
        layout_grid = QGridLayout(); layout_grid.setSpacing(4)
        self.layout_var = "2张·横排"
        names = list(COLLAGE_LAYOUTS.keys())
        for idx, name in enumerate(names):
            row = idx // 2
            col = idx % 2
            cfg = COLLAGE_LAYOUTS[name]
            thumb = self._make_layout_thumb(cfg)
            rb = QRadioButton(name)
            rb.setStyleSheet("")  # styled via QSS QRadioButton
            rb.toggled.connect(lambda checked, n=name: self._on_layout_change(n) if checked else None)
            self.layout_group.addButton(rb)
            wrap = QHBoxLayout(); wrap.setSpacing(8); wrap.setContentsMargins(0,0,0,0)
            wrap.addWidget(thumb)
            wrap.addWidget(rb)
            wrap_w = QWidget(); wrap_w.setLayout(wrap)
            layout_grid.addWidget(wrap_w, row, col)
            if idx == 0:
                rb.setChecked(True)
        left.addLayout(layout_grid)

        # 图片列表
        list_label = QLabel("图片列表（点击添加）"); list_label.setObjectName("SectionLabel")
        left.addWidget(list_label)
        self.img_list = QListWidget(); self.img_list.setObjectName("FileList")
        self.img_list.setMaximumHeight(200)
        left.addWidget(self.img_list)
        self.count_label = QLabel("已导入 0 张")
        self.count_label.setObjectName("SecondaryLabel")
        left.addWidget(self.count_label)

        # 列表按钮
        btn_row = QHBoxLayout(); btn_row.setSpacing(8)
        b_add = QPushButton("+ 添加"); b_add.setObjectName("TopBtn")
        b_up = QPushButton("↑ 上移"); b_up.setObjectName("TopBtn")
        b_down = QPushButton("↓ 下移"); b_down.setObjectName("TopBtn")
        b_del = QPushButton("✕ 移除"); b_del.setObjectName("TopBtn")
        b_clear = QPushButton("清空"); b_clear.setObjectName("TopBtn")
        btn_row.addWidget(b_add); btn_row.addWidget(b_up); btn_row.addWidget(b_down); btn_row.addWidget(b_del); btn_row.addWidget(b_clear)
        left.addLayout(btn_row)

        # 设置
        set_label = QLabel("拼图设置"); set_label.setObjectName("SectionLabel")
        left.addWidget(set_label)
        set_grid = QGridLayout(); set_grid.setSpacing(8)
        set_grid.addWidget(QLabel("间距:"), 0, 0)
        self.spacing_slider = QSlider(Qt.Horizontal); self.spacing_slider.setRange(0, 50); self.spacing_slider.setValue(8)
        self.spacing_label = QLabel("8px")
        self.spacing_slider.valueChanged.connect(lambda v: self.spacing_label.setText(f"{v}px"))
        set_grid.addWidget(self.spacing_slider, 0, 1)
        set_grid.addWidget(self.spacing_label, 0, 2)
        set_grid.addWidget(QLabel("圆角:"), 1, 0)
        self.radius_slider = QSlider(Qt.Horizontal); self.radius_slider.setRange(0, 50); self.radius_slider.setValue(0)
        self.radius_label = QLabel("0px")
        self.radius_slider.valueChanged.connect(lambda v: self.radius_label.setText(f"{v}px"))
        set_grid.addWidget(self.radius_slider, 1, 1)
        set_grid.addWidget(self.radius_label, 1, 2)
        set_grid.addWidget(QLabel("背景色:"), 2, 0)
        self.bg_btn = QPushButton("白色"); self.bg_btn.setObjectName("TopBtn")
        self.bg_btn.clicked.connect(self._pick_bg)
        set_grid.addWidget(self.bg_btn, 2, 1)
        set_grid.addWidget(QLabel("质量:"), 2, 2)
        self.quality_slider = QSlider(Qt.Horizontal); self.quality_slider.setRange(10, 100); self.quality_slider.setValue(95)
        self.quality_label = QLabel("95%")
        self.quality_slider.valueChanged.connect(lambda v: self.quality_label.setText(f"{v}%"))
        set_grid.addWidget(self.quality_slider, 2, 3)
        set_grid.addWidget(self.quality_label, 2, 4)
        left.addLayout(set_grid)

        # 生成按钮
        gen_row = QHBoxLayout(); gen_row.setSpacing(8); gen_row.setContentsMargins(0, 0, 0, 8)
        b_gen = AnimatedButton("生成拼图"); b_gen.setObjectName("TopBtnPrimary")
        b_export = QPushButton("导出"); b_export.setObjectName("TopBtn")
        b_copy = QPushButton("复制到剪贴板"); b_copy.setObjectName("TopBtn")
        gen_row.addWidget(b_gen); gen_row.addWidget(b_export); gen_row.addWidget(b_copy)
        left.addLayout(gen_row)
        body.addLayout(left, stretch=1)

        # 右预览
        right = QVBoxLayout(); right.setSpacing(8)
        preview_label = QLabel("预览"); preview_label.setObjectName("SectionLabel")
        right.addWidget(preview_label)
        self.preview = QLabel("添加图片后点击生成拼图预览"); self.preview.setObjectName("Preview")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.preview.setMinimumSize(500, 400)
        right.addWidget(self.preview, stretch=1)
        body.addLayout(right, stretch=1)
        lay.addLayout(body, stretch=1)

        # 信号
        b_add.clicked.connect(self._add_images)
        b_up.clicked.connect(self._move_up)
        b_down.clicked.connect(self._move_down)
        b_del.clicked.connect(self._remove_selected)
        b_clear.clicked.connect(self._clear_all)
        b_gen.clicked.connect(self._generate)
        b_export.clicked.connect(self._export)
        b_copy.clicked.connect(self._copy_clipboard)

    def _make_layout_thumb(self, cfg):
        """为布局生成一个小示意图（48x36）"""
        cols, rows = cfg["cols"], cfg["rows"]
        special = cfg.get("special")
        W, H = 48, 36
        pad = 2
        thumb = Image.new('RGBA', (W, H), (0,0,0,0))
        draw = ImageDraw.Draw(thumb)
        cell_w = (W - pad * (cols + 1)) // cols
        cell_h = (H - pad * (rows + 1)) // rows
        if special == "L3":
            # 左大右二
            cw = cell_w * 2 + pad
            ch = cell_h * 2 + pad
            x0, y0 = pad, pad
            draw.rounded_rectangle([x0, y0, x0 + cw, y0 + ch], 3, fill=(111,111,255,180))
            x1 = x0 + cw + pad
            draw.rounded_rectangle([x1, y0, x1 + cell_w, y0 + cell_h], 3, fill=(111,111,255,120))
            draw.rounded_rectangle([x1, y0 + cell_h + pad, x1 + cell_w, y0 + ch], 3, fill=(111,111,255,120))
        elif special == "L4":
            # 左大右四（右2x2）
            cw = cell_w * 2 + pad
            ch = cell_h * 3 + pad * 2
            x0, y0 = pad, pad
            draw.rounded_rectangle([x0, y0, x0 + cw, y0 + ch], 3, fill=(111,111,255,180))
            x1 = x0 + cw + pad
            for r in range(3):
                y = y0 + r * (cell_h + pad)
                draw.rounded_rectangle([x1, y, x1 + cell_w, y + cell_h], 3, fill=(111,111,255,120))
        elif special == "hole5":
            # 上三下二（缺右下）
            x0, y0 = pad, pad
            for c in range(3):
                x = x0 + c * (cell_w + pad)
                draw.rounded_rectangle([x, y0, x + cell_w, y0 + cell_h], 3, fill=(111,111,255,150))
            y1 = y0 + cell_h + pad
            for c in range(2):
                x = x0 + c * (cell_w + pad)
                draw.rounded_rectangle([x, y1, x + cell_w, y1 + cell_h], 3, fill=(111,111,255,150))
        else:
            # 网格
            for r in range(rows):
                for c in range(cols):
                    x = pad + c * (cell_w + pad)
                    y = pad + r * (cell_h + pad)
                    draw.rounded_rectangle([x, y, x + cell_w, y + cell_h], 3, fill=(111,111,255,150))
        data = thumb.tobytes("raw", "RGBA")
        qimg = QImage(data, W, H, W * 4, QImage.Format_RGBA8888)
        pm = QPixmap.fromImage(qimg)
        lab = QLabel()
        lab.setPixmap(pm)
        lab.setFixedSize(W, H)
        return lab

    def _on_layout_change(self, name):
        self.layout_var = name
        layout = COLLAGE_LAYOUTS.get(name, {"cols": 2, "rows": 1})
        needed = layout["cols"] * layout["rows"]
        special = layout.get("special")
        if special == "L3": needed = 3
        elif special == "L4": needed = 5
        elif special == "hole5": needed = 5
        self.app.set_status(f"当前布局需要 {needed} 张，已添加 {len(self.images)} 张")

    def _add_images(self):
        files, _ = QFileDialog.getOpenFileNames(self, "选择图片", "", "图片 (*.jpg *.jpeg *.png *.bmp *.webp *.gif)")
        added = 0
        for f in files:
            if not _is_image_file(f) or not os.path.isfile(f): continue
            if f in self.paths: continue
            try:
                img = Image.open(f).convert("RGB")
                self.paths.append(f)
                self.images.append(img)
                self.offsets.append([0, 0])
                it = QListWidgetItem(os.path.basename(f))
                it.setData(Qt.UserRole, f)
                self.img_list.addItem(it)
                added += 1
            except Exception as e:
                QMessageBox.warning(self, "错误", f"无法打开 {os.path.basename(f)}:\n{e}")
        if added:
            self._on_layout_change(self.layout_var)
            self._update_count()

    def _update_count(self):
        self.count_label.setText(f"已导入 {len(self.images)} 张")

    def _move_up(self):
        row = self.img_list.currentRow()
        if row <= 0: return
        self.images[row], self.images[row-1] = self.images[row-1], self.images[row]
        self.paths[row], self.paths[row-1] = self.paths[row-1], self.paths[row]
        self.offsets[row], self.offsets[row-1] = self.offsets[row-1], self.offsets[row]
        cur = self.img_list.takeItem(row)
        self.img_list.insertItem(row-1, cur)
        self.img_list.setCurrentRow(row-1)

    def _move_down(self):
        row = self.img_list.currentRow()
        if row < 0 or row >= self.img_list.count() - 1: return
        self.images[row], self.images[row+1] = self.images[row+1], self.images[row]
        self.paths[row], self.paths[row+1] = self.paths[row+1], self.paths[row]
        self.offsets[row], self.offsets[row+1] = self.offsets[row+1], self.offsets[row]
        cur = self.img_list.takeItem(row)
        self.img_list.insertItem(row+1, cur)
        self.img_list.setCurrentRow(row+1)

    def _remove_selected(self):
        row = self.img_list.currentRow()
        if row < 0: return
        del self.images[row]
        del self.paths[row]
        if row < len(self.offsets): del self.offsets[row]
        self.img_list.takeItem(row)
        self._update_count()

    def _clear_all(self):
        self.images.clear()
        self.paths.clear()
        self.offsets.clear()
        self.img_list.clear()
        self.result_img = None
        self.preview.setPixmap(QPixmap())
        self.preview.setText("添加图片后点击生成拼图预览")
        self._update_count()

    def _pick_bg(self):
        from PySide6.QtWidgets import QColorDialog
        color = QColorDialog.getColor()
        if color.isValid():
            self.bg_color = color.name()
            self.bg_btn.setText(color.name())

    def _generate(self):
        if len(self.images) < 2:
            QMessageBox.warning(self, "提示", "至少需要2张图片才能拼图")
            return
        layout = COLLAGE_LAYOUTS.get(self.layout_var, {"cols": 2, "rows": 1})
        cols, rows = layout["cols"], layout["rows"]
        special = layout.get("special")
        spacing = self.spacing_slider.value()
        radius = self.radius_slider.value()
        quality = self.quality_slider.value()

        if special == "L3": needed = 3
        elif special == "L4": needed = 5
        elif special == "hole5": needed = 5
        else: needed = cols * rows

        imgs = self.images[:needed]
        max_w = max(img.width for img in imgs)
        max_h = max(img.height for img in imgs)

        resized = []
        for i, img in enumerate(imgs):
            ratio = max(max_w / img.width, max_h / img.height)
            new_w = int(img.width * ratio)
            new_h = int(img.height * ratio)
            img_resized = img.resize((new_w, new_h), Image.LANCZOS)
            max_left = new_w - max_w
            max_top = new_h - max_h
            dx, dy = self.offsets[i] if i < len(self.offsets) else [0, 0]
            left = max(0, min(max_left, max_left // 2 + int(dx)))
            top = max(0, min(max_top, max_top // 2 + int(dy)))
            img_cropped = img_resized.crop((left, top, left + max_w, top + max_h))
            if radius > 0:
                mask = Image.new('L', (max_w, max_h), 0)
                mdraw = ImageDraw.Draw(mask)
                mdraw.rounded_rectangle([0, 0, max_w-1, max_h-1], radius, fill=255)
                img_cropped = Image.composite(img_cropped, Image.new('RGB', (max_w, max_h), self.bg_color), mask)
                resized.append((img_cropped, mask))
            else:
                resized.append((img_cropped, None))

        cell_rects = []
        if special == "L3":
            cw2 = max_w * 2 + spacing
            ch2 = max_h * 2 + spacing
            canvas = Image.new('RGB', (cw2, ch2), self.bg_color)
            for i in range(3):
                img, mask = resized[i]
                x = 0 if i == 0 else (max_w + spacing)
                y = 0 if i < 2 else (max_h + spacing)
                canvas.paste(img, (x, y), mask); cell_rects.append((x, y, i))
        elif special == "L4":
            cw2 = max_w * 2 + spacing
            ch2 = max_h * 2 + spacing
            canvas = Image.new('RGB', (cw2, ch2), self.bg_color)
            for i in range(5):
                img, mask = resized[i]
                if i == 0:
                    x, y = 0, 0
                else:
                    col = (i - 1) % 2; row = (i - 1) // 2
                    x = max_w + spacing + col * (max_w + spacing)
                    y = row * (max_h + spacing)
                canvas.paste(img, (x, y), mask); cell_rects.append((x, y, i))
        elif special == "hole5":
            w3 = max_w * 3 + spacing * 2
            canvas = Image.new('RGB', (w3, max_h * 2 + spacing), self.bg_color)
            for c in range(3):
                x = c * (max_w + spacing)
                img, mask = resized[c]
                canvas.paste(img, (x, 0), mask); cell_rects.append((x, 0, c))
            for c in range(2):
                x = c * (max_w + spacing)
                img, mask = resized[c+3]
                canvas.paste(img, (x, max_h + spacing), mask); cell_rects.append((x, max_h+spacing, c+3))
        else:
            cw = max_w * cols + spacing * (cols - 1)
            ch = max_h * rows + spacing * (rows - 1)
            canvas = Image.new('RGB', (cw, ch), self.bg_color)
            for r in range(rows):
                for c in range(cols):
                    idx = r * cols + c
                    if idx < len(resized):
                        x = c * (max_w + spacing)
                        y = r * (max_h + spacing)
                        img, mask = resized[idx]
                        canvas.paste(img, (x, y), mask); cell_rects.append((x, y, idx))

        self.result_img = canvas
        # 转 QPixmap 预览
        data = canvas.tobytes("raw", "RGB")
        qimg = QImage(data, canvas.width, canvas.height, canvas.width * 3, QImage.Format_RGB888)
        pm = QPixmap.fromImage(qimg)
        scaled = pm.scaled(self.preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.preview.setPixmap(scaled)
        self.app.set_status(f"拼图已生成: {canvas.width}×{canvas.height}")

    def _export(self):
        if self.result_img is None:
            QMessageBox.warning(self, "提示", "请先生成拼图")
            return
        path, _ = QFileDialog.getSaveFileName(self, "导出拼图", "collage.png", "PNG (*.png);;JPEG (*.jpg)")
        if path:
            quality = self.quality_slider.value()
            self.result_img.save(path, quality=quality)
            self.app.set_status(f"已导出: {path}")

    def _copy_clipboard(self):
        """把生成的拼图复制到系统剪贴板"""
        if self.result_img is None:
            QMessageBox.warning(self, "提示", "请先生成拼图")
            return
        try:
            buf = io.BytesIO()
            self.result_img.save(buf, format="PNG")
            pm = QPixmap()
            pm.loadFromData(buf.getvalue(), "PNG")
            if pm.isNull():
                self.app.set_status("复制失败：图片转换异常")
                return
            QApplication.clipboard().setPixmap(pm)
            self.app.set_status("已复制到剪贴板")
        except Exception as e:
            self.app.set_status(f"复制失败: {e}")

# ─── 压缩页 ───
class CompressPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.files = []
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(12)

        body = QHBoxLayout(); body.setSpacing(12)
        left = QVBoxLayout(); left.setSpacing(8)
        g_list = QGroupBox("待压缩文件")
        left.addWidget(g_list)
        self.file_list = QListWidget(); self.file_list.setObjectName("FileList")
        glay = QVBoxLayout(g_list); glay.setSpacing(8); glay.setContentsMargins(16, 20, 16, 16)
        glay.addWidget(self.file_list, stretch=1)
        btn_row = QHBoxLayout(); btn_row.setSpacing(8)
        b_add = QPushButton("+ 添加文件"); b_add.setObjectName("TopBtn")
        b_folder = QPushButton("+ 添加文件夹"); b_folder.setObjectName("TopBtn")
        b_rm = QPushButton("✕ 移除"); b_rm.setObjectName("TopBtn")
        b_clr = QPushButton("清空"); b_clr.setObjectName("TopBtn")
        btn_row.addWidget(b_add); btn_row.addWidget(b_folder); btn_row.addWidget(b_rm); btn_row.addWidget(b_clr)
        left.addLayout(btn_row)
        self.size_label = QLabel("共 0 个文件，总大小 0 B")
        left.addWidget(self.size_label)
        body.addLayout(left, stretch=1)

        right = QVBoxLayout(); right.setSpacing(16)
        g_quality = QGroupBox("压缩设置")
        g_quality.setMinimumWidth(360)
        qlay = QGridLayout(g_quality); qlay.setSpacing(10); qlay.setContentsMargins(16, 20, 16, 16)
        qlay.addWidget(QLabel("JPEG 质量:"), 0, 0)
        self.quality_slider = QSlider(Qt.Horizontal); self.quality_slider.setRange(10, 100); self.quality_slider.setValue(85)
        self.quality_slider.setMinimumWidth(180)
        self.quality_label = QLabel("85%")
        self.quality_slider.valueChanged.connect(lambda v: self.quality_label.setText(f"{v}%"))
        qlay.addWidget(self.quality_slider, 0, 1)
        qlay.addWidget(self.quality_label, 0, 2)
        self.resize_cb = QCheckBox("限制最大尺寸（长边超过则等比缩小）")
        self.max_dim = QSpinBox(); self.max_dim.setRange(200, 10000); self.max_dim.setValue(1920)
        self.max_dim.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.max_dim.setEnabled(False)
        self.resize_cb.toggled.connect(self.max_dim.setEnabled)
        qlay.addWidget(self.resize_cb, 1, 0, 1, 3)
        px_label = QLabel("px"); px_label.setObjectName("HintLabel")
        px_h = QHBoxLayout(); px_h.setSpacing(4); px_h.addWidget(self.max_dim); px_h.addWidget(px_label)
        qlay.addLayout(px_h, 2, 1)
        tip = QLabel("例如原图 4000×3000，设 1920px 则等比缩为 1920×1440")
        tip.setObjectName("HintLabel")
        tip.setWordWrap(True)
        qlay.addWidget(tip, 3, 0, 1, 3)
        self.del_cb = QCheckBox("压缩后删除原图（请谨慎！）")
        qlay.addWidget(self.del_cb, 4, 0, 1, 3)
        self.est_label = QLabel("估计压缩后大小：—")
        self.est_label.setObjectName("SecondaryLabel")
        qlay.addWidget(self.est_label, 5, 0, 1, 3)
        right.addWidget(g_quality)

        g_out = QGroupBox("输出")
        g_out.setMinimumWidth(360)
        olay = QVBoxLayout(g_out); olay.setSpacing(10); olay.setContentsMargins(16, 20, 16, 16)
        self.same_dir_rb = QRadioButton("覆盖原文件目录（加后缀）")
        self.custom_rb = QRadioButton("输出到指定文件夹:")
        self.same_dir_rb.setChecked(True)
        olay.addWidget(self.same_dir_rb)
        dir_row = QHBoxLayout()
        dir_row.setSpacing(8)
        self.out_dir_edit = QLineEdit(); self.out_dir_edit.setReadOnly(True)
        self.out_dir_edit.setEnabled(False)
        b_browse = QPushButton("浏览"); b_browse.setObjectName("TopBtn")
        b_browse.clicked.connect(self._pick_out_dir)
        self.custom_rb.toggled.connect(self.out_dir_edit.setEnabled)
        self.custom_rb.toggled.connect(b_browse.setEnabled)
        dir_row.addWidget(self.custom_rb)
        dir_row.addWidget(self.out_dir_edit)
        dir_row.addWidget(b_browse)
        olay.addLayout(dir_row)
        suf_row = QHBoxLayout()
        suf_row.addWidget(QLabel("文件名后缀:"))
        self.suffix_edit = QLineEdit("_compressed"); self.suffix_edit.setMaximumWidth(120)
        suf_row.addWidget(self.suffix_edit)
        suf_row.addWidget(QLabel("（输出到原目录时使用）"))
        suf_row.addStretch()
        olay.addLayout(suf_row)
        right.addWidget(g_out)

        b_row = QHBoxLayout(); b_row.setSpacing(8)
        b_preview = QPushButton("单个预览"); b_preview.setObjectName("TopBtn")
        b_start = AnimatedButton("开始压缩"); b_start.setObjectName("TopBtnPrimary")
        b_row.addWidget(b_preview); b_row.addWidget(b_start)
        right.addLayout(b_row)
        self.progress = QProgressBar(); self.progress.setValue(0)
        right.addWidget(self.progress)
        right.addStretch()
        body.addLayout(right, stretch=1)
        lay.addLayout(body, stretch=1)

        b_add.clicked.connect(self._add_files)
        b_folder.clicked.connect(self._add_folder)
        b_rm.clicked.connect(self._remove_selected)
        b_clr.clicked.connect(self._clear_list)
        b_start.clicked.connect(self._compress)
        b_preview.clicked.connect(self._preview_single)

    def _add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "选择图片", "", "图片 (*.jpg *.jpeg *.png *.bmp *.webp *.gif)")
        added = 0
        for f in files:
            if _is_image_file(f) and f not in self.files:
                self.files.append(f)
                size = os.path.getsize(f)
                it = QListWidgetItem(f"{os.path.basename(f)}  ({self._fmt(size)})")
                it.setData(Qt.UserRole, f)
                self.file_list.addItem(it)
                added += 1
        if added: self._update_size()

    def _add_folder(self):
        d = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if not d: return
        count = 0
        for root_dir, _, fns in os.walk(d):
            for fn in fns:
                fp = os.path.join(root_dir, fn)
                if _is_image_file(fp) and fp not in self.files:
                    self.files.append(fp)
                    size = os.path.getsize(fp)
                    it = QListWidgetItem(f"{os.path.relpath(fp, d)}  ({self._fmt(size)})")
                    it.setData(Qt.UserRole, fp)
                    self.file_list.addItem(it)
                    count += 1
        self._update_size()
        if count == 0:
            QMessageBox.information(self, "提示", "该文件夹中没有图片")

    def _remove_selected(self):
        for item in self.file_list.selectedItems():
            row = self.file_list.row(item)
            del self.files[row]
            self.file_list.takeItem(row)
        self._update_size()

    def _clear_list(self):
        self.files.clear()
        self.file_list.clear()
        self._update_size()

    def _fmt(self, n):
        if n < 1024: return f"{n} B"
        if n < 1024*1024: return f"{n/1024:.1f} KB"
        if n < 1024*1024*1024: return f"{n/1024/1024:.1f} MB"
        return f"{n/1024/1024/1024:.2f} GB"

    def _update_size(self):
        total = sum(os.path.getsize(f) for f in self.files)
        self.size_label.setText(f"共 {len(self.files)} 个文件，总大小 {self._fmt(total)}")
        if self.files:
            est = total * self.quality_slider.value() // 100
            self.est_label.setText(f"估计压缩后大小：≈ {self._fmt(est)}")
        else:
            self.est_label.setText("估计压缩后大小：—")

    def _pick_out_dir(self):
        d = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if d:
            self.out_dir_edit.setText(d)

    def _preview_single(self):
        if not self.files:
            QMessageBox.warning(self, "提示", "请先添加文件")
            return
        path = self.files[0]
        try:
            original = Image.open(path)
            quality = self.quality_slider.value()
            max_dim = self.max_dim.value() if self.resize_cb.isChecked() else None
            img = original.copy()
            if img.mode in ('RGBA', 'P', 'LA'):
                img = img.convert('RGBA')
                bg = Image.new('RGB', img.size, (255,255,255))
                bg.paste(img, mask=img.split()[3])
                img = bg
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            if max_dim:
                img.thumbnail((max_dim, max_dim), Image.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format='JPEG', quality=quality, optimize=True)
            comp_size = buf.tell()
            buf.seek(0)
            compressed = Image.open(buf)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"预览失败:\n{e}")
            return
        orig_size = os.path.getsize(path)
        dlg = QDialog(self)
        dlg.setWindowTitle(f"压缩预览 — {os.path.basename(path)}")
        dlg.resize(760, 520)
        dl = QVBoxLayout(dlg); dl.setContentsMargins(12,12,12,12)
        row = QHBoxLayout()
        orig_lab = QLabel(f"原图\n{original.width}×{original.height} · {self._fmt(orig_size)}")
        orig_lab.setAlignment(Qt.AlignCenter)
        op = original.copy(); op.thumbnail((320,320))
        oprgb = op.convert('RGB')
        od = oprgb.tobytes("raw", "RGB")
        oq = QImage(od, oprgb.width, oprgb.height, oprgb.width*3, QImage.Format_RGB888)
        orig_pm = QPixmap.fromImage(oq)
        orig_img = QLabel(); orig_img.setPixmap(orig_pm)
        col_l = QVBoxLayout(); col_l.addWidget(orig_img); col_l.addWidget(orig_lab)
        w1 = QWidget(); w1.setLayout(col_l)
        row.addWidget(w1)
        comp_lab = QLabel(f"压缩后 ({quality}%)\n{compressed.width}×{compressed.height} · {self._fmt(comp_size)}")
        comp_lab.setAlignment(Qt.AlignCenter)
        cp = compressed.copy(); cp.thumbnail((320,320))
        cprgb = cp.convert('RGB')
        cd = cprgb.tobytes("raw", "RGB")
        cq = QImage(cd, cprgb.width, cprgb.height, cprgb.width*3, QImage.Format_RGB888)
        comp_pm = QPixmap.fromImage(cq)
        comp_img = QLabel(); comp_img.setPixmap(comp_pm)
        col_r = QVBoxLayout(); col_r.addWidget(comp_img); col_r.addWidget(comp_lab)
        w2 = QWidget(); w2.setLayout(col_r)
        row.addWidget(w2)
        dl.addLayout(row)
        saved = orig_size - comp_size
        pct = comp_size / orig_size * 100 if orig_size > 0 else 0
        info = QLabel(f"最大尺寸: {'≤'+str(max_dim)+'px' if max_dim else '无'}  |  节省: {self._fmt(saved)} ({100-pct:.1f}%)")
        dl.addWidget(info)
        b_close = QPushButton("关闭"); b_close.setObjectName("TopBtn")
        b_close.clicked.connect(dlg.accept)
        dl.addWidget(b_close)
        dlg.exec()

    def _compress(self):
        if not self.files:
            QMessageBox.warning(self, "提示", "请先添加文件")
            return
        quality = self.quality_slider.value()
        max_dim = self.max_dim.value() if self.resize_cb.isChecked() else None
        suffix = self.suffix_edit.text().strip()
        del_orig = self.del_cb.isChecked()
        same_dir = self.same_dir_rb.isChecked()
        out_dir = self.out_dir_edit.text() if not same_dir else ""
        if not same_dir and not out_dir:
            QMessageBox.warning(self, "提示", "请选择输出文件夹")
            return
        self.progress.setMaximum(len(self.files))
        self.progress.setValue(0)
        success = 0; errors = []
        total_before = 0; total_after = 0
        for i, path in enumerate(self.files):
            try:
                img = Image.open(path)
                before = os.path.getsize(path)
                total_before += before
                if img.mode in ('RGBA', 'P', 'LA'):
                    img = img.convert('RGBA')
                    bg = Image.new('RGB', img.size, (255,255,255))
                    bg.paste(img, mask=img.split()[3])
                    img = bg
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                if max_dim:
                    img.thumbnail((max_dim, max_dim), Image.LANCZOS)
                out_name = os.path.basename(path)
                name_no_ext, ext = os.path.splitext(out_name)
                if out_dir:
                    os.makedirs(out_dir, exist_ok=True)
                    out_path = os.path.join(out_dir, out_name)
                else:
                    out_path = os.path.join(os.path.dirname(path), f"{name_no_ext}{suffix}{ext}")
                img.save(out_path, quality=quality, optimize=True)
                after = os.path.getsize(out_path)
                total_after += after
                if del_orig and out_path != path:
                    os.remove(path)
                success += 1
            except Exception as e:
                errors.append(f"{os.path.basename(path)}: {e}")
            self.progress.setValue(i+1)
            QApplication.processEvents()
        msg = f"完成！成功 {success} 个"
        if errors:
            msg += f"\n失败 {len(errors)} 个:\n" + "\n".join(errors[:5])
        if total_before > 0:
            pct = total_after / total_before * 100
            msg += f"\n原始 {self._fmt(total_before)} → 压缩后 {self._fmt(total_after)}（{pct:.1f}%）"
        self.app.set_status(msg)
        QMessageBox.information(self, "压缩完成", msg)

# ─── 编辑页 ───
# -*- coding: utf-8 -*-
# ─── 编辑页 ───
class CanvasLabel(QLabel):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(500, 400)
        self.setObjectName("CanvasLabel")
        self.dragging = False
        self.start_pos = None
        self.cur_pos = None
        self.persistent_rect = None
        self.preview_rotated = None

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton and self.page.base is not None:
            p = e.position().toPoint()
            hit = self.page._hit_wm(p)
            if hit:
                self.page._sel_wm = hit
                self.page._wm_drag = (p.x() - hit["x"], p.y() - hit["y"])
                self.dragging = False
                self.update()
                return
            self.page._sel_wm = None
            if self.page.tool is not None:
                self.dragging = True
                self.start_pos = p
                self.cur_pos = p
                self.page._on_press(p)
                self.update()

    def mouseMoveEvent(self, e):
        if self.page._wm_drag is not None:
            p = e.position().toPoint()
            ox, oy = self.page._wm_drag
            if self.page._sel_wm:
                self.page._sel_wm["x"] = p.x() - ox
                self.page._sel_wm["y"] = p.y() - oy
                # 节流刷新
                if not hasattr(self.page, '_wm_drag_timer'):
                    self.page._wm_drag_timer = None
                if self.page._wm_drag_timer is None:
                    self.page._wm_drag_timer = self.page.startTimer(16)
            return
        if self.dragging:
            p = e.position().toPoint()
            if self.page.tool == "裁剪" and self.start_pos:
                ratio_text = self.page.crop_ratio.currentText()
                if ratio_text != "自由":
                    ratio_map = {"1:1": 1.0, "4:3": 4/3, "3:2": 3/2, "16:9": 16/9, "9:16": 9/16}
                    target_ratio = ratio_map.get(ratio_text, 0)
                    if target_ratio > 0:
                        dx = p.x() - self.start_pos.x()
                        dy = p.y() - self.start_pos.y()
                        aw = abs(dx)
                        ah = abs(dy)
                        if target_ratio >= 1:
                            if aw / max(ah, 1) > target_ratio:
                                dy = int(aw / target_ratio * (1 if dy >= 0 else -1))
                            else:
                                dx = int(ah * target_ratio * (1 if dx >= 0 else -1))
                        else:
                            if ah / max(aw, 1) > (1/target_ratio):
                                dx = int(ah * target_ratio * (1 if dx >= 0 else -1))
                            else:
                                dy = int(aw / target_ratio * (1 if dy >= 0 else -1))
                        p = QPoint(self.start_pos.x() + dx, self.start_pos.y() + dy)
            self.cur_pos = p
            self.page._on_move(self.cur_pos)
            self.update()

    def mouseReleaseEvent(self, e):
        if self.page._wm_drag is not None:
            self.page._wm_drag = None
            if hasattr(self.page, '_wm_drag_timer') and self.page._wm_drag_timer is not None:
                self.page.killTimer(self.page._wm_drag_timer)
                self.page._wm_drag_timer = None
            self.page._refresh()
            self.page._push_undo()
            self.update()
            return
        if e.button() == Qt.LeftButton and self.dragging:
            self.dragging = False
            if self.start_pos and self.cur_pos:
                self.page._on_release(self.start_pos, self.cur_pos)
                if self.page.tool == "裁剪":
                    self.persistent_rect = QRect(self.start_pos, self.cur_pos)
                else:
                    self.persistent_rect = None
            self.start_pos = None
            self.cur_pos = None
            self.update()

    def mouseDoubleClickEvent(self, e): pass

    def paintEvent(self, e):
        super().paintEvent(e)
        if self.dragging and self.start_pos and self.cur_pos:
            t = self.page.tool
            painter = QPainter(self)
            pen = QPen(QColor(111, 111, 255), 2, Qt.DashLine)
            painter.setPen(pen)
            if t == "直线":
                painter.drawLine(self.start_pos, self.cur_pos)
            elif t == "箭头":
                import math
                painter.drawLine(self.start_pos, self.cur_pos)
                dx = self.cur_pos.x()-self.start_pos.x()
                dy = self.cur_pos.y()-self.start_pos.y()
                ang = math.atan2(dy, dx); al = 14
                a1 = ang + math.radians(150); a2 = ang - math.radians(150)
                p3 = QPointF(self.cur_pos.x()+al*math.cos(a1), self.cur_pos.y()+al*math.sin(a1))
                p4 = QPointF(self.cur_pos.x()+al*math.cos(a2), self.cur_pos.y()+al*math.sin(a2))
                painter.setBrush(QBrush(QColor(111, 111, 255)))
                painter.drawPolygon(QPolygonF([QPointF(self.cur_pos), p3, p4]))
            elif t == "画圈":
                painter.drawEllipse(QRect(self.start_pos, self.cur_pos).normalized())
            else:
                painter.drawRect(QRect(self.start_pos, self.cur_pos))
            painter.end()
        elif self.persistent_rect is not None:
            painter = QPainter(self)
            pen = QPen(QColor(111, 111, 255), 2, Qt.DashLine)
            painter.setPen(pen)
            painter.drawRect(self.persistent_rect)
            painter.end()
        elif self.page._sel_wm is not None:
            wm = self.page._sel_wm
            if hasattr(self.page, '_disp_scale'):
                s = self.page._disp_scale
                ox, oy = self.page._disp_off
                rx = wm["x"] * s + ox
                ry = wm["y"] * s + oy
                rw = wm["img"].width * s
                rh = wm["img"].height * s
                painter = QPainter(self)
                pen = QPen(QColor(111, 111, 255), 2, Qt.DashLine)
                painter.setPen(pen)
                painter.drawRect(QRectF(rx-4, ry-4, rw+8, rh+8))
                painter.end()


class CollapsibleGroupBox(QWidget):
    """可折叠的分组框"""
    def __init__(self, title, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self); lay.setContentsMargins(0,0,0,0); lay.setSpacing(0)
        self.btn = QPushButton("▼ " + title)
        self.btn.setObjectName("CollapsibleBtn")
        self.btn.clicked.connect(self.toggle)
        lay.addWidget(self.btn)
        self.content = QWidget()
        self.content.setObjectName("CollapsibleContent")
        self.content_lay = QVBoxLayout(self.content); self.content_lay.setContentsMargins(8,8,8,8); self.content_lay.setSpacing(6)
        lay.addWidget(self.content)
        self._collapsed = False

    def toggle(self):
        self._collapsed = not self._collapsed
        self.content.setVisible(not self._collapsed)
        self.btn.setText(("▼ " if not self._collapsed else "▶ ") + self.btn.text()[2:])

    def layout(self):
        return self.content_lay

    def addWidget(self, w):
        self.content_lay.addWidget(w)

    def addLayout(self, l):
        self.content_lay.addLayout(l)


class EditPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.base = None
        self.original = None
        self.file_path = None
        self.undo_stack = []
        self.redo_stack = []
        self.tool = None
        self.draw_color = "#FF0000"
        self.wm_items = []
        self._pending_crop = None
        self._rembg_session = None
        self._mask_model_path = ""
        self._sel_wm = None
        self._wm_drag = None
        self._wm_drag_timer = None
        self.twm_color = "#FFFFFF"
        # 证件照换背景：默认标准蓝
        self.id_bg_color = "#438EDB"
        self.id_chip_buttons = []
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(12)

        top = QHBoxLayout(); top.setSpacing(8)
        b_open = QPushButton("打开图片"); b_open.setObjectName("TopBtn")
        b_save = AnimatedButton("保存"); b_save.setObjectName("TopBtnPrimary")
        b_undo = QPushButton("撤销"); b_undo.setObjectName("TopBtn")
        b_redo = QPushButton("重做"); b_redo.setObjectName("TopBtn")
        b_reset = QPushButton("重置"); b_reset.setObjectName("TopBtn")
        b_copy = QPushButton("复制到剪贴板"); b_copy.setObjectName("TopBtn")
        top.addWidget(b_open); top.addWidget(b_save); top.addWidget(b_copy); top.addWidget(b_undo); top.addWidget(b_redo); top.addWidget(b_reset)
        top.addStretch()
        self.info_label = QLabel("未打开图片")
        self.info_label.setObjectName("InfoLabel")
        top.addWidget(self.info_label)
        lay.addLayout(top)

        body = QHBoxLayout(); body.setSpacing(12)
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        self.scroll.setMinimumWidth(292); self.scroll.setMaximumWidth(380)
        self.scroll.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.viewport().setAutoFillBackground(False)
        panel = QWidget()
        panel.setAutoFillBackground(False)
        pl = QVBoxLayout(panel); pl.setSpacing(12); pl.setContentsMargins(0,0,0,0)

        g_tool = CollapsibleGroupBox("标注工具")
        tl = QGridLayout(); g_tool.content_lay.addLayout(tl); tl.setSpacing(6); tl.setContentsMargins(16,20,16,16)
        self.tool_group = QButtonGroup(self)
        for i, t in enumerate(["打码", "矩形框", "箭头", "直线", "画圈"]):
            rb = QRadioButton(t)
            rb.toggled.connect(lambda checked, x=t: checked and (setattr(self, 'tool', x), setattr(self.canvas, 'persistent_rect', None) if x != '裁剪' else None))
            self.tool_group.addButton(rb)
            tl.addWidget(rb, i // 3, i % 3)
        tl.addWidget(QLabel("颜色:"), 2, 0)
        self.color_btn = QPushButton(""); self.color_btn.setFixedSize(40, 28)
        self.color_btn.setObjectName("ColorBtn")
        self.color_btn.clicked.connect(self._pick_color)
        self.color_btn.setStyleSheet(f"background:{self.draw_color}; border-radius:10px; border:1px solid rgba(128,128,128,0.3);")
        tl.addWidget(self.color_btn, 2, 1, 1, 2)
        tl.addWidget(QLabel("粗细:"), 3, 0)
        self.width_slider = QSlider(Qt.Horizontal); self.width_slider.setRange(1, 20); self.width_slider.setValue(3)
        tl.addWidget(self.width_slider, 3, 1, 1, 2)
        tl.addWidget(QLabel("打码强度:"), 4, 0)
        self.mosaic_slider = QSlider(Qt.Horizontal); self.mosaic_slider.setRange(4, 64); self.mosaic_slider.setValue(16)
        tl.addWidget(self.mosaic_slider, 4, 1, 1, 2)
        pl.addWidget(g_tool)

        g_crop = CollapsibleGroupBox("裁剪")
        cl = QGridLayout(); g_crop.content_lay.addLayout(cl); cl.setSpacing(8); cl.setContentsMargins(16,20,16,16)
        rb_crop = QRadioButton("裁剪工具")
        rb_crop.toggled.connect(lambda checked: checked and setattr(self, 'tool', '裁剪'))
        self.tool_group.addButton(rb_crop)
        cl.addWidget(rb_crop, 0, 0)
        cl.addWidget(QLabel("锁定比例:"), 0, 1)
        self.crop_ratio = QComboBox(); self.crop_ratio.addItems(["自由", "1:1", "4:3", "3:2", "16:9", "9:16"])
        cl.addWidget(self.crop_ratio, 0, 2)
        self.crop_info = QLabel("选「裁剪工具」后在图上拖动，点应用裁剪")
        self.crop_info.setObjectName("SecondaryLabel"); self.crop_info.setWordWrap(True)
        cl.addWidget(self.crop_info, 1, 0, 1, 3)
        b_do_crop = AnimatedButton("应用裁剪"); b_do_crop.setObjectName("TopBtnPrimary")
        b_do_crop.clicked.connect(self._do_crop)
        cl.addWidget(b_do_crop, 2, 0, 1, 3)
        pl.addWidget(g_crop)

        g_rot = CollapsibleGroupBox("旋转 / 翻转")
        rl = QGridLayout(); g_rot.content_lay.addLayout(rl); rl.setSpacing(8); rl.setContentsMargins(16,20,16,16)
        rl.setColumnStretch(1, 1)
        rl.addWidget(QLabel("角度:"), 0, 0)
        self.angle_spin = QSpinBox(); self.angle_spin.setRange(-360, 360)
        self.angle_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        rl.addWidget(self.angle_spin, 0, 1)
        deg_label = QLabel("°"); deg_label.setObjectName("HintLabel")
        rl.addWidget(deg_label, 0, 2)
        self.angle_slider = QSlider(Qt.Horizontal); self.angle_slider.setRange(-360, 360)
        self.angle_slider.valueChanged.connect(self.angle_spin.setValue)
        self.angle_slider.sliderReleased.connect(self._on_slider_release)
        self.angle_spin.valueChanged.connect(self.angle_slider.setValue)
        rl.addWidget(self.angle_slider, 1, 0, 1, 2)
        rl.addWidget(QLabel("拖动滑块实时旋转"), 2, 0, 1, 2)
        b_row = QHBoxLayout(); b_row.setSpacing(6)
        for txt, ang in [("左90", 90), ("右90", -90), ("180", 180)]:
            b = QPushButton(txt); b.setObjectName("TopBtn")
            b.clicked.connect(lambda checked, a=ang: self._quick_rotate(a))
            b_row.addWidget(b)
        rl.addLayout(b_row, 3, 0, 1, 2)
        f_row = QHBoxLayout(); f_row.setSpacing(6)
        b_fh = QPushButton("水平翻转"); b_fh.setObjectName("TopBtn")
        b_fv = QPushButton("垂直翻转"); b_fv.setObjectName("TopBtn")
        b_fh.clicked.connect(lambda: self._flip("h")); b_fv.clicked.connect(lambda: self._flip("v"))
        f_row.addWidget(b_fh); f_row.addWidget(b_fv)
        rl.addLayout(f_row, 4, 0, 1, 2)
        pl.addWidget(g_rot)

        g_adj = CollapsibleGroupBox("调整")
        al = QGridLayout(); g_adj.content_lay.addLayout(al); al.setSpacing(8); al.setContentsMargins(16,20,16,16)
        al.setColumnStretch(1, 1)
        self.sliders = {}
        for i, (name, lo, hi, val) in enumerate([
            ("亮度", 20, 200, 100), ("对比度", 20, 250, 100),
            ("饱和度", 0, 250, 100), ("锐度", 0, 300, 100)]):
            al.addWidget(QLabel(name), i, 0)
            sl = QSlider(Qt.Horizontal); sl.setRange(lo, hi); sl.setValue(val)
            lb = QLabel(f"{val}%")
            sl.valueChanged.connect(lambda v, l=lb: l.setText(f"{v}%"))
            al.addWidget(sl, i, 1); al.addWidget(lb, i, 2)
            self.sliders[name] = (sl, lb)
        b_apply = AnimatedButton("应用调整"); b_apply.setObjectName("TopBtnPrimary")
        b_apply.clicked.connect(self._apply_adjust)
        al.addWidget(b_apply, 4, 0, 1, 3)
        pl.addWidget(g_adj)

        g_eff = CollapsibleGroupBox("效果")
        el = QGridLayout(); g_eff.content_lay.addLayout(el); el.setSpacing(6); el.setContentsMargins(16,20,16,16)
        el.setColumnStretch(0, 1); el.setColumnStretch(1, 1)
        for i, (txt, key) in enumerate([("灰度","gray"),("反色","invert"),("模糊","blur"),("锐化","sharpen")]):
            b = QPushButton(txt); b.setObjectName("TopBtn")
            b.clicked.connect(lambda checked, k=key: self._apply_effect(k))
            el.addWidget(b, i // 2, i % 2)
        b_aibg = AnimatedButton("✂ AI 去背景"); b_aibg.setObjectName("TopBtnPrimary")
        b_aibg.clicked.connect(self._remove_bg)
        el.addWidget(b_aibg, 2, 0, 1, 2)
        pl.addWidget(g_eff)

        g_id = CollapsibleGroupBox("证件照换背景")
        il = QGridLayout(); g_id.content_lay.addLayout(il); il.setSpacing(8); il.setContentsMargins(16,20,16,16)
        il.setColumnStretch(1, 1)
        il.addWidget(QLabel("底色:"), 0, 0)
        id_row = QHBoxLayout(); id_row.setSpacing(8)
        for name, hexc in [("白底", "#FFFFFF"), ("标准蓝", "#438EDB"), ("红底", "#D9001B")]:
            b = QPushButton(name)
            b.setMinimumSize(58, 30); b.setMaximumHeight(30)
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            b.clicked.connect(lambda _, c=hexc, btn=b: self._pick_id_preset(c, btn))
            self.id_chip_buttons.append((b, hexc))
            id_row.addWidget(b)
        self.id_custom_chip = QPushButton("自定义")
        self.id_custom_chip.setMinimumSize(58, 30); self.id_custom_chip.setMaximumHeight(30)
        self.id_custom_chip.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.id_custom_chip.clicked.connect(self._pick_id_custom)
        id_row.addWidget(self.id_custom_chip)
        id_row.addStretch()
        il.addLayout(id_row, 0, 1, 1, 2)
        id_note = QLabel("AI 自动识别人物，把纯色底证件照换成所选底色，适合白 / 蓝 / 红底互转")
        id_note.setObjectName("SecondaryLabel"); id_note.setWordWrap(True)
        il.addWidget(id_note, 1, 0, 1, 3)
        b_idbg = AnimatedButton("一键换背景"); b_idbg.setObjectName("TopBtnPrimary")
        b_idbg.clicked.connect(self._change_id_bg)
        il.addWidget(b_idbg, 2, 0, 1, 3)
        self._refresh_id_chips()
        pl.addWidget(g_id)

        g_twm = CollapsibleGroupBox("文字水印")
        tl2 = QGridLayout(); g_twm.content_lay.addLayout(tl2); tl2.setSpacing(6); tl2.setContentsMargins(16,20,16,16)
        tl2.setColumnStretch(1, 1)
        tl2.addWidget(QLabel("文字:"), 0, 0)
        self.twm_text = QLineEdit("拾光"); tl2.addWidget(self.twm_text, 0, 1, 1, 2)
        tl2.addWidget(QLabel("字号:"), 1, 0)
        self.twm_size = QSpinBox(); self.twm_size.setRange(12, 300); self.twm_size.setValue(48)
        self.twm_size.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        tl2.addWidget(self.twm_size, 1, 1)
        tl2.addWidget(QLabel("颜色:"), 1, 2)
        self.twm_color_btn = QPushButton(""); self.twm_color_btn.setFixedSize(40, 28)
        self.twm_color_btn.setObjectName("ColorBtn")
        self.twm_color_btn.clicked.connect(self._pick_twm_color)
        self.twm_color_btn.setStyleSheet(f"background:{self.twm_color}; border-radius:10px; border:1px solid rgba(128,128,128,0.3);")
        tl2.addWidget(self.twm_color_btn, 1, 3)
        tl2.addWidget(QLabel("透明度:"), 2, 0)
        self.twm_alpha = QSlider(Qt.Horizontal); self.twm_alpha.setRange(5, 100); self.twm_alpha.setValue(60)
        tl2.addWidget(self.twm_alpha, 2, 1, 1, 3)
        b_twm = AnimatedButton("添加文字水印"); b_twm.setObjectName("TopBtnPrimary")
        b_twm.clicked.connect(self._add_text_wm)
        tl2.addWidget(b_twm, 3, 0, 1, 4)
        pl.addWidget(g_twm)

        g_iwm = CollapsibleGroupBox("图片水印")
        il = QGridLayout(); g_iwm.content_lay.addLayout(il); il.setSpacing(6); il.setContentsMargins(16,20,16,16)
        il.setColumnStretch(1, 1)
        b_iwm_pick = QPushButton("选择水印图"); b_iwm_pick.setObjectName("TopBtn")
        b_iwm_pick.clicked.connect(self._pick_wm_img)
        il.addWidget(b_iwm_pick, 0, 0)
        self.iwm_name = QLabel("未选择"); self.iwm_name.setObjectName("SecondaryLabel")
        il.addWidget(self.iwm_name, 0, 1, 1, 2)
        il.addWidget(QLabel("透明度:"), 1, 0)
        self.iwm_alpha = QSlider(Qt.Horizontal); self.iwm_alpha.setRange(10, 100); self.iwm_alpha.setValue(50)
        il.addWidget(self.iwm_alpha, 1, 1, 1, 2)
        il.addWidget(QLabel("缩放:"), 2, 0)
        self.iwm_scale = QSlider(Qt.Horizontal); self.iwm_scale.setRange(10, 200); self.iwm_scale.setValue(100)
        il.addWidget(self.iwm_scale, 2, 1, 1, 2)
        self.twm_size.valueChanged.connect(lambda: self._update_sel_wm())
        self.twm_alpha.valueChanged.connect(lambda: self._update_sel_wm())
        self.iwm_alpha.valueChanged.connect(lambda: self._update_sel_wm())
        self.iwm_scale.valueChanged.connect(lambda: self._update_sel_wm())
        b_iwm = AnimatedButton("添加图片水印"); b_iwm.setObjectName("TopBtnPrimary")
        b_iwm.clicked.connect(self._add_img_wm)
        il.addWidget(b_iwm, 3, 0, 1, 2)
        b_del_wm = QPushButton("删除水印"); b_del_wm.setObjectName("TopBtn")
        b_del_wm.clicked.connect(self._del_selected_wm)
        il.addWidget(b_del_wm, 3, 2)
        pl.addWidget(g_iwm)
        pl.addStretch()
        self.scroll.setWidget(panel)
        body.addWidget(self.scroll)

        self.canvas = CanvasLabel(self)
        body.addWidget(self.canvas, stretch=1)
        lay.addLayout(body, stretch=1)

        b_open.clicked.connect(self._open)
        b_save.clicked.connect(self._save)
        b_copy.clicked.connect(self._copy_clipboard)
        b_undo.clicked.connect(self._undo)
        b_redo.clicked.connect(self._redo)
        b_reset.clicked.connect(self._reset)

    def _open(self):
        path, _ = QFileDialog.getOpenFileName(self, "打开图片", "", "图片 (*.jpg *.jpeg *.png *.bmp *.webp)")
        if path: self._load(path)

    def _load(self, path):
        try:
            img = Image.open(path).convert("RGBA")
            self.file_path = path
            self.original = img.copy()
            self.base = img.copy()
            self.undo_stack = [img.copy()]
            self.redo_stack = []
            self.wm_items = []
            self._refresh()
            self.info_label.setText(f"{os.path.basename(path)}  {img.width}×{img.height}")
            self.app.set_status(f"已打开: {os.path.basename(path)}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法打开:\n{e}")

    def timerEvent(self, event):
        if hasattr(self, '_wm_drag_timer') and self._wm_drag_timer == event.timerId():
            self._refresh(fast=True)

    def _hit_wm(self, p):
        if not hasattr(self, '_disp_scale'): return None
        ox, oy = self._disp_off
        s = self._disp_scale
        ix = int((p.x() - ox) / s)
        iy = int((p.y() - oy) / s)
        for wm in reversed(self.wm_items):
            if wm["x"] <= ix <= wm["x"] + wm["img"].width and wm["y"] <= iy <= wm["y"] + wm["img"].height:
                return wm
        return None

    def _refresh(self, fast=False):
        if self.base is None: return
        cw = max(self.canvas.width() - 20, 400)
        ch = max(self.canvas.height() - 20, 300)
        if self.canvas.preview_rotated is not None:
            src_img = self.canvas.preview_rotated
            scale = min(cw / src_img.width, ch / src_img.height)
            disp = src_img.resize((int(src_img.width*scale), int(src_img.height*scale)), Image.BILINEAR if fast else Image.LANCZOS)
        else:
            scale = min(cw / self.base.width, ch / self.base.height)
            sw, sh = int(self.base.width*scale), int(self.base.height*scale)
            # 先缩底图
            disp = self.base.resize((sw, sh), Image.BILINEAR if fast else Image.LANCZOS).convert("RGBA")
            # 再 paste 水印（也缩到显示尺寸）
            for wm in self.wm_items:
                wmx, wmy = int(wm["x"]*scale), int(wm["y"]*scale)
                wmw, wmh = int(wm["img"].width*scale), int(wm["img"].height*scale)
                if wmw > 0 and wmh > 0:
                    wm_small = wm["img"].resize((wmw, wmh), Image.BILINEAR)
                    disp.paste(wm_small, (wmx, wmy), wm_small)
        self._disp_scale = scale
        self._disp_off = ((self.canvas.width() - disp.width)//2, (self.canvas.height() - disp.height)//2)
        bg = Image.new("RGB", disp.size, (240,240,240))
        bg.paste(disp, mask=disp.split()[3])
        data = bg.tobytes("raw", "RGB")
        qimg = QImage(data, bg.width, bg.height, bg.width*3, QImage.Format_RGB888)
        self.canvas.setPixmap(QPixmap.fromImage(qimg))

    def _push_undo(self):
        self.undo_stack.append(self.base.copy())
        if len(self.undo_stack) > 30: self.undo_stack.pop(0)
        self.redo_stack.clear()

    def _undo(self):
        if len(self.undo_stack) > 1:
            self.redo_stack.append(self.undo_stack.pop())
            self.base = self.undo_stack[-1].copy()
            self._refresh()

    def _redo(self):
        if self.redo_stack:
            img = self.redo_stack.pop()
            self.undo_stack.append(img)
            self.base = img.copy(); self._refresh()

    def _reset(self):
        if self.original:
            self.base = self.original.copy()
            self.undo_stack = [self.original.copy()]
            self.redo_stack = []; self.wm_items = []
            self._refresh()

    def _pick_color(self):
        from PySide6.QtWidgets import QColorDialog
        c = QColorDialog.getColor()
        if c.isValid():
            self.draw_color = c.name()
            self.color_btn.setStyleSheet(f"background:{c.name()}; border-radius:10px; border:1px solid rgba(128,128,128,0.3);")

    def _to_img(self, p):
        s = self._disp_scale; ox, oy = self._disp_off
        return (int((p.x() - ox) / s), int((p.y() - oy) / s))

    def _on_press(self, p): pass
    def _on_move(self, p): pass

    def _on_release(self, p1, p2):
        if self.base is None: return
        x1, y1 = self._to_img(p1); x2, y2 = self._to_img(p2)
        rgb = self.base.convert("RGB")
        draw = ImageDraw.Draw(rgb)
        w = self.width_slider.value()
        if self.tool in ("裁剪", "打码", "矩形框"):
            ax1, ax2 = sorted([x1, x2]); ay1, ay2 = sorted([y1, y2])
            if ax2-ax1 < 3 or ay2-ay1 < 3: return
            if self.tool == "裁剪":
                self._pending_crop = (ax1, ay1, ax2, ay2)
                self.crop_info.setText(f"选区: {ax2-ax1}×{ay2-ay1}px，点应用裁剪")
            elif self.tool == "打码":
                block = self.mosaic_slider.value()
                region = rgb.crop((ax1, ay1, ax2, ay2))
                small = region.resize((max(1, region.width//block), max(1, region.height//block)), Image.BILINEAR)
                region = small.resize(region.size, Image.NEAREST)
                rgb.paste(region, (ax1, ay1, ax2, ay2))
                self.base = rgb.convert("RGBA"); self._push_undo(); self._refresh()
            elif self.tool == "矩形框":
                draw.rectangle([ax1, ay1, ax2, ay2], outline=self.draw_color, width=w)
                self.base = rgb.convert("RGBA"); self._push_undo(); self._refresh()
        elif self.tool == "直线":
            if abs(x2-x1) < 3 and abs(y2-y1) < 3: return
            draw.line([x1, y1, x2, y2], fill=self.draw_color, width=w)
            self.base = rgb.convert("RGBA"); self._push_undo(); self._refresh()
        elif self.tool == "箭头":
            if abs(x2-x1) < 3 and abs(y2-y1) < 3: return
            import math
            draw.line([x1, y1, x2, y2], fill=self.draw_color, width=w)
            ang = math.atan2(y2-y1, x2-x1); al = 12 + w*2
            a1 = ang + math.radians(150); a2 = ang - math.radians(150)
            p3 = (x2 + al*math.cos(a1), y2 + al*math.sin(a1))
            p4 = (x2 + al*math.cos(a2), y2 + al*math.sin(a2))
            draw.polygon([(x2,y2), p3, p4], fill=self.draw_color)
            self.base = rgb.convert("RGBA"); self._push_undo(); self._refresh()
        elif self.tool == "画圈":
            ax1, ax2 = sorted([x1, x2]); ay1, ay2 = sorted([y1, y2])
            if ax2-ax1 < 3 or ay2-ay1 < 3: return
            draw.ellipse([ax1, ay1, ax2, ay2], outline=self.draw_color, width=w)
            self.base = rgb.convert("RGBA"); self._push_undo(); self._refresh()

    def _do_crop(self):
        if not self._pending_crop or self.base is None: return
        self.canvas.persistent_rect = None
        x1,y1,x2,y2 = self._pending_crop
        ratio = self.crop_ratio.currentText()
        if ratio != "自由":
            rw, rh = {"1:1":(1,1),"4:3":(4,3),"3:2":(3,2),"16:9":(16,9),"9:16":(9,16)}[ratio]
            cw_, ch_ = x2-x1, y2-y1
            if cw_/ch_ > rw/rh:
                nh = int(cw_/(rw/rh)); dy = (nh-ch_)//2; y1-=dy; y2+=dy
            else:
                nw = int(ch_*(rw/rh)); dx = (nw-cw_)//2; x1-=dx; x2+=dx
        x1=max(0,x1); y1=max(0,y1); x2=min(self.base.width,x2); y2=min(self.base.height,y2)
        self.base = self.base.crop((x1,y1,x2,y2))
        self._push_undo(); self._refresh()
        self._pending_crop = None
        self.crop_info.setText("选「裁剪」后在图上拖动")

    def _on_slider_release(self):
        if self.original is None: return
        ang = self.angle_slider.value()
        self.base = self.original.copy().rotate(-ang, expand=True, resample=Image.BICUBIC)
        self._push_undo()
        self._refresh()
        self.app.set_status(f"已旋转 {ang}°")

    def _quick_rotate(self, ang):
        if self.base is None: return
        self.base = self.base.rotate(-ang, expand=True, resample=Image.BICUBIC)
        self._push_undo(); self._refresh()

    def _flip(self, d):
        if self.base is None: return
        if d == "h": self.base = self.base.transpose(Image.FLIP_LEFT_RIGHT)
        else: self.base = self.base.transpose(Image.FLIP_TOP_BOTTOM)
        self._push_undo(); self._refresh()

    def _apply_adjust(self):
        if self.base is None: return
        img = self.base.convert("RGB")
        for n, (sl, lb) in self.sliders.items():
            v = sl.value() / 100.0
            if n == "亮度": img = ImageEnhance.Brightness(img).enhance(v)
            elif n == "对比度": img = ImageEnhance.Contrast(img).enhance(v)
            elif n == "饱和度": img = ImageEnhance.Color(img).enhance(v)
            elif n == "锐度": img = ImageEnhance.Sharpness(img).enhance(v)
        self.base = img.convert("RGBA"); self._push_undo(); self._refresh()

    def _apply_effect(self, key):
        if self.base is None: return
        img = self.base.convert("RGB")
        if key == "gray": img = img.convert("L").convert("RGB")
        elif key == "invert":
            from PIL import ImageChops; img = ImageChops.invert(img)
        elif key == "blur": img = img.filter(ImageFilter.GaussianBlur(radius=3))
        elif key == "sharpen": img = img.filter(ImageFilter.SHARPEN)
        self.base = img.convert("RGBA"); self._push_undo(); self._refresh()

    def _infer_subject_mask(self, rgb_img):
        """主体分割，返回与原图同尺寸的 L 蒙版（255=主体，0=背景）。
        优先级：BiRefNet-Portrait（1024，logits→sigmoid，边缘最佳）→
        RMBG-1.4（1024，输出已含 sigmoid）→ u2net（320）。
        AI 去背景与证件照换背景共用；模型缺失抛 FileNotFoundError。"""
        import numpy as np
        import onnxruntime as ort
        base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        # (路径, 输入尺寸, 输出处理方式)  mode: sigmoid=图外sigmoid; calibrated=已在0..1做min-max
        candidates = [
            (os.path.join(base_dir, "models", "birefnet", "model.onnx"), 1024, "sigmoid"),
            (os.path.join(base_dir, "models", "rmbg", "model.onnx"), 1024, "calibrated"),
            (os.path.join(base_dir, "models", "u2net", "u2net.onnx"), 320, "calibrated"),
        ]
        chosen = None
        for p, size, mode in candidates:
            if os.path.exists(p):
                chosen = (p, size, mode)
                break
        if chosen is None:
            raise FileNotFoundError(candidates[0][0])
        model_path, size, mode = chosen
        if self._rembg_session is None or getattr(self, "_mask_model_path", "") != model_path:
            self._rembg_session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
            self._mask_model_path = model_path
        w, h = rgb_img.size
        img = rgb_img.resize((size, size), Image.BILINEAR)
        arr = np.array(img).astype(np.float32) / 255.0
        # ImageNet 归一化（三者通用）
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        arr = (arr - mean) / std
        arr = arr.transpose(2, 0, 1)[np.newaxis, ...]  # 1,3,size,size
        input_name = self._rembg_session.get_inputs()[0].name
        outputs = self._rembg_session.run(None, {input_name: arr})
        mask = outputs[-1][0, 0]
        if mode == "sigmoid":
            # BiRefNet 输出 logits，先 sigmoid；不做 min-max，避免把弱背景拉伸成主体（空洞）
            mask = 1.0 / (1.0 + np.exp(-mask))
            mask = np.clip((mask - 0.02) / 0.98, 0, 1)
        else:
            mask = (mask - mask.min()) / (mask.max() - mask.min() + 1e-8)
            # 轻微压低暗部
            mask = np.clip((mask - 0.05) / 0.95, 0, 1)
        mask_img = Image.fromarray((mask * 255).astype(np.uint8)).resize((w, h), Image.LANCZOS)
        return mask_img

    def _shrink_mask(self, mask_img, px=1, feather=0.8):
        """收缩主体蒙版外圈并轻羽化，切掉原底色残留环，避免换底后出现毛边。"""
        import numpy as np
        a = np.asarray(mask_img).astype(np.float32) / 255.0
        core = (a > 0.55).astype(np.float32)  # 只保留高置信主体
        m = core
        for _ in range(px):
            k = m.copy()
            for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1),
                           (-1, -1), (-1, 1), (1, -1), (1, 1)):
                k = np.minimum(k, np.roll(np.roll(m, dy, axis=0), dx, axis=1))
            m = k
        out = Image.fromarray((m * 255).astype(np.uint8))
        if feather > 0:
            out = out.filter(ImageFilter.GaussianBlur(radius=feather))
        return out

    def _remove_bg(self):
        log.info("点击 AI 去背景")
        if self.base is None: return
        self.app.set_status("AI 抠图中…"); QApplication.processEvents()
        try:
            mask_img = self._infer_subject_mask(self.base.convert("RGB"))
            # 应用 alpha
            result = self.base.convert("RGBA")
            result.putalpha(mask_img)
            self.base = result
            self._push_undo(); self._refresh()
            self.app.set_status("抠图完成")
        except FileNotFoundError as e:
            QMessageBox.warning(self, "抠图失败", f"模型文件不存在:\n{e}")
        except Exception as e:
            QMessageBox.warning(self, "抠图失败", f"{e}")

    # ── 证件照一键换背景 ──────────────────────────────────────
    def _pick_id_preset(self, hexc, btn):
        self.id_bg_color = hexc
        self._refresh_id_chips()

    def _pick_id_custom(self):
        from PySide6.QtWidgets import QColorDialog
        c = QColorDialog.getColor()
        if c.isValid():
            self.id_bg_color = c.name()
            self._refresh_id_chips()

    def _refresh_id_chips(self):
        """刷新色块选中态：选中项加主题描边"""
        for btn, hexc in self.id_chip_buttons:
            selected = (hexc.upper() == self.id_bg_color.upper())
            border = "2px solid #5B5BFF" if selected else "1px solid rgba(128,128,128,0.35)"
            # 浅色底用深色字，深色底用白字
            qc = QColor(hexc)
            luminance = 0.299 * qc.red() + 0.587 * qc.green() + 0.114 * qc.blue()
            txt = "#222222" if luminance > 150 else "#FFFFFF"
            btn.setStyleSheet(
                f"background:{hexc}; color:{txt}; border-radius:10px;"
                f" border:{border}; padding:2px;"
            )
        # 自定义色块用当前色
        self.id_custom_chip.setStyleSheet(
            f"background:{self.id_bg_color}; color:#FFFFFF; border-radius:10px;"
            f" border:1px dashed rgba(128,128,128,0.6); padding:2px;"
        )

    def _change_id_bg(self):
        log.info(f"点击证件照换背景 color={self.id_bg_color}")
        if self.base is None:
            QMessageBox.information(self, "提示", "请先打开一张证件照")
            return
        self.app.set_status("AI 识别人物、替换底色中…"); QApplication.processEvents()
        try:
            rgb = self.base.convert("RGB")
            mask = self._infer_subject_mask(rgb)
            # 收缩外圈原底色残留环并轻羽化，避免换底后出现毛边
            mask = self._shrink_mask(mask, px=1, feather=1.0)
            qc = QColor(self.id_bg_color)
            bg = Image.new("RGB", rgb.size, (qc.red(), qc.green(), qc.blue()))
            out = bg.copy()
            # 蒙版=255 的位置贴人物，背景区保留纯色底
            out.paste(rgb, mask)
            self.base = out.convert("RGBA")
            self._push_undo(); self._refresh()
            self.app.set_status("证件照背景已替换")
        except FileNotFoundError as e:
            QMessageBox.warning(self, "换背景失败", f"模型文件不存在:\n{e}")
        except Exception as e:
            log.exception("证件照换背景失败")
            QMessageBox.warning(self, "换背景失败", f"{e}")

    def _add_text_wm(self):
        log.info("点击添加文字水印")
        if self.base is None: return
        txt = self.twm_text.text().strip()
        if not txt:
            QMessageBox.information(self, "提示", "请输入文字内容")
            return
        wm = self._make_text_wm(txt)
        x = (self.base.width - wm.width) // 2
        y = (self.base.height - wm.height) // 2
        item = {"img": wm, "x": x, "y": y, "type": "text", "txt": txt}
        self.wm_items.append(item)
        self._sel_wm = item
        self._refresh()
        self.app.set_status("文字水印已添加")

    def _make_text_wm(self, txt):
        size = self.twm_size.value()
        alpha = int(self.twm_alpha.value() * 2.55)
        log.info(f"生成水印: txt={txt}, size={size}, alpha={alpha}, color={self.twm_color}")
        from PIL import ImageFont
        try: font = ImageFont.truetype("msyh.ttc", size)
        except: font = ImageFont.load_default()
        tmp = Image.new("RGBA", (10, 10), (0,0,0,0))
        d = ImageDraw.Draw(tmp)
        bbox = d.textbbox((0,0), txt, font=font)
        tw = bbox[2]-bbox[0] + 20
        th = bbox[3]-bbox[1] + 20
        layer = Image.new("RGBA", (tw, th), (0,0,0,0))
        d2 = ImageDraw.Draw(layer)
        rgb = self.twm_color.lstrip("#")
        r, g, b = int(rgb[0:2],16), int(rgb[2:4],16), int(rgb[4:6],16)
        d2.text((10-bbox[0], 10-bbox[1]), txt, fill=(r,g,b,alpha), font=font)
        return layer

    def _pick_twm_color(self):
        log.info("点击选文字水印颜色")
        from PySide6.QtWidgets import QColorDialog
        from PySide6.QtGui import QColor
        dlg = QColorDialog(QColor(self.twm_color), self)
        dlg.setWindowTitle("选择水印颜色")
        dlg.setOption(QColorDialog.DontUseNativeDialog, True)
        if dlg.exec() == QColorDialog.Accepted:
            c = dlg.currentColor()
            self.twm_color = c.name().upper()
            log.info(f"选择颜色: {self.twm_color}")
            self.twm_color_btn.setStyleSheet(f"background:{self.twm_color}; border-radius:10px; border:1px solid rgba(128,128,128,0.3);")
            if not self._sel_wm or self._sel_wm.get("type") != "text":
                for wm in reversed(self.wm_items):
                    if wm.get("type") == "text":
                        self._sel_wm = wm
                        break
            if self._sel_wm and self._sel_wm.get("type") == "text":
                self._update_sel_wm()
                log.info("已更新选中文字水印颜色")
        else:
            log.info("用户取消颜色选择")

    def _update_sel_wm(self):
        if not self._sel_wm: return
        old = self._sel_wm
        if old.get("type") == "text":
            wm = self._make_text_wm(old["txt"])
            old["img"] = wm
        elif old.get("type") == "image":
            # 重新应用透明度和缩放
            wm = Image.open(old["src"]).convert("RGBA")
            scale = self.iwm_scale.value() / 100.0
            wm = wm.resize((int(wm.width*scale), int(wm.height*scale)), Image.LANCZOS)
            alpha = self.iwm_alpha.value() / 100.0
            a = wm.split()[3].point(lambda p: int(p*alpha))
            wm.putalpha(a)
            old["img"] = wm
        self._refresh()

    def _del_selected_wm(self):
        log.info("删除选中水印")
        if self._sel_wm in self.wm_items:
            self.wm_items.remove(self._sel_wm)
        self._sel_wm = None
        self._refresh()

    def _pick_wm_img(self):
        log.info("点击选择水印图")
        path, _ = QFileDialog.getOpenFileName(self, "选择水印图", "", "图片 (*.png *.jpg *.jpeg)")
        if path:
            self._wm_img_path = path
            self.iwm_name.setText(os.path.basename(path))
            log.info(f"已选择水印图: {path}")
        else:
            log.info("用户取消选择水印图")

    def _add_img_wm(self):
        log.info("点击添加图片水印")
        if self.base is None:
            QMessageBox.information(self, "提示", "请先打开一张图片")
            return
        if not hasattr(self, '_wm_img_path'):
            QMessageBox.information(self, "提示", "请先选择水印图")
            return
        try:
            wm = Image.open(self._wm_img_path).convert("RGBA")
            log.info(f"水印图原始大小: {wm.size}")
            scale = self.iwm_scale.value() / 100.0
            wm = wm.resize((int(wm.width*scale), int(wm.height*scale)), Image.LANCZOS)
            alpha = self.iwm_alpha.value() / 100.0
            a = wm.split()[3].point(lambda p: int(p*alpha))
            wm.putalpha(a)
            x = (self.base.width - wm.width) // 2
            y = (self.base.height - wm.height) // 2
            item = {"img": wm, "x": x, "y": y, "type": "image", "src": self._wm_img_path}
            self.wm_items.append(item)
            self._sel_wm = item
            self._refresh()
            self.app.set_status("图片水印已添加")
            log.info("图片水印添加成功")
        except Exception as e:
            log.exception(f"图片水印错误: {e}")
            QMessageBox.warning(self, "图片水印", str(e))

    def _save(self):
        log.info("点击保存")
        if self.base is None: return
        default = os.path.basename(self.file_path) if self.file_path else "edited.png"
        path, _ = QFileDialog.getSaveFileName(self, "保存图片", default, "PNG (*.png);;JPEG (*.jpg)")
        if path:
            img = self.base.copy()
            for wm in self.wm_items:
                overlay = Image.new("RGBA", img.size, (0,0,0,0))
                overlay.paste(wm["img"], (wm["x"], wm["y"]), wm["img"])
                img = Image.alpha_composite(img, overlay)
            if path.lower().endswith(".jpg"):
                bg = Image.new("RGB", img.size, (255,255,255))
                bg.paste(img, mask=img.split()[3]); bg.save(path, quality=95)
            else:
                img.save(path)
            self.app.set_status(f"已保存: {path}")

    def _copy_clipboard(self):
        """把当前编辑结果（含水印）复制到系统剪贴板"""
        log.info("点击复制到剪贴板")
        if self.base is None:
            self.app.set_status("没有图片可复制")
            return
        try:
            img = self.base.copy()
            for wm in self.wm_items:
                overlay = Image.new("RGBA", img.size, (0,0,0,0))
                overlay.paste(wm["img"], (wm["x"], wm["y"]), wm["img"])
                img = Image.alpha_composite(img, overlay)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            pm = QPixmap()
            pm.loadFromData(buf.getvalue(), "PNG")
            if pm.isNull():
                self.app.set_status("复制失败：图片转换异常")
                return
            QApplication.clipboard().setPixmap(pm)
            self.app.set_status("已复制到剪贴板")
        except Exception as e:
            self.app.set_status(f"复制失败: {e}")


PHOTO_SIZES = {
    "1寸（25×35mm）": (295, 413),
    "2寸（35×49mm）": (413, 579),
    "小2寸（35×45mm）": (413, 531),
    "大1寸（33×48mm）": (390, 567),
}

class BatchPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self._build_ui()

    def _build_ui(self):
        lay = QHBoxLayout(self); lay.setContentsMargins(20, 20, 20, 20); lay.setSpacing(16)

        # 左栏
        left = QVBoxLayout(); left.setSpacing(12)
        lay.addLayout(left, 1)

        # 源文件夹
        g_src = QGroupBox("源文件夹")
        sl = QVBoxLayout(g_src)
        row = QHBoxLayout()
        self.src_edit = QLineEdit(); self.src_edit.setPlaceholderText("选择包含图片的文件夹")
        row.addWidget(self.src_edit)
        b_pick = QPushButton("浏览"); b_pick.clicked.connect(self._pick_src)
        row.addWidget(b_pick)
        sl.addLayout(row)
        self.src_count = QLabel("尚未选择")
        self.src_count.setObjectName("SecondaryLabel")
        sl.addWidget(self.src_count)
        left.addWidget(g_src)

        # 任务类型
        g_task = QGroupBox("任务类型")
        tl = QVBoxLayout(g_task)
        self.task_group = QButtonGroup(self)
        self.tasks = ["批量压缩图片（体积）", "批量修改尺寸", "批量转换格式", "批量生成证件照"]
        for i, t in enumerate(self.tasks):
            rb = QRadioButton(t)
            if i == 0: rb.setChecked(True)
            self.task_group.addButton(rb, i)
            rb.toggled.connect(self._on_task_change)
            tl.addWidget(rb)
        left.addWidget(g_task)

        # 参数区
        self.g_param = QGroupBox("任务参数")
        self.pl = QVBoxLayout(self.g_param)
        self._build_compress_params()
        left.addWidget(self.g_param)
        left.addStretch()

        # 右栏
        right = QVBoxLayout(); right.setSpacing(12)
        lay.addLayout(right, 1)

        g_out = QGroupBox("输出设置")
        ol = QVBoxLayout(g_out)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("输出目录:"))
        self.out_edit = QLineEdit()
        row2.addWidget(self.out_edit)
        b_out = QPushButton("浏览"); b_out.clicked.connect(self._pick_out)
        row2.addWidget(b_out)
        ol.addLayout(row2)
        self.overwrite_chk = QCheckBox("覆盖已存在的文件")
        ol.addWidget(self.overwrite_chk)
        self.subdir_chk = QCheckBox("保留子目录结构"); self.subdir_chk.setChecked(True)
        ol.addWidget(self.subdir_chk)
        right.addWidget(g_out)

        b_run = AnimatedButton("开始批处理"); b_run.setObjectName("TopBtnPrimary")
        b_run.clicked.connect(self._run_batch)
        right.addWidget(b_run)

        from PySide6.QtWidgets import QProgressBar, QTextEdit
        self.progress = QProgressBar()
        right.addWidget(self.progress)
        self.log_text = QTextEdit(); self.log_text.setReadOnly(True)
        self.log_text.setObjectName("LogText")
        right.addWidget(self.log_text, 1)

    def _clear_param(self):
        while self.pl.count():
            item = self.pl.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    sub = item.layout().takeAt(0)
                    if sub.widget(): sub.widget().deleteLater()

    def _build_compress_params(self):
        self._clear_param()
        row = QHBoxLayout()
        row.addWidget(QLabel("JPEG质量:"))
        self.quality_slider = QSlider(Qt.Horizontal); self.quality_slider.setRange(10, 100); self.quality_slider.setValue(85)
        row.addWidget(self.quality_slider)
        self.quality_label = QLabel("85%")
        row.addWidget(self.quality_label)
        self.quality_slider.valueChanged.connect(lambda v: self.quality_label.setText(f"{v}%"))
        self.pl.addLayout(row)
        row2 = QHBoxLayout()
        self.resize_chk = QCheckBox("限制最大尺寸")
        row2.addWidget(self.resize_chk)
        self.max_dim = QSpinBox(); self.max_dim.setRange(200, 10000); self.max_dim.setValue(1920)
        self.max_dim.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        row2.addWidget(self.max_dim)
        px_lb = QLabel("px"); px_lb.setObjectName("HintLabel")
        row2.addWidget(px_lb)
        self.pl.addLayout(row2)

    def _build_resize_params(self):
        self._clear_param()
        row = QHBoxLayout()
        row.addWidget(QLabel("宽度:"))
        self.rw = QSpinBox(); self.rw.setRange(10, 10000); self.rw.setValue(800)
        self.rw.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        row.addWidget(self.rw)
        row.addWidget(QLabel("高度:"))
        self.rh = QSpinBox(); self.rh.setRange(10, 10000); self.rh.setValue(600)
        self.rh.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        row.addWidget(self.rh)
        self.pl.addLayout(row)
        self.keep_ratio = QCheckBox("保持宽高比（较长边适配）"); self.keep_ratio.setChecked(True)
        self.pl.addWidget(self.keep_ratio)

    def _build_convert_params(self):
        self._clear_param()
        row = QHBoxLayout()
        row.addWidget(QLabel("目标格式:"))
        self.fmt_combo = QComboBox()
        self.fmt_combo.addItems(["JPEG (.jpg)", "PNG (.png)", "WebP (.webp)", "BMP (.bmp)"])
        row.addWidget(self.fmt_combo)
        self.pl.addLayout(row)
        self.del_orig = QCheckBox("转换后删除原文件（谨慎！）")
        self.pl.addWidget(self.del_orig)

    def _build_idphoto_params(self):
        self._clear_param()
        row = QHBoxLayout()
        row.addWidget(QLabel("尺寸:"))
        self.size_combo = QComboBox()
        for name in PHOTO_SIZES:
            self.size_combo.addItems([name])
        row.addWidget(self.size_combo)
        self.pl.addLayout(row)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("背景色:"))
        self.bg_combo = QComboBox(); self.bg_combo.addItems(["白色", "蓝色", "红色"])
        row2.addWidget(self.bg_combo)
        self.pl.addLayout(row2)
        self.auto_crop = QCheckBox("自动裁剪为证件照比例"); self.auto_crop.setChecked(True)
        self.pl.addWidget(self.auto_crop)

    def _on_task_change(self):
        idx = self.task_group.checkedId()
        if idx == 0: self._build_compress_params()
        elif idx == 1: self._build_resize_params()
        elif idx == 2: self._build_convert_params()
        elif idx == 3: self._build_idphoto_params()

    def _pick_src(self):
        d = QFileDialog.getExistingDirectory(self, "选择源文件夹")
        if d:
            self.src_edit.setText(d)
            exts = ('.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff', '.gif')
            count = 0
            for _, _, files in os.walk(d):
                for f in files:
                    if f.lower().endswith(exts): count += 1
            self.src_count.setText(f"找到 {count} 个图片文件")
            self.app.set_status(f"源文件夹: {d} ({count} 个图片)")

    def _pick_out(self):
        d = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if d: self.out_edit.setText(d)

    def _log(self, msg):
        self.log_text.append(msg)

    def _run_batch(self):
        src = self.src_edit.text().strip()
        out = self.out_edit.text().strip()
        idx = self.task_group.checkedId()
        if not src or not os.path.isdir(src):
            QMessageBox.warning(self, "提示", "请选择有效的源文件夹"); return
        if not out:
            QMessageBox.warning(self, "提示", "请选择输出目录"); return

        exts = ('.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff')
        files = []
        keep_subdir = self.subdir_chk.isChecked()
        for root_dir, _, filenames in os.walk(src):
            for fn in filenames:
                if fn.lower().endswith(exts):
                    fp = os.path.join(root_dir, fn)
                    if keep_subdir:
                        rel = os.path.relpath(root_dir, src)
                        td = os.path.join(out, rel) if rel != '.' else out
                    else:
                        td = out
                    files.append((fp, td, fn))
        if not files:
            QMessageBox.information(self, "提示", "没有找到图片文件"); return

        self.log_text.clear()
        self.progress.setMaximum(len(files))
        self.progress.setValue(0)
        self.app.set_status("正在批处理...")
        success = 0; errors = []

        for i, (fp, td, fn) in enumerate(files):
            try:
                os.makedirs(td, exist_ok=True)
                out_path = os.path.join(td, fn)
                if idx == 0:  # 压缩
                    quality = self.quality_slider.value()
                    max_dim = self.max_dim.value() if self.resize_chk.isChecked() else None
                    img = Image.open(fp)
                    if img.mode in ('RGBA', 'P'):
                        bg = Image.new('RGB', img.size, (255,255,255))
                        bg.paste(img, mask=img.split()[3] if img.mode=='RGBA' else None)
                        img = bg
                    elif img.mode != 'RGB': img = img.convert('RGB')
                    if max_dim: img.thumbnail((max_dim, max_dim), Image.LANCZOS)
                    if os.path.splitext(fn)[1].lower() not in ('.jpg', '.jpeg'):
                        out_path = os.path.join(td, os.path.splitext(fn)[0] + '.jpg')
                    img.save(out_path, 'JPEG', quality=quality, optimize=True)
                    self._log(f"✓ 压缩: {fn}")
                elif idx == 1:  # 改尺寸
                    w, h = self.rw.value(), self.rh.value()
                    img = Image.open(fp)
                    if self.keep_ratio.isChecked():
                        img.thumbnail((w, h), Image.LANCZOS)
                    else:
                        img = img.resize((w, h), Image.LANCZOS)
                    img.save(out_path)
                    self._log(f"✓ 改尺寸: {fn}")
                elif idx == 2:  # 转换格式
                    fmts = {"JPEG (.jpg)": ".jpg", "PNG (.png)": ".png", "WebP (.webp)": ".webp", "BMP (.bmp)": ".bmp"}
                    new_ext = fmts[self.fmt_combo.currentText()]
                    name_no_ext = os.path.splitext(fn)[0]
                    out_path = os.path.join(td, f"{name_no_ext}{new_ext}")
                    img = Image.open(fp)
                    if new_ext == '.jpg' and img.mode in ('RGBA', 'P'):
                        bg = Image.new('RGB', img.size, (255,255,255))
                        bg.paste(img, mask=img.split()[3] if img.mode=='RGBA' else None)
                        img = bg
                    elif img.mode != 'RGB' and new_ext == '.jpg':
                        img = img.convert('RGB')
                    img.save(out_path)
                    if self.del_orig.isChecked() and out_path != fp:
                        os.remove(fp)
                    self._log(f"✓ 转换: {fn} → {name_no_ext}{new_ext}")
                elif idx == 3:  # 证件照
                    size_name = self.size_combo.currentText()
                    target = PHOTO_SIZES.get(size_name, (295, 413))
                    bg_map = {"白色": (255,255,255), "蓝色": (0,128,255), "红色": (255,0,0)}
                    bg_rgb = bg_map[self.bg_combo.currentText()]
                    img = Image.open(fp).convert('RGB')
                    if self.auto_crop.isChecked():
                        cw, ch = img.size
                        l = int(cw*0.15); t = int(ch*0.15); r = int(cw*0.85); b = int(ch*0.85)
                        img = img.crop((l,t,r,b))
                    img = img.resize(target, Image.LANCZOS)
                    canvas = Image.new('RGB', target, bg_rgb)
                    canvas.paste(img, (0,0))
                    name_no_ext = os.path.splitext(fn)[0]
                    out_path = os.path.join(td, f"{name_no_ext}_证件照.jpg")
                    canvas.save(out_path, 'JPEG', quality=92)
                    self._log(f"✓ 证件照: {fn}")
                success += 1
            except Exception as e:
                errors.append(f"{fn}: {e}")
                self._log(f"✗ 失败: {fn} - {e}")
            self.progress.setValue(i+1)

        self.app.set_status(f"批处理完成: {success}/{len(files)} 成功")
        self._log(f"\n完成: {success}/{len(files)} 成功")
        QMessageBox.information(self, "批处理结果", f"总计: {len(files)}\n成功: {success}\n失败: {len(errors)}")

# ─── 主窗口 ───
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"拾光 {APP_VERSION}")
        self.resize(1280, 820)
        self.move(100, 100)
        self.setWindowIcon(QIcon(_app_icon_path()))
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._dragging = False
        self._corner_radius = 12

        central = QWidget(); self.setCentralWidget(central)
        central.setAutoFillBackground(False)
        central.setAttribute(Qt.WA_TranslucentBackground)
        main_lay = QVBoxLayout(central); main_lay.setContentsMargins(0, 0, 0, 0); main_lay.setSpacing(0)

        # ── 玻璃背景层（大椭圆光晕）──
        self._bg = GlassBackground(central)
        self._bg.lower()
        self._current_theme = "dark"

        # ── 自定义标题栏 ──
        title_bar = QFrame(); title_bar.setObjectName("TitleBar")
        title_bar.setAttribute(Qt.WA_TranslucentBackground)
        title_bar.setAutoFillBackground(False)
        title_lay = QHBoxLayout(title_bar); title_lay.setContentsMargins(0, 0, 0, 0); title_lay.setSpacing(0)
        title_label = QLabel(f"拾光 {APP_VERSION}"); title_label.setObjectName("TitleLabel")
        title_lay.addWidget(title_label)
        title_lay.addStretch()
        self._theme_btn = QPushButton("\u263E"); self._theme_btn.setObjectName("WinBtn")
        self._theme_btn.setToolTip("切换深色/浅色主题")
        self._theme_btn.setCursor(Qt.PointingHandCursor)
        self._theme_btn.setFocusPolicy(Qt.NoFocus)
        self._theme_btn.clicked.connect(self._toggle_theme)
        title_lay.addWidget(self._theme_btn)
        btn_min = QPushButton("\u2014"); btn_min.setObjectName("WinBtn")
        btn_max = QPushButton("\u25a1"); btn_max.setObjectName("WinBtn")
        btn_close = QPushButton("\u2715"); btn_close.setObjectName("WinBtn")
        btn_close.setObjectName("WinBtnClose")
        btn_min.clicked.connect(self.showMinimized)
        btn_max.clicked.connect(self._toggle_max)
        btn_close.clicked.connect(self.close)
        for b in (btn_min, btn_max, btn_close):
            b.setCursor(Qt.PointingHandCursor)
            b.setFocusPolicy(Qt.NoFocus)
            title_lay.addWidget(b)
        self._btn_max = btn_max
        main_lay.addWidget(title_bar)

        # ── 主体区域 ──
        body = QWidget()
        body.setAttribute(Qt.WA_TranslucentBackground)
        body.setAutoFillBackground(False)
        root = QHBoxLayout(body); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)

        # ── 侧边栏 ──
        side = QFrame(); side.setObjectName("SideBar"); side.setFixedWidth(160)
        side_lay = QVBoxLayout(side); side_lay.setContentsMargins(8, 16, 8, 8); side_lay.setSpacing(4)

        # 侧边栏投影
        self._side_shadow = QGraphicsDropShadowEffect()
        self._side_shadow.setBlurRadius(30)
        self._side_shadow.setColor(QColor(0, 0, 0, 120))
        self._side_shadow.setOffset(3, 0)
        side.setGraphicsEffect(self._side_shadow)

        self.nav_btns = []
        nav_items = [
            ("\u25C9  浏览", "浏览"), ("\u25A4  拼图", "拼图"),
            ("\u25C8  压缩", "压缩"), ("\u270E  编辑", "编辑"),
            ("\u2261  批处理", "批处理")
        ]
        for i, (label, name) in enumerate(nav_items):
            b = AnimatedButton(label); b.setObjectName("SideBtn"); b.setCheckable(True)
            b.clicked.connect(lambda checked, idx=i: self.switch_page(idx))
            side_lay.addWidget(b); self.nav_btns.append(b)
        b_about = AnimatedButton("\u2139  关于"); b_about.setObjectName("SideBtn")
        b_about.clicked.connect(self._show_about)
        side_lay.addWidget(b_about)
        side_lay.addStretch()

        # ── 右侧内容区 ──
        right = QWidget()
        right_lay = QVBoxLayout(right); right_lay.setContentsMargins(0, 0, 0, 0); right_lay.setSpacing(0)
        self.stack = QStackedWidget()
        self.stack.addWidget(ViewerPage(self))
        self.stack.addWidget(CollagePage(self))
        self.stack.addWidget(CompressPage(self))
        self.stack.addWidget(EditPage(self))
        self.stack.addWidget(BatchPage(self))
        right_lay.addWidget(self.stack)
        self.status = QStatusBar(); self.statusBar().showMessage("就绪")
        self.setStatusBar(self.status)
        root.addWidget(side)
        root.addWidget(right, stretch=1)
        main_lay.addWidget(body, stretch=1)
        self.switch_page(0)
        # 版本更新弹窗
        import json, os
        ver_file = os.path.join(_data_dir(), ".shiguang_ver")
        cur_ver = APP_VERSION
        old_ver = ""
        try:
            if os.path.exists(ver_file):
                old_ver = open(ver_file).read().strip()
        except: pass
        if old_ver != cur_ver:
            try: open(ver_file, "w").write(cur_ver)
            except: pass
            QMessageBox.information(self, "拾光 更新",
                "<h3>拾光 5.2 更新内容</h3>"
                "<p>• 新增「证件照一键换背景」：白 / 标准蓝 / 红底互转，也可取自定义颜色</p>"
                "<p>• AI 分割模型升级为 BiRefNet-Portrait，人物发丝与身体边缘更干净"
                "（AI 去背景与证件照换底共用）</p>"
                "<p>• 修复证件照换底后边缘残留原底色毛边的问题</p>"
                "<p>• 加深状态栏提示文字，深色主题下更易辨认</p>"
                "<p>• 主题切换精简为深 / 浅双主题，移除多余皮肤</p>")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, '_bg'):
            self._bg.setGeometry(self.centralWidget().rect())
            self._bg.update()
        from PySide6.QtGui import QRegion, QPainterPath
        r = self._corner_radius
        w, h = self.width(), self.height()
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, w, h), r, r)
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def paintEvent(self, event):
        super().paintEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.position().y() <= 40:
            self._dragging = True
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._dragging:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._dragging = False

    def _toggle_max(self):
        if self.isMaximized():
            self.showNormal()
            self._btn_max.setText("\u25a1")
        else:
            self.showMaximized()
            self._btn_max.setText("\u29c9")

    def switch_page(self, idx):
        self.stack.setCurrentIndex(idx)
        for i, b in enumerate(self.nav_btns):
            b.setChecked(i == idx)

    def _show_about(self):
        QMessageBox.about(self, "关于 拾光",
            "<h3>拾光 " + APP_VERSION + "</h3>"
            "<p>轻量级图片查看与编辑工具</p>"
            "<p>浏览 · 拼图 · 压缩 · 编辑 · 批处理</p>"
            "<hr>"
            "<p>基于 Python + PySide6 (Qt) + Pillow 开发</p>"
            "<p>本软件为自由软件，个人可免费使用、传播</p>"
            "<p>请勿擅自修改后冒充原版分发</p>"
            "<p>反馈: shiguang.app@qq.com</p>"
            "<p>© 2026 拾光</p>")

    def set_status(self, msg):
        self.statusBar().showMessage(msg)

    def _toggle_theme(self):
        self._current_theme = "light" if self._current_theme == "dark" else "dark"
        self._apply_theme(self._current_theme)

    def _apply_theme(self, theme):
        qss = build_qss(theme)
        app = QApplication.instance()
        app._current_theme = theme
        app.setStyleSheet(qss)

        # 更新背景
        if hasattr(self, '_bg'):
            self._bg.set_theme(theme)
            self._bg.update()

        # 更新调色板
        if theme == "dark":
            pal = QPalette()
            pal.setColor(QPalette.Window, QColor("#0a0a1a"))
            pal.setColor(QPalette.WindowText, QColor(255, 255, 255, 200))
            pal.setColor(QPalette.Base, QColor("#0f0f2a"))
            pal.setColor(QPalette.AlternateBase, QColor("#15152e"))
            pal.setColor(QPalette.Text, QColor(255, 255, 255, 210))
            pal.setColor(QPalette.Button, QColor("#1a1a3a"))
            pal.setColor(QPalette.ButtonText, QColor(255, 255, 255, 200))
            pal.setColor(QPalette.Highlight, QColor(111, 111, 255))
            pal.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        else:
            pal = QPalette()
            pal.setColor(QPalette.Window, QColor("#f4f5fa"))
            pal.setColor(QPalette.WindowText, QColor(0, 0, 0, 180))
            pal.setColor(QPalette.Base, QColor("#ffffff"))
            pal.setColor(QPalette.AlternateBase, QColor("#f0f1f6"))
            pal.setColor(QPalette.Text, QColor(0, 0, 0, 200))
            pal.setColor(QPalette.Button, QColor("#ffffff"))
            pal.setColor(QPalette.ButtonText, QColor(0, 0, 0, 180))
            pal.setColor(QPalette.Highlight, QColor(111, 111, 255))
            pal.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        QApplication.instance().setPalette(pal)

        # 更新切换按钮图标
        self._theme_btn.setText("\u2600" if theme == "light" else "\u263E")

        # 更新侧边栏阴影
        if hasattr(self, '_side_shadow'):
            self._side_shadow.setColor(QColor(0, 0, 0, 60 if theme == "light" else 120))

        self.update()
        self._refresh_inline_styles(theme)

    def _refresh_inline_styles(self, theme):
        edit_page = self.stack.widget(3)
        if not edit_page or not hasattr(edit_page, 'color_btn'):
            return
        edit_page.color_btn.setStyleSheet(
            f"background:{edit_page.draw_color}; border-radius:10px; border:1px solid rgba(128,128,128,0.3);")
        edit_page.twm_color_btn.setStyleSheet(
            f"background:{edit_page.twm_color}; border-radius:10px; border:1px solid rgba(128,128,128,0.3);")
        for w in [edit_page, edit_page.scroll]:
            w.style().unpolish(w)
            w.style().polish(w)

if __name__ == "__main__":
    log.info("=" * 56)
    log.info(f"拾光 {APP_VERSION} 启动")
    log.info(f"打包运行: {getattr(sys, 'frozen', False)}   可执行: {sys.executable}")
    log.info(f"Python: {sys.version.split()[0]}   平台: {sys.platform}")
    log.info(f"日志目录: {LOG_DIR}")
    try:
        _bd = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        _biref = os.path.join(_bd, "models", "birefnet", "model.onnx")
        _rmbg = os.path.join(_bd, "models", "rmbg", "model.onnx")
        _u2 = os.path.join(_bd, "models", "u2net", "u2net.onnx")
        if os.path.exists(_biref):
            log.info(f"抠图模型(BiRefNet-Portrait): {_biref}  存在=True")
        elif os.path.exists(_rmbg):
            log.info(f"抠图模型(回退RMBG-1.4): {_rmbg}  存在=True")
        elif os.path.exists(_u2):
            log.info(f"抠图模型(回退u2net): {_u2}  存在=True")
        else:
            log.info(f"抠图模型: 未找到 BiRefNet/RMBG/u2net（{_biref} / {_rmbg} / {_u2}）")
    except Exception as _e:
        log.info(f"抠图模型检查失败: {_e}")

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app._current_theme = "dark"
    font = QFont("Microsoft YaHei UI", 9)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)
    app.setStyleSheet(build_qss("dark"))

    dark_palette = app.palette()
    dark_palette.setColor(QPalette.Window, QColor("#0a0a1a"))
    dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255, 200))
    dark_palette.setColor(QPalette.Base, QColor("#0f0f2a"))
    dark_palette.setColor(QPalette.AlternateBase, QColor("#15152e"))
    dark_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Text, QColor(255, 255, 255, 210))
    dark_palette.setColor(QPalette.Button, QColor("#1a1a3a"))
    dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255, 200))
    dark_palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Highlight, QColor(111, 111, 255))
    dark_palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(dark_palette)

    win = MainWindow()
    win.show()
    sys.exit(app.exec())




