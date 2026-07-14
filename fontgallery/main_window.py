from __future__ import annotations

import subprocess
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .services.analysis import AnalysisService
from .services.card_generation import CardGenerationService
from .services.extraction import ExtractionService
from .services.flat_card_export import FlatCardExportService
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
        self.flat_card_export_service = FlatCardExportService(workspace)
        self.path_labels: dict[str, QLabel] = {}
        self.exists_labels: dict[str, QLabel] = {}
        self.write_labels: dict[str, QLabel] = {}
        self.action_buttons: list[QPushButton] = []
        self.step_buttons: dict[str, QPushButton] = {}
        self.flat_export_buttons: dict[str, QPushButton] = {}
        self.flat_export_path_labels: dict[str, QLabel] = {}
        self.flat_export_status_labels: dict[str, QLabel] = {}
        self.step_states = {
            "prepare": "pending",
            "extract": "pending",
            "analyze": "pending",
            "html": "pending",
            "cards": "pending",
        }
        self.package_count_label = QLabel()
        self.progress_label = QLabel()
        self.progress_bar = QProgressBar()
        self.log_output = QTextEdit()
        self._init_texts()

        self.setWindowTitle(self.window_title_text)
        self.resize(980, 700)
        self._build_menu()
        self._build_ui()
        self._recompute_step_states()
        self.refresh_status()

    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu(self.file_menu_text)
        exit_action = QAction(self.exit_action_text, self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = self.menuBar().addMenu(self.help_menu_text)
        about_action = QAction(self.about_action_text, self)
        about_action.triggered.connect(self.on_show_about)
        help_menu.addAction(about_action)

    def _init_texts(self) -> None:
        self.window_title_text = self.tr("FontGallery")
        self.subtitle_text = self.tr(
            "Tool for preparing a workspace and automating visual font albums from .deb packages."
        )
        self.workspace_group_text = self.tr("Workspace Status")
        self.actions_group_text = self.tr("Primary Actions")
        self.optional_group_text = self.tr("Optional Flat Card Folders")
        self.log_group_text = self.tr("Log")
        self.workspace_tab_text = self.tr("Workspace")
        self.log_tab_text = self.tr("Log")
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
            "album_main_cards": self.tr("Main cards"),
            "album_es_cards": self.tr("Spanish cards"),
            "album_tech_cards": self.tr("Technical cards"),
        }
        self.album_labels_text = {
            "main": self.tr("Main album"),
            "spanish": self.tr("Spanish album"),
            "technical": self.tr("Technical album"),
        }
        self.prepare_button_text = self.tr("1. Prepare workspace")
        self.extract_button_text = self.tr("2. Extract all fonts to the main album")
        self.analyze_button_text = self.tr("3. Analyze and classify the master collection")
        self.html_button_text = self.tr("4. Generate HTML indexes")
        self.cards_button_text = self.tr("5. Generate PNG cards")
        self.refresh_button_text = self.tr("Refresh status")
        self.export_main_flat_button_text = self.tr("Copy main PNG cards to one root folder")
        self.export_spanish_flat_button_text = self.tr("Copy Spanish PNG cards to one root folder")
        self.export_technical_flat_button_text = self.tr("Copy technical PNG cards to one root folder")
        self.optional_export_hint_text = self.tr(
            "These optional actions copy the generated PNG cards into a single root folder so you can browse them sequentially in an image viewer."
        )
        self.flat_export_path_column_text = self.tr("Flat folder")
        self.progress_idle_text = self.tr("Ready.")
        self.progress_prepare_text = self.tr("Preparing workspace...")
        self.progress_extract_text = self.tr("Extracting fonts...")
        self.progress_analyze_text = self.tr("Analyzing master collection...")
        self.progress_html_text = self.tr("Generating HTML indexes...")
        self.progress_cards_text = self.tr("Generating PNG cards...")
        self.progress_completed_text = self.tr("Completed.")
        self.legend_pending_text = self.tr("Pending step")
        self.legend_active_text = self.tr("Step in progress")
        self.legend_completed_text = self.tr("Completed and current step")
        self.exists_text = self.tr("Exists")
        self.missing_text = self.tr("Missing")
        self.writable_text = self.tr("Writable")
        self.not_writable_text = self.tr("Not writable")
        self.package_count_text = self.tr("Detected .deb packages in '{folder}': {count}")
        self.error_title_text = self.tr("Error")
        self.warning_title_text = self.tr("Warning")
        self.file_menu_text = self.tr("File")
        self.help_menu_text = self.tr("Help")
        self.exit_action_text = self.tr("Exit")
        self.about_action_text = self.tr("About...")
        self.about_title_text = self.tr("About FontGallery")
        self.about_description_text = self.tr(
            "Desktop application for GNU/Linux that extracts fonts from .deb packages and builds visual HTML and PNG font albums."
        )
        self.about_email_label_text = self.tr("Email")
        self.about_license_label_text = self.tr("License")
        self.about_website_label_text = self.tr("Website")
        self.about_technologies_title_text = self.tr("Technologies used")
        self.about_technologies_text = self.tr("Python 3, PyQt6, Pillow, Fontconfig, dpkg")
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
        self.flat_export_completed_title_text = self.tr("Flat PNG card folder created")
        self.flat_export_completed_message_text = self.tr(
            "Copied {count} PNG cards into:\n{path}"
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
        self.flat_export_failed_text = self.tr("Could not create the flat PNG card folder:\n{error}")
        self.error_log_text = self.tr("ERROR: {error}")
        self.warning_log_text = self.tr("WARNING: {error}")

    def _build_ui(self) -> None:
        central = QWidget(self)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(14)

        subtitle = QLabel(self.subtitle_text)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #444; font-size: 14px;")
        root_layout.addWidget(subtitle)

        tabs = QTabWidget()
        tabs.addTab(self._build_workspace_tab(), self.workspace_tab_text)
        tabs.addTab(self._build_log_box(), self.log_tab_text)
        root_layout.addWidget(tabs, 1)

        self.setCentralWidget(central)

    def _build_workspace_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        layout.addWidget(self._build_workspace_box())
        layout.addWidget(self._build_actions_box())
        layout.addStretch(1)
        return tab

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

        for row, item in enumerate(self.workspace.status_paths, start=1):
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
        layout = QVBoxLayout(box)
        buttons_layout = QHBoxLayout()

        prepare_button = QPushButton(self.prepare_button_text)
        prepare_button.clicked.connect(self.on_prepare_structure)
        buttons_layout.addWidget(prepare_button)
        self.action_buttons.append(prepare_button)
        self.step_buttons["prepare"] = prepare_button

        extract_button = QPushButton(self.extract_button_text)
        extract_button.clicked.connect(self.on_extract_main_fonts)
        buttons_layout.addWidget(extract_button)
        self.action_buttons.append(extract_button)
        self.step_buttons["extract"] = extract_button

        analyze_button = QPushButton(self.analyze_button_text)
        analyze_button.clicked.connect(self.on_analyze_main_collection)
        buttons_layout.addWidget(analyze_button)
        self.action_buttons.append(analyze_button)
        self.step_buttons["analyze"] = analyze_button

        html_button = QPushButton(self.html_button_text)
        html_button.clicked.connect(self.on_generate_html_indexes)
        buttons_layout.addWidget(html_button)
        self.action_buttons.append(html_button)
        self.step_buttons["html"] = html_button

        cards_button = QPushButton(self.cards_button_text)
        cards_button.clicked.connect(self.on_generate_png_cards)
        buttons_layout.addWidget(cards_button)
        self.action_buttons.append(cards_button)
        self.step_buttons["cards"] = cards_button

        refresh_button = QPushButton(self.refresh_button_text)
        refresh_button.clicked.connect(self.refresh_status)
        buttons_layout.addWidget(refresh_button)
        self.action_buttons.append(refresh_button)

        buttons_layout.addStretch(1)
        layout.addLayout(buttons_layout)

        self.progress_label.setText(self.progress_idle_text)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v/%m (%p%)")
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)
        layout.addLayout(self._build_step_legend())
        layout.addWidget(self._build_optional_exports_box())
        self._refresh_step_button_styles()
        return box

    def _build_optional_exports_box(self) -> QGroupBox:
        box = QGroupBox(self.optional_group_text)
        layout = QVBoxLayout(box)

        hint_label = QLabel(self.optional_export_hint_text)
        hint_label.setWordWrap(True)
        hint_label.setStyleSheet("color: #4b5563;")
        layout.addWidget(hint_label)

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(8)
        grid.addWidget(QLabel(self.column_item_text), 0, 0)
        grid.addWidget(QLabel(self.flat_export_path_column_text), 0, 1)
        grid.addWidget(QLabel(self.column_status_text), 0, 2)

        main_button = QPushButton(self.export_main_flat_button_text)
        main_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        main_button.clicked.connect(lambda: self.on_export_flat_cards("main"))
        self.flat_export_buttons["main"] = main_button
        main_path_label = QLabel()
        main_path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        main_status_label = QLabel()
        self.flat_export_path_labels["main"] = main_path_label
        self.flat_export_status_labels["main"] = main_status_label
        grid.addWidget(main_button, 1, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        grid.addWidget(main_path_label, 1, 1)
        grid.addWidget(main_status_label, 1, 2)

        spanish_button = QPushButton(self.export_spanish_flat_button_text)
        spanish_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        spanish_button.clicked.connect(lambda: self.on_export_flat_cards("spanish"))
        self.flat_export_buttons["spanish"] = spanish_button
        spanish_path_label = QLabel()
        spanish_path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        spanish_status_label = QLabel()
        self.flat_export_path_labels["spanish"] = spanish_path_label
        self.flat_export_status_labels["spanish"] = spanish_status_label
        grid.addWidget(spanish_button, 2, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        grid.addWidget(spanish_path_label, 2, 1)
        grid.addWidget(spanish_status_label, 2, 2)

        technical_button = QPushButton(self.export_technical_flat_button_text)
        technical_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        technical_button.clicked.connect(lambda: self.on_export_flat_cards("technical"))
        self.flat_export_buttons["technical"] = technical_button
        technical_path_label = QLabel()
        technical_path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        technical_status_label = QLabel()
        self.flat_export_path_labels["technical"] = technical_path_label
        self.flat_export_status_labels["technical"] = technical_status_label
        grid.addWidget(technical_button, 3, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        grid.addWidget(technical_path_label, 3, 1)
        grid.addWidget(technical_status_label, 3, 2)

        layout.addLayout(grid)
        return box

    def _build_step_legend(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(18)
        layout.addWidget(self._build_legend_item("#f3f4f6", "#cfd4dc", self.legend_pending_text))
        layout.addWidget(self._build_legend_item("#dbeafe", "#7aa2e3", self.legend_active_text))
        layout.addWidget(self._build_legend_item("#dcfce7", "#7ecb99", self.legend_completed_text))
        layout.addStretch(1)
        return layout

    def _build_legend_item(self, fill_color: str, border_color: str, text: str) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        swatch = QLabel()
        swatch.setFixedSize(28, 18)
        swatch.setStyleSheet(
            f"background-color: {fill_color}; border: 1px solid {border_color}; border-radius: 4px;"
        )
        layout.addWidget(swatch)

        text_label = QLabel(text)
        text_label.setStyleSheet("color: #4b5563;")
        layout.addWidget(text_label)
        return widget

    def _build_log_box(self) -> QGroupBox:
        box = QGroupBox(self.log_group_text)
        layout = QVBoxLayout(box)
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)
        return box

    def refresh_status(self) -> None:
        self._recompute_step_states()
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
        self._refresh_flat_export_statuses()

    def on_prepare_structure(self) -> None:
        self._start_action_progress(self.progress_prepare_text, "prepare")
        try:
            created = self.workspace.prepare_structure(progress=self._update_progress)
        except OSError as exc:
            self._finish_action_progress("prepare")
            QMessageBox.critical(self, self.error_title_text, self.workspace_prepare_failed_text.format(error=exc))
            self._log(self.error_log_text.format(error=exc))
            return

        if created:
            for path in created:
                self._log(self.created_folder_log_text.format(path=path))
        else:
            self._log(self.no_folders_created_log_text)

        self._complete_action_progress(self.progress_completed_text, "prepare")
        self.refresh_status()
        QMessageBox.information(self, self.workspace_ready_title_text, self.workspace_ready_message_text)

    def on_extract_main_fonts(self) -> None:
        self._start_action_progress(self.progress_extract_text, "extract")
        try:
            summary, _ = self.extraction_service.extract_to_main_album(log=self._log, progress=self._update_progress)
        except FileNotFoundError as exc:
            self._finish_action_progress("extract")
            QMessageBox.warning(self, self.no_packages_title_text, str(exc))
            self._log(self.warning_log_text.format(error=exc))
            return
        except subprocess.CalledProcessError as exc:  # type: ignore[name-defined]
            self._finish_action_progress("extract")
            QMessageBox.critical(self, self.error_title_text, self.external_tool_failed_text.format(error=exc))
            self._log(self.error_log_text.format(error=exc))
            return
        except OSError as exc:
            self._finish_action_progress("extract")
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
        self._invalidate_step_states(("analyze", "html", "cards"))
        self._complete_action_progress(self.progress_completed_text, "extract")
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
        self._start_action_progress(self.progress_analyze_text, "analyze")
        try:
            summary, _ = self.analysis_service.analyze_main_collection(log=self._log, progress=self._update_progress)
        except FileNotFoundError as exc:
            self._finish_action_progress("analyze")
            QMessageBox.warning(self, self.master_missing_title_text, str(exc))
            self._log(self.warning_log_text.format(error=exc))
            return
        except subprocess.CalledProcessError as exc:
            self._finish_action_progress("analyze")
            QMessageBox.critical(self, self.error_title_text, self.external_tool_failed_text.format(error=exc))
            self._log(self.error_log_text.format(error=exc))
            return
        except OSError as exc:
            self._finish_action_progress("analyze")
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
        self._invalidate_step_states(("html", "cards"))
        self._complete_action_progress(self.progress_completed_text, "analyze")
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
        self._start_action_progress(self.progress_html_text, "html")
        try:
            summaries = self.html_generation_service.generate_all_albums(log=self._log, progress=self._update_progress)
        except FileNotFoundError as exc:
            self._finish_action_progress("html")
            QMessageBox.warning(self, self.html_missing_title_text, str(exc))
            self._log(self.warning_log_text.format(error=exc))
            return
        except subprocess.CalledProcessError as exc:
            self._finish_action_progress("html")
            QMessageBox.critical(self, self.error_title_text, self.external_tool_failed_text.format(error=exc))
            self._log(self.error_log_text.format(error=exc))
            return
        except OSError as exc:
            self._finish_action_progress("html")
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

        self._complete_action_progress(self.progress_completed_text, "html")
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
        self._start_action_progress(self.progress_cards_text, "cards")
        try:
            summaries = self.card_generation_service.generate_all_albums(log=self._log, progress=self._update_progress)
        except FileNotFoundError as exc:
            self._finish_action_progress("cards")
            QMessageBox.warning(self, self.html_missing_title_text, str(exc))
            self._log(self.warning_log_text.format(error=exc))
            return
        except subprocess.CalledProcessError as exc:
            self._finish_action_progress("cards")
            QMessageBox.critical(self, self.error_title_text, self.external_tool_failed_text.format(error=exc))
            self._log(self.error_log_text.format(error=exc))
            return
        except (OSError, RuntimeError) as exc:
            self._finish_action_progress("cards")
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

        self._complete_action_progress(self.progress_completed_text, "cards")
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

    def on_show_about(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle(self.about_title_text)
        dialog.setModal(True)
        dialog.resize(760, 360)

        layout = QHBoxLayout(dialog)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)

        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon = self.windowIcon()
        if not icon.isNull():
            icon_label.setPixmap(icon.pixmap(220, 220))
        icon_label.setMinimumWidth(240)
        layout.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignCenter)

        info_label = QLabel(
            "<div>"
            "<p><b>FontGallery</b></p>"
            f"<p>{self.about_description_text}</p>"
            "<p>"
            "Copyright: © 2026 Washington Indacochea Delgado<br/>"
            f"{self.about_email_label_text}: <a href=\"mailto:linuxfrontier@proton.me\">linuxfrontier@proton.me</a><br/>"
            f"{self.about_license_label_text}: GPL3<br/>"
            f"{self.about_website_label_text}: <a href=\"https://github.com/wachin/FontGallery\">https://github.com/wachin/FontGallery</a>"
            "</p>"
            f"<p><b>{self.about_technologies_title_text}</b><br/>{self.about_technologies_text}</p>"
            "</div>"
        )
        info_label.setWordWrap(True)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        info_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextBrowserInteraction | Qt.TextInteractionFlag.LinksAccessibleByMouse
        )
        info_label.setOpenExternalLinks(True)
        info_label.setMinimumWidth(420)
        layout.addWidget(info_label, 1)

        dialog.exec()

    def on_export_flat_cards(self, label: str) -> None:
        label_text = self.album_labels_text.get(label, label)
        self._start_action_progress(
            self.tr("Copying {label} PNG cards into one root folder...").format(label=label_text),
            "cards",
        )
        try:
            summary = self.flat_card_export_service.export_album(
                label=label,
                log=self._log,
                progress=self._update_progress,
            )
        except (FileNotFoundError, OSError, ValueError) as exc:
            self._finish_action_progress("cards")
            QMessageBox.critical(self, self.error_title_text, self.flat_export_failed_text.format(error=exc))
            self._log(self.error_log_text.format(error=exc))
            return

        self._complete_action_progress(self.progress_completed_text, "cards")
        self.refresh_status()
        QMessageBox.information(
            self,
            self.flat_export_completed_title_text,
            self.flat_export_completed_message_text.format(
                count=summary.copied_cards,
                path=summary.output_dir,
            ),
        )

    def _log(self, message: str) -> None:
        self.log_output.append(message)

    def _set_actions_enabled(self, enabled: bool) -> None:
        for button in self.action_buttons:
            button.setEnabled(enabled)
        self._refresh_flat_export_buttons(enabled)

    def _start_action_progress(self, label: str, step_key: str) -> None:
        self._set_actions_enabled(False)
        self.step_states[step_key] = "active"
        self._refresh_step_button_styles()
        self.progress_label.setText(label)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%v/%m (%p%)")
        QApplication.processEvents()

    def _update_progress(self, current: int, total: int, label: str) -> None:
        safe_total = max(total, 1)
        safe_value = min(max(current, 0), safe_total)
        self.progress_label.setText(label)
        self.progress_bar.setRange(0, safe_total)
        self.progress_bar.setValue(safe_value)
        self.progress_bar.setFormat("%v/%m (%p%)")
        QApplication.processEvents()

    def _complete_action_progress(self, label: str, step_key: str) -> None:
        maximum = max(self.progress_bar.maximum(), 1)
        self.progress_bar.setRange(0, maximum)
        self.progress_bar.setValue(maximum)
        self.progress_label.setText(label)
        self.step_states[step_key] = "completed"
        self._refresh_step_button_styles()
        QApplication.processEvents()
        self._set_actions_enabled(True)

    def _finish_action_progress(self, step_key: str) -> None:
        if self.step_states.get(step_key) == "active":
            self.step_states[step_key] = "pending"
        self._refresh_step_button_styles()
        self.progress_label.setText(self.progress_idle_text)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%v/%m (%p%)")
        self._set_actions_enabled(True)
        QApplication.processEvents()

    def _invalidate_step_states(self, step_keys: tuple[str, ...]) -> None:
        for step_key in step_keys:
            self.step_states[step_key] = "pending"
        self._refresh_step_button_styles()

    def _recompute_step_states(self) -> None:
        states = {
            "prepare": self._is_workspace_prepared(),
            "extract": self._has_generated_files(self.workspace.album_main_extract_dir),
            "analyze": (
                self._has_generated_files(self.workspace.album_es_extract_dir)
                or self._has_generated_files(self.workspace.album_tech_extract_dir)
            ),
            "html": self._has_generated_html_outputs(),
            "cards": self._has_generated_card_outputs(),
        }
        for step_key, is_completed in states.items():
            self.step_states[step_key] = "completed" if is_completed else "pending"
        self._refresh_step_button_styles()
        self._refresh_flat_export_buttons(all(button.isEnabled() for button in self.action_buttons))

    def _is_workspace_prepared(self) -> bool:
        return all(item.path.exists() and item.path.is_dir() for item in self.workspace.required_directories)

    def _has_generated_html_outputs(self) -> bool:
        return any(
            html_path.exists() and html_path.is_file()
            for html_path in (
                self.workspace.album_main_html_path,
                self.workspace.album_es_html_path,
                self.workspace.album_tech_html_path,
            )
        )

    def _has_generated_card_outputs(self) -> bool:
        return any(
            self._has_generated_files(cards_dir)
            for cards_dir in (
                self.workspace.album_main_cards_dir,
                self.workspace.album_es_cards_dir,
                self.workspace.album_tech_cards_dir,
            )
        )

    def _has_generated_files(self, directory: Path) -> bool:
        if not directory.exists() or not directory.is_dir():
            return False
        return any(path.is_file() for path in directory.rglob("*"))

    def _refresh_flat_export_buttons(self, actions_enabled: bool) -> None:
        available = {
            "main": self._has_generated_files(self.workspace.album_main_cards_dir),
            "spanish": self._has_generated_files(self.workspace.album_es_cards_dir),
            "technical": self._has_generated_files(self.workspace.album_tech_cards_dir),
        }
        for label, button in self.flat_export_buttons.items():
            button.setEnabled(actions_enabled and available[label])

    def _refresh_flat_export_statuses(self) -> None:
        flat_dirs = {
            "main": self.workspace.album_main_flat_cards_dir,
            "spanish": self.workspace.album_es_flat_cards_dir,
            "technical": self.workspace.album_tech_flat_cards_dir,
        }
        for label, directory in flat_dirs.items():
            path_label = self.flat_export_path_labels[label]
            status_label = self.flat_export_status_labels[label]
            path_label.setText(self._elide_path_from_start(directory))
            path_label.setToolTip(str(directory))
            if directory.exists():
                status_label.setText(self.exists_text)
                status_label.setStyleSheet("color: #0a7f2e; font-weight: 600;")
            else:
                status_label.setText(self.missing_text)
                status_label.setStyleSheet("color: #a33; font-weight: 600;")

    def _elide_path_from_start(self, path: Path, max_chars: int = 78) -> str:
        text = str(path)
        if len(text) <= max_chars:
            return text
        return "..." + text[-(max_chars - 3):]

    def _refresh_step_button_styles(self) -> None:
        styles = {
            "pending": "background-color: #f3f4f6; color: #1f2937; border: 1px solid #cfd4dc; padding: 6px 10px;",
            "active": "background-color: #dbeafe; color: #0f3d91; border: 1px solid #7aa2e3; padding: 6px 10px;",
            "completed": "background-color: #dcfce7; color: #166534; border: 1px solid #7ecb99; padding: 6px 10px;",
        }
        for step_key, button in self.step_buttons.items():
            button.setStyleSheet(styles[self.step_states.get(step_key, "pending")])
