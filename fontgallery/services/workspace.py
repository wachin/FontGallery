from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


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

    def path_status(self) -> list[dict[str, str | bool]]:
        statuses: list[dict[str, str | bool]] = []
        for item in self.managed_paths:
            statuses.append(
                {
                    "key": item.key,
                    "label": item.label,
                    "path": str(item.path),
                    "exists": item.path.exists(),
                    "writable": item.path.exists() and item.path.is_dir() and item.path.stat() is not None,
                }
            )
        return statuses

    def prepare_structure(self) -> list[Path]:
        created: list[Path] = []
        for item in self.managed_paths:
            if not item.path.exists():
                item.path.mkdir(parents=True, exist_ok=True)
                created.append(item.path)
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
