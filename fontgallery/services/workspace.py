from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ManagedPath:
    key: str
    label: str
    path: Path


class WorkspaceService:
    def __init__(self, project_root: Path) -> None:
        self._project_root = project_root.resolve()

    @property
    def project_root(self) -> Path:
        return self._project_root

    @property
    def managed_paths(self) -> list[ManagedPath]:
        root = self._project_root
        return [
            ManagedPath("packages", "Paquetes .deb", root / "paquetes-deb"),
            ManagedPath("album_main", "Album principal", root / "album-fuentes"),
            ManagedPath("album_es", "Album español", root / "album-fuentes-espanol"),
            ManagedPath("album_tech", "Album técnico", root / "album-fuentes-tecnicas"),
        ]

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
        packages_dir = self._project_root / "paquetes-deb"
        if not packages_dir.exists():
            return 0
        return sum(1 for path in packages_dir.iterdir() if path.is_file() and path.suffix == ".deb")
