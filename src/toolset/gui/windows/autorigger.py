from __future__ import annotations

import math
import os
import subprocess
import sys
import tempfile

from typing import TYPE_CHECKING

from qtpy.QtCore import QProcess, Qt, QTimer
from qtpy.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QOpenGLWidget,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from qtpy.QtGui import QCloseEvent, QMouseEvent, QWheelEvent


RUNNER_SCRIPT = """
from __future__ import annotations

import argparse
import os
import sys
import traceback


def _import_writer():
    try:
        from src.core.mdl_writer import MDLBinaryWriter
        return MDLBinaryWriter
    except Exception:
        from src.core.mdl_porter import MDLBinaryWriter
        return MDLBinaryWriter


def main() -> int:
    parser = argparse.ArgumentParser(description=\"GhostRigger AutoRigger runner\")
    parser.add_argument(\"--repo\", required=True)
    parser.add_argument(\"--input\", required=True)
    parser.add_argument(\"--output\", required=True)
    parser.add_argument(\"--mode\", choices=[\"auto\", \"template\"], default=\"auto\")
    parser.add_argument(\"--template\", default=\"humanoid\")
    parser.add_argument(\"--template-model\", default=\"\")
    parser.add_argument(\"--scale-to-target\", action=\"store_true\")
    parser.add_argument(\"--supermodel\", default=\"\")
    args = parser.parse_args()

    repo = os.path.abspath(args.repo)
    src_dir = os.path.join(repo, \"src\")
    if repo not in sys.path:
        sys.path.insert(0, repo)
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    from src.autorig.auto_rigger import AutoRigger
    from src.converters.mesh_converter import FBXImporter, OBJImporter

    MDLBinaryWriter = _import_writer()

    input_path = os.path.abspath(args.input)
    output_path = os.path.abspath(args.output)

    ext = os.path.splitext(input_path)[1].lower()
    if ext == \".obj\":
        model = OBJImporter().import_file(input_path)
    elif ext == \".fbx\":
        model = FBXImporter().import_file(input_path)
    else:
        raise ValueError(f\"Unsupported input extension: {ext}\")

    if args.supermodel:
        model.supermodel = args.supermodel

    rigger = AutoRigger()
    if args.mode == \"template\":
        if not args.template_model:
            raise ValueError(\"Template mode requires --template-model\")
        from src.autorig.auto_rigger import RigExtractor
        from src.core.mdl_parser import MDLBinaryParser

        template_mdl = os.path.abspath(args.template_model)
        template_mdx = os.path.splitext(template_mdl)[0] + \".mdx\"
        template_model = MDLBinaryParser.from_files(template_mdl, template_mdx).parse()
        template = RigExtractor().extract(template_model)
        model = rigger.rig_from_template(model, template, scale_to_target=args.scale_to_target)
    else:
        model = rigger.auto_rig(model, template=args.template)

    writer = MDLBinaryWriter()
    if hasattr(writer, \"write_files\"):
        writer.write_files(model, output_path)
    else:
        result = writer.write(model)
        if not isinstance(result, tuple) or len(result) != 2:
            raise RuntimeError(\"MDLBinaryWriter.write did not return (mdl_bytes, mdx_bytes)\")
        mdl_bytes, mdx_bytes = result
        mdx_path = os.path.splitext(output_path)[0] + \".mdx\"
        with open(output_path, \"wb\") as mdl_file:
            mdl_file.write(mdl_bytes)
        with open(mdx_path, \"wb\") as mdx_file:
            mdx_file.write(mdx_bytes)

    print(f\"AutoRigger complete: {output_path}\")
    print(f\"MDX path: {os.path.splitext(output_path)[0] + '.mdx'}\")
    return 0


if __name__ == \"__main__\":
    try:
        raise SystemExit(main())
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
""".strip()

# ---------------------------------------------------------------------------
# OBJ / FBX live 3D preview — GLSL 330 core, VBO-based, no extra deps
# ---------------------------------------------------------------------------
_OBJ_VSHADER = """
#version 330 core
layout(location = 0) in vec3 aPos;
layout(location = 1) in vec3 aNormal;
uniform mat4 uMVP;
uniform mat4 uModel;
out vec3 vNormal;
void main() {
    gl_Position = uMVP * vec4(aPos, 1.0);
    vNormal = normalize(mat3(uModel) * aNormal);
}
""".strip()

_OBJ_FSHADER = """
#version 330 core
in vec3 vNormal;
out vec4 fragColor;
uniform vec3 uLightDir;
uniform vec3 uBaseColor;
void main() {
    float diff = max(dot(vNormal, normalize(uLightDir)), 0.15);
    fragColor = vec4(uBaseColor * diff, 1.0);
}
""".strip()


class OBJPreviewWidget(QOpenGLWidget):
    """Interactive 3D preview widget for OBJ (and FBX placeholder) files.

    Controls:
      - Left-drag: orbit
      - Scroll: zoom
      - Middle-drag / right-drag: pan
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setMinimumSize(280, 280)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Geometry
        self._vao: int = 0
        self._vbo: int = 0
        self._tri_count: int = 0
        self._pending_load: str | None = None  # path to load once GL is ready

        # Camera (orbit)
        self._yaw: float = 0.5
        self._pitch: float = 0.4
        self._dist: float = 5.0
        self._cx: float = 0.0
        self._cy: float = 0.0
        self._cz: float = 0.0

        # Mouse
        self._mouse_last: tuple[int, int] = (0, 0)
        self._mouse_buttons: set[int] = set()

        # GL objects
        self._prog: int = 0

        # Status
        self._status: str = "No model loaded\nSelect an OBJ/FBX input file"
        self._gl_ready: bool = False

        QTimer.singleShot(33, self._loopRepaint)

    # ------------------------------------------------------------------
    def _loopRepaint(self):
        if self.isVisible():
            self.update()
        QTimer.singleShot(33, self._loopRepaint)

    # ------------------------------------------------------------------
    def loadFile(self, path: str):
        """Load OBJ for live preview (FBX shown as placeholder)."""
        if not path:
            self._status = "No model loaded"
            self._tri_count = 0
            self.update()
            return
        if path.lower().endswith(".fbx"):
            self._status = f"FBX: {os.path.basename(path)}\n3D preview available after rigging"
            self._tri_count = 0
            self.update()
            return
        if not os.path.isfile(path):
            self._status = f"File not found:\n{os.path.basename(path)}"
            self._tri_count = 0
            self.update()
            return
        if self._gl_ready:
            self._uploadOBJ(path)
        else:
            self._pending_load = path

    # ------------------------------------------------------------------
    def _parseOBJ(self, path: str) -> tuple[list[tuple[float, float, float]], list[tuple[int, int, int]]]:
        verts: list[tuple[float, float, float]] = []
        tris: list[tuple[int, int, int]] = []
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                for raw in fh:
                    line = raw.strip()
                    if line.startswith("v "):
                        p = line.split()
                        verts.append((float(p[1]), float(p[2]), float(p[3])))
                    elif line.startswith("f "):
                        p = line.split()[1:]
                        idx = [int(t.split("/")[0]) - 1 for t in p]
                        for i in range(1, len(idx) - 1):
                            tris.append((idx[0], idx[i], idx[i + 1]))
        except Exception as exc:
            self._status = f"Parse error: {exc}"
        return verts, tris

    # ------------------------------------------------------------------
    def _uploadOBJ(self, path: str):
        from OpenGL.GL import (
            GL_ARRAY_BUFFER,
            GL_FLOAT,
            GL_STATIC_DRAW,
            glBindBuffer,
            glBindVertexArray,
            glBufferData,
            glEnableVertexAttribArray,
            glVertexAttribPointer,
        )
        import ctypes
        import array as _array

        verts, tris = self._parseOBJ(path)
        if not verts or not tris:
            self._status = f"Empty OBJ: {os.path.basename(path)}"
            self._tri_count = 0
            self.update()
            return

        # Bounding box → camera
        xs = [v[0] for v in verts]
        ys = [v[1] for v in verts]
        zs = [v[2] for v in verts]
        self._cx = (min(xs) + max(xs)) / 2
        self._cy = (min(ys) + max(ys)) / 2
        self._cz = (min(zs) + max(zs)) / 2
        span = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
        self._dist = max(span * 1.8, 0.1)

        # Build interleaved (pos.xyz, normal.xyz) per triangle vertex
        data: list[float] = []
        for tri in tris:
            v0, v1, v2 = verts[tri[0]], verts[tri[1]], verts[tri[2]]
            ax, ay, az = v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2]
            bx, by, bz = v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2]
            nx, ny, nz = ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx
            length = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
            nx, ny, nz = nx / length, ny / length, nz / length
            for vx, vy, vz in (v0, v1, v2):
                data.extend([vx, vy, vz, nx, ny, nz])

        raw_bytes = _array.array("f", data).tobytes()

        glBindVertexArray(self._vao)
        glBindBuffer(GL_ARRAY_BUFFER, self._vbo)
        glBufferData(GL_ARRAY_BUFFER, len(raw_bytes), raw_bytes, GL_STATIC_DRAW)
        stride = 6 * 4  # 6 floats × 4 bytes
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, False, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, False, stride, ctypes.c_void_p(12))
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        self._tri_count = len(tris)
        self._status = f"{os.path.basename(path)}\n{len(verts)} verts · {len(tris)} tris"
        self.update()

    # ------------------------------------------------------------------
    def _compileShader(self, src: str, shader_type: int) -> int:
        from OpenGL.GL import GL_COMPILE_STATUS, glCompileShader, glCreateShader, glGetShaderiv, glShaderSource
        sh = glCreateShader(shader_type)
        glShaderSource(sh, src)
        glCompileShader(sh)
        if not glGetShaderiv(sh, GL_COMPILE_STATUS):
            from OpenGL.GL import glGetShaderInfoLog
            raise RuntimeError(f"Shader compile error: {glGetShaderInfoLog(sh)}")
        return sh

    def _buildProgram(self) -> int:
        from OpenGL.GL import (
            GL_FRAGMENT_SHADER,
            GL_LINK_STATUS,
            GL_VERTEX_SHADER,
            glAttachShader,
            glCreateProgram,
            glGetProgramiv,
            glLinkProgram,
        )
        prog = glCreateProgram()
        vs = self._compileShader(_OBJ_VSHADER, GL_VERTEX_SHADER)
        fs = self._compileShader(_OBJ_FSHADER, GL_FRAGMENT_SHADER)
        glAttachShader(prog, vs)
        glAttachShader(prog, fs)
        glLinkProgram(prog)
        if not glGetProgramiv(prog, GL_LINK_STATUS):
            from OpenGL.GL import glGetProgramInfoLog
            raise RuntimeError(f"Program link error: {glGetProgramInfoLog(prog)}")
        return int(prog)

    # ------------------------------------------------------------------
    def initializeGL(self):
        from OpenGL.GL import (
            GL_DEPTH_TEST,
            glClearColor,
            glEnable,
            glGenBuffers,
            glGenVertexArrays,
        )
        glClearColor(0.12, 0.12, 0.14, 1.0)
        glEnable(GL_DEPTH_TEST)
        self._vao = int(glGenVertexArrays(1))
        self._vbo = int(glGenBuffers(1))
        try:
            self._prog = self._buildProgram()
        except Exception:
            self._prog = 0
        self._gl_ready = True
        if self._pending_load:
            self._uploadOBJ(self._pending_load)
            self._pending_load = None

    def resizeGL(self, w: int, h: int):
        from OpenGL.GL import glViewport
        glViewport(0, 0, w, max(h, 1))

    def paintGL(self):
        import array as _array

        from OpenGL.GL import (
            GL_COLOR_BUFFER_BIT,
            GL_DEPTH_BUFFER_BIT,
            GL_TRIANGLES,
            glBindVertexArray,
            glClear,
            glDrawArrays,
            glGetUniformLocation,
            glUniform3f,
            glUniformMatrix4fv,
            glUseProgram,
        )
        import glm

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if not self._prog or not self._tri_count:
            self._paintStatus()
            return

        w, h = max(self.width(), 1), max(self.height(), 1)

        eye = glm.vec3(
            self._cx + self._dist * math.cos(self._pitch) * math.sin(self._yaw),
            self._cy + self._dist * math.cos(self._pitch) * math.cos(self._yaw),
            self._cz + self._dist * math.sin(self._pitch),
        )
        center = glm.vec3(self._cx, self._cy, self._cz)
        up = glm.vec3(0, 1, 0) if abs(self._pitch) > 1.47 else glm.vec3(0, 0, 1)

        view = glm.lookAt(eye, center, up)
        proj = glm.perspective(glm.radians(60.0), w / h, 0.05, 10000.0)
        mvp = proj * view

        # glm is column-major; supply as flat float array, transpose=False
        mvp_arr = _array.array("f", [mvp[col][row] for col in range(4) for row in range(4)])
        id_arr = _array.array("f", [1, 0, 0, 0,  0, 1, 0, 0,  0, 0, 1, 0,  0, 0, 0, 1])

        glUseProgram(self._prog)
        glUniformMatrix4fv(glGetUniformLocation(self._prog, "uMVP"), 1, False, mvp_arr)
        glUniformMatrix4fv(glGetUniformLocation(self._prog, "uModel"), 1, False, id_arr)
        glUniform3f(glGetUniformLocation(self._prog, "uLightDir"), 0.7, 0.5, 1.0)
        glUniform3f(glGetUniformLocation(self._prog, "uBaseColor"), 0.55, 0.75, 0.95)

        glBindVertexArray(self._vao)
        glDrawArrays(GL_TRIANGLES, 0, self._tri_count * 3)
        glBindVertexArray(0)
        glUseProgram(0)

        self._paintStatus()

    def _paintStatus(self):
        """Overlay the status string using QPainter on top of the GL surface."""
        from qtpy.QtGui import QColor, QFont, QPainter, QPen
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        font = QFont("Consolas", 8)
        painter.setFont(font)
        painter.setPen(QPen(QColor(180, 200, 220)))
        painter.drawText(8, 18, self._status.replace("\n", "  |  "))
        painter.end()

    # ------------------------------------------------------------------
    def mousePressEvent(self, e: QMouseEvent):
        self._mouse_buttons.add(e.button())
        self._mouse_last = (e.position().x(), e.position().y())

    def mouseReleaseEvent(self, e: QMouseEvent):
        self._mouse_buttons.discard(e.button())

    def mouseMoveEvent(self, e: QMouseEvent):
        dx = e.position().x() - self._mouse_last[0]
        dy = e.position().y() - self._mouse_last[1]
        self._mouse_last = (e.position().x(), e.position().y())
        if Qt.MouseButton.LeftButton in self._mouse_buttons:
            self._yaw -= dx * 0.008
            self._pitch = max(-1.48, min(1.48, self._pitch + dy * 0.008))
            self.update()
        elif Qt.MouseButton.MiddleButton in self._mouse_buttons or Qt.MouseButton.RightButton in self._mouse_buttons:
            self._cx -= dx * self._dist * 0.001
            self._cy -= dy * self._dist * 0.001
            self.update()

    def wheelEvent(self, e: QWheelEvent):
        self._dist = max(0.01, self._dist * (0.9 if e.angleDelta().y() > 0 else 1.1))
        self.update()


# ---------------------------------------------------------------------------
# AutoRigger main window
# ---------------------------------------------------------------------------


class AutoRiggerWindow(QMainWindow):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("AutoRigger — KotOR Model Rigger")
        self.resize(1200, 680)

        self._process: QProcess | None = None
        self._runner_script_path: str | None = None
        self._mdl_renderer = None  # lazy-loaded ModelRenderer

        central = QWidget(self)
        self.setCentralWidget(central)
        outer = QHBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)

        # ── Main horizontal splitter: controls | preview ──────────────
        splitter = QSplitter(Qt.Orientation.Horizontal, central)
        outer.addWidget(splitter)

        # ── LEFT: controls panel ──────────────────────────────────────
        left_widget = QWidget()
        left_widget.setMinimumWidth(380)
        left_widget.setMaximumWidth(520)
        root = QVBoxLayout(left_widget)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(4)
        splitter.addWidget(left_widget)

        info = QLabel(
            "Rig OBJ/FBX using GhostRigger-K1-K2 and export KotOR-compatible MDL/MDX. "
            "Requires a local clone of CrispyW0nton/Kotor-3D-Model-Converter."
        )
        info.setWordWrap(True)
        root.addWidget(info)

        paths_box = QGroupBox("Paths")
        paths_layout = QFormLayout(paths_box)

        self.repoPathEdit = QLineEdit()
        self.pythonPathEdit = QLineEdit(sys.executable)
        self.inputPathEdit = QLineEdit()
        self.outputPathEdit = QLineEdit()

        paths_layout.addRow("GhostRigger repo:", self._with_browse(self.repoPathEdit, self._browseRepo))
        paths_layout.addRow("Python executable:", self._with_browse(self.pythonPathEdit, self._browsePython))
        paths_layout.addRow("Input model (OBJ/FBX):", self._with_browse(self.inputPathEdit, self._browseInput))
        paths_layout.addRow("Output MDL path:", self._with_browse(self.outputPathEdit, self._browseOutput))

        root.addWidget(paths_box)

        options_box = QGroupBox("Rig Options")
        options_layout = QGridLayout(options_box)

        self.templateCombo = QComboBox()
        self.templateCombo.addItems(["humanoid", "creature", "prop"])

        self.supermodelEdit = QLineEdit("S_Female02")

        options_layout.addWidget(QLabel("Template:"), 0, 0)
        options_layout.addWidget(self.templateCombo, 0, 1)
        options_layout.addWidget(QLabel("Supermodel:"), 0, 2)
        options_layout.addWidget(self.supermodelEdit, 0, 3)

        root.addWidget(options_box)

        self.logOutput = QTextEdit()
        self.logOutput.setReadOnly(True)
        root.addWidget(self.logOutput, 1)

        buttons = QHBoxLayout()
        self.detectRepoButton = QPushButton("Auto-Detect Repo")
        self.detectRepoButton.clicked.connect(self.autoDetectRepoPath)
        self.validateDepsButton = QPushButton("Validate Dependencies")
        self.validateDepsButton.clicked.connect(self._onValidateDepsClicked)
        self.runButton = QPushButton("Run AutoRigger")
        self.runButton.clicked.connect(self.runAutoRigger)
        self.stopButton = QPushButton("Stop")
        self.stopButton.setEnabled(False)
        self.stopButton.clicked.connect(self.stopAutoRigger)
        buttons.addWidget(self.detectRepoButton)
        buttons.addWidget(self.validateDepsButton)
        buttons.addWidget(self.runButton)
        buttons.addWidget(self.stopButton)
        buttons.addStretch(1)
        root.addLayout(buttons)

        self.modeCombo = QComboBox()
        self.modeCombo.addItems(["auto-rig", "rig-from-template"])
        self.modeCombo.currentTextChanged.connect(self._onModeChanged)
        options_layout.addWidget(QLabel("Mode:"), 1, 0)
        options_layout.addWidget(self.modeCombo, 1, 1)

        self.templateTransferBox = QGroupBox("Template Transfer")
        template_layout = QFormLayout(self.templateTransferBox)
        self.templateModelPathEdit = QLineEdit()
        self.scaleToTargetCheck = QCheckBox("Scale template rig to target model bounds")
        self.scaleToTargetCheck.setChecked(True)
        template_layout.addRow("Template MDL:", self._with_browse(self.templateModelPathEdit, self._browseTemplateModel))
        template_layout.addRow("", self.scaleToTargetCheck)
        root.addWidget(self.templateTransferBox)

        self.autoDetectRepoPath(silent=True)
        self._onModeChanged(self.modeCombo.currentText())

        # ── RIGHT: preview panel ──────────────────────────────────────
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(4, 4, 4, 4)
        right_layout.setSpacing(2)

        preview_label = QLabel("Model Preview")
        preview_label.setStyleSheet("font-weight: bold; color: #cccccc;")
        right_layout.addWidget(preview_label)

        self.previewTabs = QTabWidget()
        self.previewTabs.setMinimumWidth(400)

        # Tab 1 – Input preview (OBJ/FBX)
        self.objPreview = OBJPreviewWidget(self)
        self.previewTabs.addTab(self.objPreview, "Input Preview")

        # Tab 2 – Output MDL preview  (lazy-loaded ModelRenderer)
        self._mdlPreviewStack = QStackedWidget()
        self._mdlPlaceholder = QLabel("Output MDL preview\nappears after rigging completes")
        self._mdlPlaceholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._mdlPlaceholder.setStyleSheet("color: #666; font-size: 10pt;")
        self._mdlPreviewStack.addWidget(self._mdlPlaceholder)  # index 0
        self.previewTabs.addTab(self._mdlPreviewStack, "Output MDL")

        right_layout.addWidget(self.previewTabs, 1)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        # Connect input path changes to live OBJ preview
        self.inputPathEdit.editingFinished.connect(self._onInputPathChanged)

    def _with_browse(self, edit: QLineEdit, callback: Callable[[], None]) -> QWidget:
        container = QWidget(self)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(edit)
        button = QPushButton("Browse...")
        button.clicked.connect(callback)
        layout.addWidget(button)
        return container

    def _browseRepo(self):
        path = QFileDialog.getExistingDirectory(self, "Select GhostRigger Repository")
        if path:
            self.repoPathEdit.setText(path)

    def _browsePython(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Python Executable")
        if path:
            self.pythonPathEdit.setText(path)

    def _browseInput(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Input Model", filter="Models (*.obj *.fbx);;All Files (*)")
        if path:
            self.inputPathEdit.setText(path)
            default_out = os.path.splitext(path)[0] + "_rigged.mdl"
            if not self.outputPathEdit.text().strip():
                self.outputPathEdit.setText(default_out)
            # Auto-preview
            self.objPreview.loadFile(path)
            self.previewTabs.setCurrentIndex(0)

    def _browseTemplateModel(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Template MDL", filter="KotOR Model (*.mdl);;All Files (*)")
        if path:
            self.templateModelPathEdit.setText(path)

    def _browseOutput(self):
        path, _ = QFileDialog.getSaveFileName(self, "Select Output MDL", filter="KotOR Model (*.mdl);;All Files (*)")
        if path:
            if not path.lower().endswith(".mdl"):
                path += ".mdl"
            self.outputPathEdit.setText(path)

    def _append_log(self, text: str):
        if text:
            self.logOutput.append(text.rstrip("\n"))

    def _validate(self) -> bool:
        repo_path = self.repoPathEdit.text().strip()
        input_path = self.inputPathEdit.text().strip()
        output_path = self.outputPathEdit.text().strip()

        if not repo_path:
            QMessageBox.warning(self, "Missing Path", "Select the GhostRigger repository path.")
            return False
        if not os.path.isdir(repo_path):
            QMessageBox.warning(self, "Invalid Path", "GhostRigger repository path does not exist.")
            return False
        if not input_path or not os.path.isfile(input_path):
            QMessageBox.warning(self, "Missing Input", "Select a valid OBJ or FBX input file.")
            return False
        if not output_path:
            QMessageBox.warning(self, "Missing Output", "Set an output MDL path.")
            return False
        ext = os.path.splitext(input_path)[1].lower()
        if ext not in {".obj", ".fbx"}:
            QMessageBox.warning(self, "Unsupported Input", "Input model must be OBJ or FBX.")
            return False
        if self.modeCombo.currentText() == "rig-from-template":
            template_path = self.templateModelPathEdit.text().strip()
            if not template_path or not os.path.isfile(template_path):
                QMessageBox.warning(self, "Missing Template", "Select a valid template MDL file for template mode.")
                return False
        return True

    def _onModeChanged(self, mode: str):
        is_template_mode = mode == "rig-from-template"
        self.templateTransferBox.setEnabled(is_template_mode)

    def _looksLikeGhostRiggerRepo(self, path: str) -> bool:
        required = [
            os.path.join(path, "src", "autorig", "auto_rigger.py"),
            os.path.join(path, "src", "converters", "mesh_converter.py"),
        ]
        return all(os.path.isfile(p) for p in required)

    def _candidateRepoPaths(self) -> list[str]:
        candidates: list[str] = []
        cwd = os.getcwd()
        user_profile = os.environ.get("USERPROFILE", "")
        home = os.path.expanduser("~")

        bases = [cwd, home, user_profile]
        for base in bases:
            if not base:
                continue
            candidates.extend(
                [
                    os.path.join(base, "Kotor-3D-Model-Converter"),
                    os.path.join(base, "Kotor-3D-Model-Converter-main"),
                    os.path.join(base, "Documents", "Kotor-3D-Model-Converter"),
                    os.path.join(base, "Documents", "GitHub", "Kotor-3D-Model-Converter"),
                ]
            )

        # If currently inside the repo, resolve from parent chain.
        path = os.path.abspath(cwd)
        while True:
            if self._looksLikeGhostRiggerRepo(path):
                candidates.insert(0, path)
                break
            parent = os.path.dirname(path)
            if parent == path:
                break
            path = parent
        return candidates

    def autoDetectRepoPath(self, *, silent: bool = False):
        for candidate in self._candidateRepoPaths():
            if self._looksLikeGhostRiggerRepo(candidate):
                self.repoPathEdit.setText(candidate)
                if not silent:
                    self._append_log(f"Auto-detected GhostRigger repo: {candidate}")
                return
        if not silent:
            self._append_log("Could not auto-detect GhostRigger repo path.")

    def validateDependencies(self, *, show_dialog: bool) -> bool:
        repo_path = self.repoPathEdit.text().strip()
        python_exec = self.pythonPathEdit.text().strip() or sys.executable
        input_path = self.inputPathEdit.text().strip()

        if not repo_path or not os.path.isdir(repo_path):
            if show_dialog:
                QMessageBox.warning(self, "Missing Repo", "Select a valid GhostRigger repository path first.")
            return False

        check_script = (
            "import os,sys;"
            "repo=sys.argv[1];"
            "src=os.path.join(repo,'src');"
            "sys.path.insert(0,repo);sys.path.insert(0,src);"
            "import src.autorig.auto_rigger as ar;"
            "import src.converters.mesh_converter as mc;"
            "print('OK: auto_rigger and mesh_converter import');"
            "print('AutoRigger:', hasattr(ar, 'AutoRigger'));"
            "print('OBJImporter:', hasattr(mc, 'OBJImporter'));"
            "print('FBXImporter:', hasattr(mc, 'FBXImporter'))"
        )

        try:
            result = subprocess.run(
                [python_exec, "-c", check_script, repo_path],
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError as exc:
            if show_dialog:
                QMessageBox.warning(self, "Python Error", f"Could not execute Python: {exc}")
            return False

        if result.stdout:
            self._append_log(result.stdout)
        if result.stderr:
            self._append_log(result.stderr)

        ok = result.returncode == 0
        if ok and input_path.lower().endswith(".fbx"):
            self._append_log("Note: FBX import may require system assimp libraries depending on environment.")

        if show_dialog:
            if ok:
                QMessageBox.information(self, "Dependencies", "GhostRigger dependency validation passed.")
            else:
                QMessageBox.warning(self, "Dependencies", "Dependency validation failed. Check log output for details.")
        return ok

    def _onValidateDepsClicked(self):
        self.validateDependencies(show_dialog=True)

    def runAutoRigger(self):
        if not self._validate():
            return

        if not self.validateDependencies(show_dialog=False):
            QMessageBox.warning(self, "Dependency Check Failed", "GhostRigger dependency validation failed. Click 'Validate Dependencies' for details.")
            return

        self.logOutput.clear()
        self._append_log("Starting AutoRigger pipeline...")

        python_exec = self.pythonPathEdit.text().strip() or sys.executable
        repo_path = self.repoPathEdit.text().strip()
        input_path = self.inputPathEdit.text().strip()
        output_path = self.outputPathEdit.text().strip()
        template = self.templateCombo.currentText()
        mode = self.modeCombo.currentText()
        runner_mode = "template" if mode == "rig-from-template" else "auto"
        template_model = self.templateModelPathEdit.text().strip()
        scale_to_target = self.scaleToTargetCheck.isChecked()
        supermodel = self.supermodelEdit.text().strip()

        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        if not self._runner_script_path:
            script_fd, script_path = tempfile.mkstemp(prefix="ht_autorigger_", suffix=".py")
            os.close(script_fd)
            with open(script_path, "w", encoding="utf-8") as script_file:
                script_file.write(RUNNER_SCRIPT)
            self._runner_script_path = script_path

        process = QProcess(self)
        self._process = process
        process.setProgram(python_exec)
        args = [
            self._runner_script_path,
            "--repo",
            repo_path,
            "--input",
            input_path,
            "--output",
            output_path,
            "--mode",
            runner_mode,
            "--template",
            template,
            "--template-model",
            template_model,
            "--supermodel",
            supermodel,
        ]
        if scale_to_target:
            args.append("--scale-to-target")
        process.setArguments(args)
        process.readyReadStandardOutput.connect(self._onStdOut)
        process.readyReadStandardError.connect(self._onStdErr)
        process.finished.connect(self._onFinished)

        self.runButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        process.start()

    def stopAutoRigger(self):
        if self._process is not None:
            self._process.kill()

    def _onStdOut(self):
        if self._process is None:
            return
        text = bytes(self._process.readAllStandardOutput()).decode("utf-8", errors="replace")
        self._append_log(text)

    def _onStdErr(self):
        if self._process is None:
            return
        text = bytes(self._process.readAllStandardError()).decode("utf-8", errors="replace")
        self._append_log(text)

    def _onFinished(self, exit_code: int, _exit_status: int):
        self.runButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        if exit_code == 0:
            self._append_log("AutoRigger completed successfully.")
            # Auto-load the output MDL into the preview
            output_path = self.outputPathEdit.text().strip()
            if output_path and os.path.isfile(output_path):
                self._loadOutputMDL(output_path)
                self.previewTabs.setCurrentIndex(1)
        else:
            self._append_log(f"AutoRigger failed with exit code {exit_code}.")

    # ------------------------------------------------------------------
    # Preview helpers
    # ------------------------------------------------------------------

    def _onInputPathChanged(self):
        """Auto-preview the input OBJ/FBX when the path field is edited."""
        path = self.inputPathEdit.text().strip()
        if path:
            self.objPreview.loadFile(path)
            self.previewTabs.setCurrentIndex(0)

    def _loadOutputMDL(self, mdl_path: str):
        """Load the rigged MDL into the ModelRenderer output tab."""
        mdx_path = os.path.splitext(mdl_path)[0] + ".mdx"
        try:
            with open(mdl_path, "rb") as f:
                mdl_data = f.read()
            mdx_data = b""
            if os.path.isfile(mdx_path):
                with open(mdx_path, "rb") as f:
                    mdx_data = f.read()
        except OSError as exc:
            self._append_log(f"Could not read output MDL: {exc}")
            return

        renderer = self._getOrCreateMDLRenderer()
        if renderer is not None:
            try:
                renderer.setModel(mdl_data, mdx_data)
            except Exception as exc:
                self._append_log(f"MDL preview error: {exc}")

    def _getOrCreateMDLRenderer(self):
        """Lazy-create the ModelRenderer the first time the output tab is needed."""
        if self._mdl_renderer is not None:
            return self._mdl_renderer
        try:
            from toolset.gui.widgets.renderer.model import ModelRenderer  # noqa: PLC0415
            renderer = ModelRenderer(self)
            self._mdlPreviewStack.addWidget(renderer)         # index 1
            self._mdlPreviewStack.setCurrentIndex(1)
            self._mdl_renderer = renderer
            return renderer
        except Exception as exc:
            self._append_log(f"Could not create MDL renderer: {exc}")
            return None

    def closeEvent(self, a0: QCloseEvent | None):
        if self._process is not None and self._process.state() != QProcess.ProcessState.NotRunning:
            self._process.kill()
        if self._runner_script_path and os.path.isfile(self._runner_script_path):
            try:
                os.remove(self._runner_script_path)
            except OSError:
                pass
        super().closeEvent(a0)
