from __future__ import annotations

import subprocess

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .services.analysis import AnalysisService
from .services.extraction import ExtractionService
from .services.html_generation import HtmlGenerationService
from .services.workspace import WorkspaceService


class MainWindow(QMainWindow):
    def __init__(self, workspace: WorkspaceService) -> None:
        super().__init__()
        self.workspace = workspace
        self.extraction_service = ExtractionService(workspace)
        self.analysis_service = AnalysisService(workspace)
        self.html_generation_service = HtmlGenerationService(workspace)
        self.path_labels: dict[str, QLabel] = {}
        self.exists_labels: dict[str, QLabel] = {}
        self.package_count_label = QLabel()
        self.log_output = QTextEdit()

        self.setWindowTitle("FontGallery")
        self.resize(980, 700)
        self._build_ui()
        self.refresh_status()

    def _build_ui(self) -> None:
        central = QWidget(self)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(14)

        title = QLabel("FontGallery")
        title.setStyleSheet("font-size: 28px; font-weight: 700;")
        root_layout.addWidget(title)

        subtitle = QLabel(
            "Herramienta para preparar la estructura de trabajo y automatizar álbumes visuales de fuentes desde paquetes .deb."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #444; font-size: 14px;")
        root_layout.addWidget(subtitle)

        root_layout.addWidget(self._build_workspace_box())
        root_layout.addWidget(self._build_actions_box())
        root_layout.addWidget(self._build_log_box(), 1)

        self.setCentralWidget(central)

    def _build_workspace_box(self) -> QGroupBox:
        box = QGroupBox("Estado del espacio de trabajo")
        layout = QVBoxLayout(box)

        root_label = QLabel(f"Carpeta base: {self.workspace.project_root}")
        root_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(root_label)

        self.package_count_label.setStyleSheet("font-weight: 600;")
        layout.addWidget(self.package_count_label)

        grid = QGridLayout()
        grid.addWidget(QLabel("Elemento"), 0, 0)
        grid.addWidget(QLabel("Ruta"), 0, 1)
        grid.addWidget(QLabel("Estado"), 0, 2)

        for row, item in enumerate(self.workspace.managed_paths, start=1):
            label = QLabel(item.label)
            path_label = QLabel(str(item.path))
            path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            state_label = QLabel()
            self.path_labels[item.key] = path_label
            self.exists_labels[item.key] = state_label
            grid.addWidget(label, row, 0)
            grid.addWidget(path_label, row, 1)
            grid.addWidget(state_label, row, 2)

        layout.addLayout(grid)
        return box

    def _build_actions_box(self) -> QGroupBox:
        box = QGroupBox("Acciones iniciales")
        layout = QHBoxLayout(box)

        prepare_button = QPushButton("Preparar estructura")
        prepare_button.clicked.connect(self.on_prepare_structure)
        layout.addWidget(prepare_button)

        extract_button = QPushButton("Extraer todas las fuentes a album-fuentes")
        extract_button.clicked.connect(self.on_extract_main_fonts)
        layout.addWidget(extract_button)

        analyze_button = QPushButton("Analizar y clasificar colección maestra")
        analyze_button.clicked.connect(self.on_analyze_main_collection)
        layout.addWidget(analyze_button)

        html_button = QPushButton("Generar indices HTML")
        html_button.clicked.connect(self.on_generate_html_indexes)
        layout.addWidget(html_button)

        refresh_button = QPushButton("Actualizar estado")
        refresh_button.clicked.connect(self.refresh_status)
        layout.addWidget(refresh_button)

        layout.addStretch(1)
        return box

    def _build_log_box(self) -> QGroupBox:
        box = QGroupBox("Registro")
        layout = QVBoxLayout(box)
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)
        return box

    def refresh_status(self) -> None:
        statuses = self.workspace.path_status()
        for item in statuses:
            key = str(item["key"])
            exists = bool(item["exists"])
            state_label = self.exists_labels[key]
            if exists:
                state_label.setText("Existe")
                state_label.setStyleSheet("color: #0a7f2e; font-weight: 600;")
            else:
                state_label.setText("No existe")
                state_label.setStyleSheet("color: #a33; font-weight: 600;")

        self.package_count_label.setText(
            f"Paquetes .deb detectados en 'paquetes-deb': {self.workspace.deb_package_count()}"
        )

    def on_prepare_structure(self) -> None:
        try:
            created = self.workspace.prepare_structure()
        except OSError as exc:
            QMessageBox.critical(self, "Error", f"No se pudo preparar la estructura:\n{exc}")
            self._log(f"ERROR: {exc}")
            return

        if created:
            for path in created:
                self._log(f"Creada carpeta: {path}")
        else:
            self._log("No fue necesario crear carpetas. La estructura ya existía.")

        self.refresh_status()
        QMessageBox.information(self, "Estructura lista", "La estructura base fue verificada correctamente.")

    def on_extract_main_fonts(self) -> None:
        try:
            summary, _ = self.extraction_service.extract_to_main_album(log=self._log)
        except FileNotFoundError as exc:
            QMessageBox.warning(self, "Sin paquetes", str(exc))
            self._log(f"AVISO: {exc}")
            return
        except subprocess.CalledProcessError as exc:  # type: ignore[name-defined]
            QMessageBox.critical(self, "Error", f"Falló una herramienta externa:\n{exc}")
            self._log(f"ERROR: {exc}")
            return
        except OSError as exc:
            QMessageBox.critical(self, "Error", f"No se pudo extraer las fuentes:\n{exc}")
            self._log(f"ERROR: {exc}")
            return

        self._log(
            "Resumen extracción: "
            f"paquetes vistos={summary.packages_seen}, "
            f"paquetes de fuentes={summary.font_packages_processed}, "
            f"fuentes únicas={summary.unique_fonts_extracted}, "
            f"duplicadas omitidas={summary.duplicate_fonts_skipped}, "
            f"rotas omitidas={summary.broken_fonts_skipped}"
        )
        self._log(f"Directorio de extracción: {summary.extract_dir}")
        self.refresh_status()
        QMessageBox.information(
            self,
            "Extracción completada",
            (
                "La extracción hacia album-fuentes terminó.\n\n"
                f"Fuentes únicas: {summary.unique_fonts_extracted}\n"
                f"Duplicadas omitidas: {summary.duplicate_fonts_skipped}\n"
                f"Rotas omitidas: {summary.broken_fonts_skipped}"
            ),
        )

    def on_analyze_main_collection(self) -> None:
        try:
            summary, _ = self.analysis_service.analyze_main_collection(log=self._log)
        except FileNotFoundError as exc:
            QMessageBox.warning(self, "Sin colección maestra", str(exc))
            self._log(f"AVISO: {exc}")
            return
        except subprocess.CalledProcessError as exc:
            QMessageBox.critical(self, "Error", f"Falló una herramienta externa:\n{exc}")
            self._log(f"ERROR: {exc}")
            return
        except OSError as exc:
            QMessageBox.critical(self, "Error", f"No se pudo analizar la colección:\n{exc}")
            self._log(f"ERROR: {exc}")
            return

        self._log(
            "Resumen análisis: "
            f"total={summary.total_fonts}, "
            f"con español={summary.spanish_fonts}, "
            f"técnicas={summary.technical_fonts}, "
            f"copiadas a español={summary.copied_to_spanish}, "
            f"copiadas a técnicas={summary.copied_to_technical}"
        )
        self.refresh_status()
        QMessageBox.information(
            self,
            "Análisis completado",
            (
                "La colección maestra fue analizada y clasificada.\n\n"
                f"Fuentes totales: {summary.total_fonts}\n"
                f"Fuentes con español: {summary.spanish_fonts}\n"
                f"Fuentes técnicas: {summary.technical_fonts}\n"
                f"Copiadas a album-fuentes-espanol: {summary.copied_to_spanish}\n"
                f"Copiadas a album-fuentes-tecnicas: {summary.copied_to_technical}"
            ),
        )

    def on_generate_html_indexes(self) -> None:
        try:
            summaries = self.html_generation_service.generate_all_albums(log=self._log)
        except FileNotFoundError as exc:
            QMessageBox.warning(self, "Missing extracted fonts", str(exc))
            self._log(f"WARNING: {exc}")
            return
        except subprocess.CalledProcessError as exc:
            QMessageBox.critical(self, "Error", f"An external tool failed:\n{exc}")
            self._log(f"ERROR: {exc}")
            return
        except OSError as exc:
            QMessageBox.critical(self, "Error", f"Could not generate HTML indexes:\n{exc}")
            self._log(f"ERROR: {exc}")
            return

        for summary in summaries:
            self._log(
                f"HTML album '{summary.label}': included={summary.included_fonts}, "
                f"excluded={summary.excluded_fonts}, path={summary.html_path}"
            )
            if summary.excluded_report is not None:
                self._log(f"Exclusion report: {summary.excluded_report}")

        QMessageBox.information(
            self,
            "HTML generation completed",
            (
                "The HTML font albums were generated successfully.\n\n"
                + "\n".join(
                    f"{summary.label}: {summary.included_fonts} fonts"
                    for summary in summaries
                )
            ),
        )

    def _log(self, message: str) -> None:
        self.log_output.append(message)
