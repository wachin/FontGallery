from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PyQt6.QtCore import QCoreApplication


@dataclass(frozen=True)
class ManagedPath:
    key: str
    label: str
    path: Path


@dataclass(frozen=True)
class WorkspaceScheme:
    language: str
    packages_dirname: str
    album_main_dirname: str
    album_es_dirname: str
    album_tech_dirname: str
    album_main_cards_dirname: str
    album_es_cards_dirname: str
    album_tech_cards_dirname: str
    album_main_flat_cards_dirname: str
    album_es_flat_cards_dirname: str
    album_tech_flat_cards_dirname: str
    album_main_html_name: str
    album_es_html_name: str
    album_tech_html_name: str
    extracted_dirname: str


WORKSPACE_SCHEMES = {
    "en": WorkspaceScheme(
        language="en",
        packages_dirname="deb-packages",
        album_main_dirname="font-album",
        album_es_dirname="spanish-font-album",
        album_tech_dirname="technical-font-album",
        album_main_cards_dirname="font-cards",
        album_es_cards_dirname="spanish-font-cards",
        album_tech_cards_dirname="technical-font-cards",
        album_main_flat_cards_dirname="font-cards-root",
        album_es_flat_cards_dirname="spanish-font-cards-root",
        album_tech_flat_cards_dirname="technical-font-cards-root",
        album_main_html_name="font-album.html",
        album_es_html_name="spanish-font-album.html",
        album_tech_html_name="technical-font-album.html",
        extracted_dirname="extracted-fonts",
    ),
    "es": WorkspaceScheme(
        language="es",
        packages_dirname="paquetes-deb",
        album_main_dirname="album-fuentes",
        album_es_dirname="album-fuentes-espanol",
        album_tech_dirname="album-fuentes-tecnicas",
        album_main_cards_dirname="tarjetas-fuentes",
        album_es_cards_dirname="tarjetas-fuentes-espanol",
        album_tech_cards_dirname="tarjetas-fuentes-tecnicas",
        album_main_flat_cards_dirname="tarjetas-fuentes-raiz",
        album_es_flat_cards_dirname="tarjetas-fuentes-espanol-raiz",
        album_tech_flat_cards_dirname="tarjetas-fuentes-tecnicas-raiz",
        album_main_html_name="album-fuentes.html",
        album_es_html_name="album-fuentes-espanol.html",
        album_tech_html_name="album-fuentes-tecnicas.html",
        extracted_dirname="fuentes-extraidas",
    ),
}


def normalize_language(language_code: str | None) -> str:
    if not language_code:
        return "en"
    prefix = language_code.split("_", 1)[0].split("-", 1)[0].lower()
    return "es" if prefix == "es" else "en"


class WorkspaceService:
    def __init__(self, project_root: Path, language_code: str | None = None) -> None:
        self._project_root = project_root.resolve()
        self._preferred_language = normalize_language(language_code)
        self._preferred_scheme = WORKSPACE_SCHEMES[self._preferred_language]
        self._paths = self._resolve_paths()

    @property
    def project_root(self) -> Path:
        return self._project_root

    @property
    def language(self) -> str:
        return self._preferred_language

    @property
    def preferred_scheme(self) -> WorkspaceScheme:
        return self._preferred_scheme

    @property
    def managed_paths(self) -> list[ManagedPath]:
        return [
            ManagedPath("packages", "Packages", self._paths["packages"]),
            ManagedPath("album_main", "Main album", self._paths["album_main"]),
            ManagedPath("album_es", "Spanish album", self._paths["album_es"]),
            ManagedPath("album_tech", "Technical album", self._paths["album_tech"]),
        ]

    @property
    def status_paths(self) -> list[ManagedPath]:
        return [
            *self.managed_paths,
            ManagedPath("album_main_cards", "Main cards", self.album_main_cards_dir),
            ManagedPath("album_es_cards", "Spanish cards", self.album_es_cards_dir),
            ManagedPath("album_tech_cards", "Technical cards", self.album_tech_cards_dir),
        ]

    @property
    def required_directories(self) -> list[ManagedPath]:
        return [
            *self.managed_paths,
            ManagedPath("album_main_extract", "Main extracted fonts", self.album_main_extract_dir),
            ManagedPath("album_es_extract", "Spanish extracted fonts", self.album_es_extract_dir),
            ManagedPath("album_tech_extract", "Technical extracted fonts", self.album_tech_extract_dir),
            ManagedPath("album_main_cards", "Main cards", self.album_main_cards_dir),
            ManagedPath("album_es_cards", "Spanish cards", self.album_es_cards_dir),
            ManagedPath("album_tech_cards", "Technical cards", self.album_tech_cards_dir),
        ]

    @property
    def packages_dir(self) -> Path:
        return self._paths["packages"]

    @property
    def album_main_dir(self) -> Path:
        return self._paths["album_main"]

    @property
    def album_es_dir(self) -> Path:
        return self._paths["album_es"]

    @property
    def album_tech_dir(self) -> Path:
        return self._paths["album_tech"]

    @property
    def album_main_extract_dir(self) -> Path:
        scheme = self._scheme_for_album_dir(self.album_main_dir, "album_main")
        return self._resolve_child_existing_or_preferred(
            parent=self.album_main_dir,
            preferred_name=scheme.extracted_dirname,
            candidate_names=[scheme.extracted_dirname for scheme in WORKSPACE_SCHEMES.values()],
        )

    @property
    def album_es_extract_dir(self) -> Path:
        scheme = self._scheme_for_album_dir(self.album_es_dir, "album_es")
        return self._resolve_child_existing_or_preferred(
            parent=self.album_es_dir,
            preferred_name=scheme.extracted_dirname,
            candidate_names=[scheme.extracted_dirname for scheme in WORKSPACE_SCHEMES.values()],
        )

    @property
    def album_tech_extract_dir(self) -> Path:
        scheme = self._scheme_for_album_dir(self.album_tech_dir, "album_tech")
        return self._resolve_child_existing_or_preferred(
            parent=self.album_tech_dir,
            preferred_name=scheme.extracted_dirname,
            candidate_names=[scheme.extracted_dirname for scheme in WORKSPACE_SCHEMES.values()],
        )

    @property
    def album_main_html_path(self) -> Path:
        scheme = self._scheme_for_album_dir(self.album_main_dir, "album_main")
        return self._resolve_child_existing_or_preferred(
            parent=self.album_main_dir,
            preferred_name=scheme.album_main_html_name,
            candidate_names=[scheme.album_main_html_name for scheme in WORKSPACE_SCHEMES.values()],
        )

    @property
    def album_es_html_path(self) -> Path:
        scheme = self._scheme_for_album_dir(self.album_es_dir, "album_es")
        return self._resolve_child_existing_or_preferred(
            parent=self.album_es_dir,
            preferred_name=scheme.album_es_html_name,
            candidate_names=[scheme.album_es_html_name for scheme in WORKSPACE_SCHEMES.values()],
        )

    @property
    def album_tech_html_path(self) -> Path:
        scheme = self._scheme_for_album_dir(self.album_tech_dir, "album_tech")
        return self._resolve_child_existing_or_preferred(
            parent=self.album_tech_dir,
            preferred_name=scheme.album_tech_html_name,
            candidate_names=[scheme.album_tech_html_name for scheme in WORKSPACE_SCHEMES.values()],
        )

    @property
    def album_main_cards_dir(self) -> Path:
        scheme = self._scheme_for_album_dir(self.album_main_dir, "album_main")
        return self._resolve_child_existing_or_preferred(
            parent=self.album_main_dir,
            preferred_name=scheme.album_main_cards_dirname,
            candidate_names=[scheme.album_main_cards_dirname for scheme in WORKSPACE_SCHEMES.values()],
        )

    @property
    def album_es_cards_dir(self) -> Path:
        scheme = self._scheme_for_album_dir(self.album_es_dir, "album_es")
        return self._resolve_child_existing_or_preferred(
            parent=self.album_es_dir,
            preferred_name=scheme.album_es_cards_dirname,
            candidate_names=[scheme.album_es_cards_dirname for scheme in WORKSPACE_SCHEMES.values()],
        )

    @property
    def album_tech_cards_dir(self) -> Path:
        scheme = self._scheme_for_album_dir(self.album_tech_dir, "album_tech")
        return self._resolve_child_existing_or_preferred(
            parent=self.album_tech_dir,
            preferred_name=scheme.album_tech_cards_dirname,
            candidate_names=[scheme.album_tech_cards_dirname for scheme in WORKSPACE_SCHEMES.values()],
        )

    @property
    def album_main_flat_cards_dir(self) -> Path:
        scheme = self._scheme_for_album_dir(self.album_main_dir, "album_main")
        return self._resolve_child_existing_or_preferred(
            parent=self.album_main_dir,
            preferred_name=scheme.album_main_flat_cards_dirname,
            candidate_names=[scheme.album_main_flat_cards_dirname for scheme in WORKSPACE_SCHEMES.values()],
        )

    @property
    def album_es_flat_cards_dir(self) -> Path:
        scheme = self._scheme_for_album_dir(self.album_es_dir, "album_es")
        return self._resolve_child_existing_or_preferred(
            parent=self.album_es_dir,
            preferred_name=scheme.album_es_flat_cards_dirname,
            candidate_names=[scheme.album_es_flat_cards_dirname for scheme in WORKSPACE_SCHEMES.values()],
        )

    @property
    def album_tech_flat_cards_dir(self) -> Path:
        scheme = self._scheme_for_album_dir(self.album_tech_dir, "album_tech")
        return self._resolve_child_existing_or_preferred(
            parent=self.album_tech_dir,
            preferred_name=scheme.album_tech_flat_cards_dirname,
            candidate_names=[scheme.album_tech_flat_cards_dirname for scheme in WORKSPACE_SCHEMES.values()],
        )

    def path_status(self) -> list[dict[str, str | bool]]:
        statuses: list[dict[str, str | bool]] = []
        for item in self.status_paths:
            statuses.append(
                {
                    "key": item.key,
                    "label": item.label,
                    "path": str(item.path),
                    "exists": item.path.exists(),
                    "writable": self._is_writable_target(item.path),
                }
            )
        return statuses

    def prepare_structure(
        self,
        progress: Callable[[int, int, str], None] | None = None,
    ) -> list[Path]:
        created: list[Path] = []
        total = len(self.required_directories)
        for index, item in enumerate(self.required_directories, start=1):
            self._ensure_writable(item.path)
            if not item.path.exists():
                item.path.mkdir(parents=True, exist_ok=True)
                created.append(item.path)
            if progress is not None:
                progress(
                    index,
                    total,
                    QCoreApplication.translate(
                        "WorkspaceService",
                        "Verified workspace path: {path}",
                    ).format(path=item.path),
                )
        return created

    def deb_package_count(self) -> int:
        if not self.packages_dir.exists():
            return 0
        return sum(1 for path in self.packages_dir.iterdir() if path.is_file() and path.suffix == ".deb")

    def _resolve_paths(self) -> dict[str, Path]:
        preferred = self._preferred_scheme
        return {
            "packages": self._resolve_existing_or_preferred(
                preferred_name=preferred.packages_dirname,
                candidate_names=[scheme.packages_dirname for scheme in WORKSPACE_SCHEMES.values()],
            ),
            "album_main": self._resolve_existing_or_preferred(
                preferred_name=preferred.album_main_dirname,
                candidate_names=[scheme.album_main_dirname for scheme in WORKSPACE_SCHEMES.values()],
            ),
            "album_es": self._resolve_existing_or_preferred(
                preferred_name=preferred.album_es_dirname,
                candidate_names=[scheme.album_es_dirname for scheme in WORKSPACE_SCHEMES.values()],
            ),
            "album_tech": self._resolve_existing_or_preferred(
                preferred_name=preferred.album_tech_dirname,
                candidate_names=[scheme.album_tech_dirname for scheme in WORKSPACE_SCHEMES.values()],
            ),
        }

    def _resolve_existing_or_preferred(
        self,
        preferred_name: str,
        candidate_names: list[str],
    ) -> Path:
        preferred_path = self._project_root / preferred_name
        if preferred_path.exists():
            return preferred_path

        for name in candidate_names:
            candidate = self._project_root / name
            if candidate.exists():
                return candidate

        return preferred_path

    def _resolve_child_existing_or_preferred(
        self,
        parent: Path,
        preferred_name: str,
        candidate_names: list[str],
    ) -> Path:
        preferred_path = parent / preferred_name
        if preferred_path.exists():
            return preferred_path

        for name in candidate_names:
            candidate = parent / name
            if candidate.exists():
                return candidate

        return preferred_path

    def _scheme_for_album_dir(self, album_dir: Path, key: str) -> WorkspaceScheme:
        for scheme in WORKSPACE_SCHEMES.values():
            dirname = {
                "album_main": scheme.album_main_dirname,
                "album_es": scheme.album_es_dirname,
                "album_tech": scheme.album_tech_dirname,
            }[key]
            if album_dir.name == dirname:
                return scheme
        return self._preferred_scheme

    def _is_writable_target(self, path: Path) -> bool:
        candidate = path if path.exists() else self._nearest_existing_parent(path)
        if candidate is None or not candidate.is_dir():
            return False
        return os.access(candidate, os.W_OK | os.X_OK)

    def _nearest_existing_parent(self, path: Path) -> Path | None:
        current = path
        while not current.exists():
            if current == current.parent:
                return None
            current = current.parent
        return current

    def _ensure_writable(self, path: Path) -> None:
        if path.exists():
            if not path.is_dir():
                raise OSError(
                    QCoreApplication.translate(
                        "WorkspaceService",
                        "Expected a directory but found a file: {path}",
                    ).format(path=path)
                )
            if not self._is_writable_target(path):
                raise PermissionError(
                    QCoreApplication.translate(
                        "WorkspaceService",
                        "Directory is not writable: {path}",
                    ).format(path=path)
                )
            return

        parent = self._nearest_existing_parent(path.parent)
        if parent is None or not parent.is_dir() or not self._is_writable_target(parent):
            raise PermissionError(
                QCoreApplication.translate(
                    "WorkspaceService",
                    "Cannot create directory '{path}' because its parent is not writable: {parent}",
                ).format(path=path, parent=parent or path.parent)
            )
