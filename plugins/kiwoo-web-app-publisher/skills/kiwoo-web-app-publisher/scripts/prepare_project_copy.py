#!/usr/bin/env python3
"""Create an isolated, editable copy of a project under its own .loot directory."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path


WORKSPACES_DIR = Path(".loot") / "deploy-workspaces"
WORKSPACE_PREFIX = "workspace-"

# Dependency and cache directories are regenerated and safe to exclude at every depth.
# Excluding .loot is also what prevents a destination nested under the source from
# recursively copying itself.
RECURSIVE_EXCLUDED_NAMES = frozenset(
    {
        ".git",
        ".hg",
        ".loot",
        ".next",
        ".nuxt",
        ".output",
        ".svn",
        ".venv",
        "__pycache__",
        "node_modules",
    }
)

# These conventional build-output names are ambiguous in nested source trees (for
# example src/utils/dist/helper.ts), so exclude them only at the project root.
ROOT_ONLY_EXCLUDED_NAMES = frozenset({"coverage", "dist"})
EXCLUDED_NAMES = RECURSIVE_EXCLUDED_NAMES | ROOT_ONLY_EXCLUDED_NAMES


class PrepareProjectCopyError(RuntimeError):
    pass


def _ignore_names(project_root: Path, directory: str, names: list[str]) -> set[str]:
    excluded = RECURSIVE_EXCLUDED_NAMES
    if Path(directory).resolve() == project_root:
        excluded = EXCLUDED_NAMES
    return {name for name in names if name in excluded}


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _validate_symlink_targets(project: Path) -> None:
    """Reject links that would materialize content from outside the project."""

    for directory, directory_names, file_names in os.walk(
        project, topdown=True, followlinks=False
    ):
        excluded = _ignore_names(
            project, directory, [*directory_names, *file_names]
        )
        directory_names[:] = [
            name for name in directory_names if name not in excluded
        ]

        current = Path(directory)
        for name in [*directory_names, *file_names]:
            if name in excluded:
                continue
            candidate = current / name
            if not candidate.is_symlink():
                continue
            target = candidate.resolve(strict=True)
            if not _is_within(target, project):
                relative = candidate.relative_to(project)
                raise PrepareProjectCopyError(
                    f"项目包含指向项目目录外部的符号链接，已停止复制：{relative}"
                )


def prepare_project_copy(project_dir: Path) -> Path:
    project = project_dir.expanduser().resolve()
    if not project.is_dir():
        raise PrepareProjectCopyError(f"项目目录不存在：{project}")

    _validate_symlink_targets(project)

    workspaces_root = project / WORKSPACES_DIR
    workspaces_root.mkdir(parents=True, exist_ok=True)
    workspace_ignore = workspaces_root / ".gitignore"
    if not workspace_ignore.exists():
        workspace_ignore.write_text("*\n!.gitignore\n", encoding="utf-8")
    workspace = Path(
        tempfile.mkdtemp(prefix=WORKSPACE_PREFIX, dir=str(workspaces_root))
    )
    try:
        shutil.copytree(
            project,
            workspace,
            dirs_exist_ok=True,
            ignore=lambda directory, names: _ignore_names(project, directory, names),
            # Dereference symlinks so editing a copied path cannot mutate its
            # original target outside the workspace. A dangling link is an explicit
            # copy failure rather than a silently missing file in the build workspace.
            symlinks=False,
            ignore_dangling_symlinks=False,
        )
    except Exception:
        # This directory was created by this invocation and cannot contain earlier
        # user edits. Clean up only that exact fresh destination on copy failure.
        shutil.rmtree(workspace, ignore_errors=True)
        raise
    return workspace


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="在原项目 .loot/deploy-workspaces 下创建独立可编辑副本"
    )
    parser.add_argument("--project-dir", required=True, type=Path, help="原项目目录")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        workspace = prepare_project_copy(args.project_dir)
    except (OSError, PrepareProjectCopyError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "project_dir": str(args.project_dir.expanduser().resolve()),
                "workspace_dir": str(workspace),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
