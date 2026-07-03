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
from .services.card_generation import CardGenerationService
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
        self.card_generation_service = CardGenerationService(workspace)
        self.path_labels: dict[str, QLabel] = {}
        self.exists_labels: dict[str, QLabel] = {}
        self.write_labels: dict[str, QLabel] = {}
        self.package_count_label = QLabel()
        self.log_output = QTextEdit()
        self._init_texts()

        self.setWindowTitle(self.window_title_text)
        self.resize(980, 700)
        self._build_ui()
        self.refresh_status()

    def _init_texts(self) -> None:
        self.window_title_text = self.tr("FontGallery")
        self.title_text = self.tr("FontGallery")
        self.subtitle_text = self.tr(
            "Tool for preparing a workspace and automating visual font albums from .deb packages."
        )
        self.workspace_group_text = self.tr("Workspace Status")
        self.actions_group_text = self.tr("Primary Actions")
        self.log_group_text = self.tr("Log")
        self.base_folder_text = self.tr("Base folder")
        self.column_item_text = self.tr("Item")
        self.column_path_text = self.tr("Path")
        self.column_status_text = self.tr("Status")
        self.column_write_text = self.tr("Write access")
        self.path_labels_text = {
            "packages": self.tr("Packages"),
            "album_main": self.tr("Main album"),
            "album_es": self.tr("Spanish album"),
            "album_tech": self.tr("Technical album"),
        }
        self.album_labels_text = {
            "main": self.tr("Main album"),
            "spanish": self.tr("Spanish album"),
            "technical": self.tr("Technical album"),
        }
        self.prepare_button_text = self.tr("Prepare workspace")
        self.extract_button_text = self.tr("Extract all fonts to the main album")
        self.analyze_button_text = self.tr("Analyze and classify the master collection")
        self.html_button_text = self.tr("Generate HTML indexes")
        self.cards_button_text = self.tr("Generate PNG cards")
        self.refresh_button_text = self.tr("Refresh status")
        self.exists_text = self.tr("Exists")
        self.missing_text = self.tr("Missing")
        self.writable_text = self.tr("Writable")
        self.not_writable_text = self.tr("Not writable")
        self.package_count_text = self.tr("Detected .deb packages in '{folder}': {count}")
        self.error_title_text = self.tr("Error")
        self.warning_title_text = self.tr("Warning")
        self.workspace_ready_title_text = self.tr("Workspace ready")
        self.workspace_ready_message_text = self.tr("The base workspace structure was verified successfully.")
        self.created_folder_log_text = self.tr("Created folder: {path}")
        self.no_folders_created_log_text = self.tr("No folders needed to be created. The workspace already existed.")
        self.no_packages_title_text = self.tr("No packages")
        self.extract_completed_title_text = self.tr("Extraction completed")
        self.extract_completed_message_text = self.tr(
            "Extraction into the main album finished.\n\n"
            "Unique fonts: {unique}\n"
            "Skipped duplicates: {duplicates}\n"
            "Skipped broken fonts: {broken}"
        )
        self.extract_summary_log_text = self.tr(
            "Extraction summary: packages seen={seen}, font packages={font_packages}, "
            "unique fonts={unique}, skipped duplicates={duplicates}, skipped broken={broken}"
        )
        self.extract_dir_log_text = self.tr("Extraction directory: {path}")
        self.master_missing_title_text = self.tr("Missing master collection")
        self.analysis_completed_title_text = self.tr("Analysis completed")
        self.analysis_completed_message_text = self.tr(
            "The master collection was analyzed and classified.\n\n"
            "Total fonts: {total}\n"
            "Fonts with Spanish support: {spanish}\n"
            "Technical fonts: {technical}\n"
            "Copied to the Spanish album: {copied_spanish}\n"
            "Copied to the technical album: {copied_technical}"
        )
        self.analysis_summary_log_text = self.tr(
            "Analysis summary: total={total}, with Spanish support={spanish}, "
            "technical={technical}, copied to Spanish={copied_spanish}, copied to technical={copied_technical}"
        )
        self.html_missing_title_text = self.tr("Missing extracted fonts")
        self.html_completed_title_text = self.tr("HTML generation completed")
        self.html_completed_message_text = self.tr(
            "The HTML font albums were generated successfully.\n\n{details}"
        )
        self.cards_completed_title_text = self.tr("PNG card generation completed")
        self.cards_completed_message_text = self.tr(
            "The PNG font cards were generated successfully.\n\n{details}"
        )
        self.html_summary_log_text = self.tr(
            "HTML album '{label}': included={included}, excluded={excluded}, path={path}"
        )
        self.cards_summary_log_text = self.tr(
            "PNG cards '{label}': generated={generated}, excluded={excluded}, render errors={errors}, path={path}"
        )
        self.exclusion_report_log_text = self.tr("Exclusion report: {path}")
        self.external_tool_failed_text = self.tr("An external tool failed:\n{error}")
        self.workspace_prepare_failed_text = self.tr("Could not prepare the workspace:\n{error}")
        self.extract_failed_text = self.tr("Could not extract the fonts:\n{error}")
        self.analysis_failed_text = self.tr("Could not analyze the collection:\n{error}")
        self.html_failed_text = self.tr("Could not generate HTML indexes:\n{error}")
        self.cards_failed_text = self.tr("Could not generate PNG cards:\n{error}")
        self.error_log_text = self.tr("ERROR: {error}")
        self.warning_log_text = self.tr("WARNING: {error}")

    def _build_ui(self) -> None:
        central = QWidget(self)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(14)

        title = QLabel(self.title_text)
        title.setStyleSheet("font-size: 28px; font-weight: 700;")
        root_layout.addWidget(title)

        subtitle = QLabel(self.subtitle_text)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #444; font-size: 14px;")
        root_layout.addWidget(subtitle)

        root_layout.addWidget(self._build_workspace_box())
        root_layout.addWidget(self._build_actions_box())
        root_layout.addWidget(self._build_log_box(), 1)

        self.setCentralWidget(central)

    def _build_workspace_box(self) -> QGroupBox:
        box = QGroupBox(self.workspace_group_text)
        layout = QVBoxLayout(box)

        root_label = QLabel(f"{self.base_folder_text}: {self.workspace.project_root}")
        root_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(root_label)

        self.package_count_label.setStyleSheet("font-weight: 600;")
        layout.addWidget(self.package_count_label)

        grid = QGridLayout()
        grid.addWidget(QLabel(self.column_item_text), 0, 0)
        grid.addWidget(QLabel(self.column_path_text), 0, 1)
        grid.addWidget(QLabel(self.column_status_text), 0, 2)
        grid.addWidget(QLabel(self.column_write_text), 0, 3)

        for row, item in enumerate(self.workspace.managed_paths, start=1):
            label = QLabel(self.path_labels_text.get(item.key, item.label))
            path_label = QLabel(str(item.path))
            path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            state_label = QLabel()
            write_label = QLabel()
            self.path_labels[item.key] = path_label
            self.exists_labels[item.key] = state_label
            self.write_labels[item.key] = write_label
            grid.addWidget(label, row, 0)
            grid.addWidget(path_label, row, 1)
            grid.addWidget(state_label, row, 2)
            grid.addWidget(write_label, row, 3)

        layout.addLayout(grid)
        return box

    def _build_actions_box(self) -> QGroupBox:
        box = QGroupBox(self.actions_group_text)
        layout = QHBoxLayout(box)

        prepare_button = QPushButton(self.prepare_button_text)
        prepare_button.clicked.connect(self.on_prepare_structure)
        layout.addWidget(prepare_button)

        extract_button = QPushButton(self.extract_button_text)
        extract_button.clicked.connect(self.on_extract_main_fonts)
        layout.addWidget(extract_button)

        analyze_button = QPushButton(self.analyze_button_text)
        analyze_button.clicked.connect(self.on_analyze_main_collection)
        layout.addWidget(analyze_button)

        html_button = QPushButton(self.html_button_text)
        html_button.clicked.connect(self.on_generate_html_indexes)
        layout.addWidget(html_button)

        cards_button = QPushButton(self.cards_button_text)
        cards_button.clicked.connect(self.on_generate_png_cards)
        layout.addWidget(cards_button)

        refresh_button = QPushButton(self.refresh_button_text)
        refresh_button.clicked.connect(self.refresh_status)
        layout.addWidget(refresh_button)

        layout.addStretch(1)
        return box

    def _build_log_box(self) -> QGroupBox:
        box = QGroupBox(self.log_group_text)
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
                state_label.setText(self.exists_text)
                state_label.setStyleSheet("color: #0a7f2e; font-weight: 600;")
            else:
                state_label.setText(self.missing_text)
                state_label.setStyleSheet("color: #a33; font-weight: 600;")

            writable = bool(item["writable"])
            write_label = self.write_labels[key]
            if writable:
                write_label.setText(self.writable_text)
                write_label.setStyleSheet("color: #0a7f2e; font-weight: 600;")
            else:
                write_label.setText(self.not_writable_text)
                write_label.setStyleSheet("color: #a33; font-weight: 600;")

        self.package_count_label.setText(
            self.package_count_text.format(
                folder=self.workspace.packages_dir.name,
                count=self.workspace.deb_package_count(),
            )
        )

    def on_prepare_structure(self) -> None:
        try:
            created = self.workspace.prepare_structure()
        except OSError as exc:
            QMessageBox.critical(self, self.error_title_text, self.workspace_prepare_failed_text.format(error=exc))
            self._log(self.error_log_text.format(error=exc))
            return

        if created:
            for path in created:
                self._log(self.created_folder_log_text.format(path=path))
        else:
            self._log(self.no_folders_created_log_text)

        self.refresh_status()
        QMessageBox.information(self, self.workspace_ready_title_text, self.workspace_ready_message_text)

    def on_extract_main_fonts(self) -> None:
        try:
            summary, _ = self.extraction_service.extract_to_main_album(log=self._log)
        except FileNotFoundError as exc:
            QMessageBox.warning(self, self.no_packages_title_text, str(exc))
            self._log(self.warning_log_text.format(error=exc))
            return
        except subprocess.CalledProcessError as exc:  # type: ignore[name-defined]
            QMessageBox.critical(self, self.error_title_text, self.external_tool_failed_text.format(error=exc))
            self._log(self.error_log_text.format(error=exc))
            return
        except OSError as exc:
            QMessageBox.critical(self, self.error_title_text, self.extract_failed_text.format(error=exc))
            self._log(self.error_log_text.format(error=exc))
            return

        self._log(
            self.extract_summary_log_text.format(
                seen=summary.packages_seen,
                font_packages=summary.font_packages_processed,
                unique=summary.unique_fonts_extracted,
                duplicates=summary.duplicate_fonts_skipped,
                broken=summary.broken_fonts_skipped,
            )
        )
        self._log(self.extract_dir_log_text.format(path=summary.extract_dir))
        self.refresh_status()
        QMessageBox.information(
            self,
            self.extract_completed_title_text,
            self.extract_completed_message_text.format(
                unique=summary.unique_fonts_extracted,
                duplicates=summary.duplicate_fonts_skipped,
                broken=summary.broken_fonts_skipped,
            ),
        )

    def on_analyze_main_collection(self) -> None:
        try:
            summary, _ = self.analysis_service.analyze_main_collection(log=self._log)
        except FileNotFoundError as exc:
            QMessageBox.warning(self, self.master_missing_title_text, str(exc))
            self._log(self.warning_log_text.format(error=exc))
            return
        except subprocess.CalledProcessError as exc:
            QMessageBox.critical(self, self.error_title_text, self.external_tool_failed_text.format(error=exc))
            self._log(self.error_log_text.format(error=exc))
            return
        except OSError as exc:
            QMessageBox.critical(self, self.error_title_text, self.analysis_failed_text.format(error=exc))
            self._log(self.error_log_text.format(error=exc))
            return

        self._log(
            self.analysis_summary_log_text.format(
                total=summary.total_fonts,
                spanish=summary.spanish_fonts,
                technical=summary.technical_fonts,
                copied_spanish=summary.copied_to_spanish,
                copied_technical=summary.copied_to_technical,
            )
        )
        self.refresh_status()
        QMessageBox.information(
            self,
            self.analysis_completed_title_text,
            self.analysis_completed_message_text.format(
                total=summary.total_fonts,
                spanish=summary.spanish_fonts,
                technical=summary.technical_fonts,
                copied_spanish=summary.copied_to_spanish,
                copied_technical=summary.copied_to_technical,
            ),
        )

    def on_generate_html_indexes(self) -> None:
        try:
            summaries = self.html_generation_service.generate_all_albums(log=self._log)
        except FileNotFoundError as exc:
            QMessageBox.warning(self, self.html_missing_title_text, str(exc))
            self._log(self.warning_log_text.format(error=exc))
            return
        except subprocess.CalledProcessError as exc:
            QMessageBox.critical(self, self.error_title_text, self.external_tool_failed_text.format(error=exc))
            self._log(self.error_log_text.format(error=exc))
            return
        except OSError as exc:
            QMessageBox.critical(self, self.error_title_text, self.html_failed_text.format(error=exc))
            self._log(self.error_log_text.format(error=exc))
            return

        for summary in summaries:
            label_text = self.album_labels_text.get(summary.label, summary.label)
            self._log(
                self.html_summary_log_text.format(
                    label=label_text,
                    included=summary.included_fonts,
                    excluded=summary.excluded_fonts,
                    path=summary.html_path,
                )
            )
            if summary.excluded_report is not None:
                self._log(self.exclusion_report_log_text.format(path=summary.excluded_report))

        QMessageBox.information(
            self,
            self.html_completed_title_text,
            self.html_completed_message_text.format(
                details="\n".join(
                    f"{self.album_labels_text.get(summary.label, summary.label)}: {summary.included_fonts} fonts"
                    for summary in summaries
                )
            ),
        )

    def on_generate_png_cards(self) -> None:
        try:
            summaries = self.card_generation_service.generate_all_albums(log=self._log)
        except FileNotFoundError as exc:
            QMessageBox.warning(self, self.html_missing_title_text, str(exc))
            self._log(self.warning_log_text.format(error=exc))
            return
        except subprocess.CalledProcessError as exc:
            QMessageBox.critical(self, self.error_title_text, self.external_tool_failed_text.format(error=exc))
            self._log(self.error_log_text.format(error=exc))
            return
        except (OSError, RuntimeError) as exc:
            QMessageBox.critical(self, self.error_title_text, self.cards_failed_text.format(error=exc))
            self._log(self.error_log_text.format(error=exc))
            return

        for summary in summaries:
            label_text = self.album_labels_text.get(summary.label, summary.label)
            self._log(
                self.cards_summary_log_text.format(
                    label=label_text,
                    generated=summary.generated_cards,
                    excluded=summary.excluded_fonts,
                    errors=summary.render_errors,
                    path=summary.output_dir,
                )
            )

        QMessageBox.information(
            self,
            self.cards_completed_title_text,
            self.cards_completed_message_text.format(
                details="\n".join(
                    f"{self.album_labels_text.get(summary.label, summary.label)}: {summary.generated_cards} cards"
                    for summary in summaries
                )
            ),
        )

    def _log(self, message: str) -> None:
        self.log_output.append(message)
