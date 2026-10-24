#!/usr/bin/env python3
# ruff: noqa: EXE001
"""通过 Kiwoo 部署接口把单文件 HTML 预览成草稿、并落库到「我的创作」。

纯标准库实现，零 pip 依赖（不同于灵光的 qrcode 依赖）。子命令：

- ``configure``：把部署令牌安全写入平台原生配置文件（从 stdin 读取，绝不走 argv）。
- ``preview``：上传单文件 HTML，建/更新草稿并签发 10 分钟预览链接。
- ``deploy``：把最终 HTML 落成草稿（始终 status=0），返回工作台链接。

部署令牌只经 ``Authorization: Bearer`` 头发送；绝不写进命令行参数、日志或诊断输出。
"""

from __future__ import annotations

import argparse
import http.client
import json
import os
import stat
import sys
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

DEFAULT_API_BASE = "https://loot.alrite.fun"
API_BASE_ENV = "LOOT_API_BASE"
TOKEN_ENV = "LOOT_DEPLOY_TOKEN"
APP_DIRECTORY_NAME = "loot-flash-apps"
CONFIG_FILE_NAME = "config.json"
CONFIG_TOKEN_FIELD = "deploy_token"
TOKEN_PREFIX = "loot_deploy_"
TOKEN_SETTINGS_HINT = "在 Kiwoo 个人中心「获取安装口令」处生成部署 token"

ARTIFACT_DIR_NAME = ".loot"
ARTIFACT_FILE_NAME = "loot-artifact.json"

PREVIEW_PATH = "/api/deploy/preview"
COMMIT_PATH = "/api/deploy/commit"

SKILL_NAME = "loot-flash-apps"
SKILL_VERSION = "1.1.1"
SKILL_VERSION_HEADER = "X-Loot-Skill-Version"
USER_AGENT = f"loot-flash-apps-cli/{SKILL_VERSION}"

EXIT_USAGE_OR_CONFIG = 2
EXIT_TRANSPORT = 3
EXIT_API = 4


# --------------------------------------------------------------------------- #
# 平台原生路径
# --------------------------------------------------------------------------- #
def default_config_path(
    *,
    environ: Mapping[str, str] | None = None,
    home: Path | None = None,
    platform_name: str | None = None,
) -> Path:
    """返回平台原生的按用户配置路径。"""
    environment = os.environ if environ is None else environ
    user_home = Path.home() if home is None else home
    platform = os.name if platform_name is None else platform_name
    if platform == "nt":
        configured_root = environment.get("APPDATA", "").strip()
        root = Path(configured_root) if configured_root else user_home / "AppData/Roaming"
    else:
        configured_root = environment.get("XDG_CONFIG_HOME", "").strip()
        root = (
            Path(configured_root).expanduser()
            if configured_root
            else user_home / ".config"
        )
    return root / APP_DIRECTORY_NAME / CONFIG_FILE_NAME


def legacy_config_path(*, home: Path | None = None) -> Path:
    """老版本统一使用的跨平台配置路径（供 Windows 回退读取）。"""
    user_home = Path.home() if home is None else home
    return user_home / ".config" / APP_DIRECTORY_NAME / CONFIG_FILE_NAME


DEFAULT_CONFIG_PATH = default_config_path()


def resolve_config_path(
    config_path: Path,
    *,
    environ: Mapping[str, str] | None = None,
    home: Path | None = None,
    platform_name: str | None = None,
) -> Path:
    """解析配置路径；Windows 原生路径不存在时回退老位置。"""
    path = config_path.expanduser()
    if path.is_file():
        return path
    platform = os.name if platform_name is None else platform_name
    if platform == "nt":
        native_default = default_config_path(
            environ=environ, home=home, platform_name=platform
        ).expanduser()
        if path == native_default:
            legacy = legacy_config_path(home=home).expanduser()
            if legacy.is_file():
                return legacy
    return path


def configure_standard_streams(
    *,
    platform_name: str | None = None,
    stdout: Any | None = None,
    stderr: Any | None = None,
) -> None:
    """在 Windows 终端用 UTF-8 输出 JSON 与中文诊断。"""
    platform = os.name if platform_name is None else platform_name
    if platform != "nt":
        return
    output_stream = sys.stdout if stdout is None else stdout
    error_stream = sys.stderr if stderr is None else stderr
    for stream in (output_stream, error_stream):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")


# --------------------------------------------------------------------------- #
# 错误类型与退出码
# --------------------------------------------------------------------------- #
class LootDeployError(Exception):
    exit_code = EXIT_API


class UsageError(LootDeployError):
    exit_code = EXIT_USAGE_OR_CONFIG


class ConfigError(LootDeployError):
    exit_code = EXIT_USAGE_OR_CONFIG


class ConfigPermissionError(ConfigError):
    pass


class TransportError(LootDeployError):
    exit_code = EXIT_TRANSPORT


class HttpApiError(LootDeployError):
    exit_code = EXIT_TRANSPORT


class ResponseFormatError(LootDeployError):
    exit_code = EXIT_API


class BusinessApiError(LootDeployError):
    exit_code = EXIT_API


# --------------------------------------------------------------------------- #
# 令牌处理
# --------------------------------------------------------------------------- #
def _redact(value: object, token: str) -> str:
    text = str(value)
    if token:
        text = text.replace(f"Bearer {token}", "Bearer [REDACTED]")
        text = text.replace(token, "[REDACTED]")
    return text


def _normalize_token(raw_token: str) -> str:
    token = raw_token.strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
    lowered = token.lower()
    if not token or lowered.startswith("replace-") or lowered in {
        "yourdeploytoken",
        "your-deploy-token",
    }:
        raise ConfigError(f"部署 token 仍是占位值；请{TOKEN_SETTINGS_HINT}")
    return token


def load_deploy_token(
    config_path: Path = DEFAULT_CONFIG_PATH,
    *,
    environ: Mapping[str, str] | None = None,
) -> str:
    """令牌优先级：环境变量 > 配置文件。绝不接受 CLI 参数传入。"""
    environment = os.environ if environ is None else environ
    env_token = environment.get(TOKEN_ENV, "").strip()
    if env_token:
        return _normalize_token(env_token)

    path = resolve_config_path(config_path, environ=environment)
    if not path.is_file():
        raise ConfigError(
            f"部署 token 配置不存在：{path}；请{TOKEN_SETTINGS_HINT}，"
            f"或先运行 configure 子命令写入"
        )

    if os.name == "posix":
        permissions = stat.S_IMODE(path.stat().st_mode)
        if permissions & 0o077:
            raise ConfigPermissionError(
                f"部署 token 配置不能对同组或其他用户可读：{path}；请执行 chmod 600"
            )

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"无法读取部署 token 配置：{path}：{exc}") from exc
    if not isinstance(payload, dict):
        raise ConfigError(f"部署 token 配置必须是 JSON 对象：{path}")
    raw_token = payload.get(CONFIG_TOKEN_FIELD)
    if not isinstance(raw_token, str) or not raw_token.strip():
        raise ConfigError(f"配置中缺少 {CONFIG_TOKEN_FIELD}：{path}")
    return _normalize_token(raw_token)


def write_deploy_token(config_path: Path, token: str) -> Path:
    """把令牌原子写入配置文件；POSIX 强制 0600。绝不打印令牌。"""
    normalized = _normalize_token(token)
    path = config_path.expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {CONFIG_TOKEN_FIELD: normalized}
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            if os.name == "posix":
                os.fchmod(handle.fileno(), 0o600)
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
            temporary_path = Path(handle.name)
        os.replace(temporary_path, path)
    except OSError as exc:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
        raise ConfigError(f"无法写入部署 token 配置：{path}：{exc}") from exc
    if os.name == "posix":
        os.chmod(path, 0o600)
    return path


# --------------------------------------------------------------------------- #
# 作品身份（work_id）持久化：.loot/loot-artifact.json
# --------------------------------------------------------------------------- #
def _project_directory(project_dir: Path) -> Path:
    path = project_dir.expanduser()
    if not path.is_dir():
        raise UsageError(f"项目目录不存在：{path}")
    return path


def _artifact_path(project_dir: Path) -> Path:
    return _project_directory(project_dir) / ARTIFACT_DIR_NAME / ARTIFACT_FILE_NAME


def load_artifact_work_id(project_dir: Path) -> str | None:
    path = _artifact_path(project_dir)
    if not path.exists():
        return None
    if not path.is_file():
        raise UsageError(f"作品身份路径不是文件：{path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise UsageError(f"无法读取作品身份：{path}：{exc}") from exc
    if not isinstance(payload, dict):
        raise UsageError(f"作品身份必须是 JSON 对象：{path}")
    if payload.get("schemaVersion") != 1:
        raise UsageError(f"作品身份必须使用 schemaVersion 1：{path}")
    work_id = payload.get("workId")
    if not isinstance(work_id, str) or not work_id.strip():
        raise UsageError(f"作品身份缺少非空 workId：{path}")
    return work_id.strip()


def write_artifact_work_id(project_dir: Path, work_id: str) -> Path:
    path = _artifact_path(project_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schemaVersion": 1, "workId": work_id}
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
            temporary_path = Path(handle.name)
        os.replace(temporary_path, path)
    except OSError as exc:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
        raise UsageError(f"无法写入作品身份：{path}：{exc}") from exc
    return path


def resolve_work_id(
    project_dir: Path,
    *,
    explicit_work_id: str | None,
    new_work: bool,
    required: bool,
) -> str | None:
    """确定本次操作的 work_id：显式 > 身份文件；``new_work`` 强制新建。"""
    if explicit_work_id and new_work:
        raise UsageError("--work-id 与 --new 互斥")
    if explicit_work_id is not None:
        work_id = explicit_work_id.strip()
        if not work_id:
            raise UsageError("--work-id 不能为空")
        return work_id
    if new_work:
        return None
    stored = load_artifact_work_id(project_dir)
    if stored is None and required:
        raise UsageError(
            f"未找到 {ARTIFACT_DIR_NAME}/{ARTIFACT_FILE_NAME}；请先运行 preview，"
            "或用 --work-id 指定作品"
        )
    return stored


# --------------------------------------------------------------------------- #
# HTML 读取
# --------------------------------------------------------------------------- #
def read_html_file(html_file: Path) -> str:
    path = html_file.expanduser()
    if not path.is_file():
        raise UsageError(f"HTML 文件不存在：{path}")
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise UsageError(f"无法读取 HTML 文件：{path}：{exc}") from exc
    if not text.strip():
        raise UsageError(f"HTML 文件为空：{path}")
    return text


# --------------------------------------------------------------------------- #
# HTTP 客户端
# --------------------------------------------------------------------------- #
def _require_nonempty_string(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ResponseFormatError(f"响应缺少非空字段 {key}")
    return value.strip()


class LootDeployClient:
    def __init__(self, deploy_token: str, *, base_url: str = DEFAULT_API_BASE):
        self.deploy_token = _normalize_token(deploy_token)
        parsed = urlparse(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ConfigError(f"无效的 API 地址：{base_url}")
        self.scheme = parsed.scheme
        self.hostname = parsed.hostname
        self.port = parsed.port
        self.base_path = parsed.path.rstrip("/")

    def _connection(self, timeout: float) -> http.client.HTTPConnection:
        connection_type = (
            http.client.HTTPSConnection
            if self.scheme == "https"
            else http.client.HTTPConnection
        )
        return connection_type(self.hostname, self.port, timeout=timeout)

    def _path(self, endpoint: str) -> str:
        return f"{self.base_path}{endpoint}"

    def _headers(self) -> dict[str, str]:
        # 只发送本 CLI 自己的上下文；绝不重放任何浏览器 Cookie / UA / sec-* 头。
        return {
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {self.deploy_token}",
            "User-Agent": USER_AGENT,
            SKILL_VERSION_HEADER: SKILL_VERSION,
        }

    def _read_response(
        self, response: http.client.HTTPResponse, *, operation: str
    ) -> dict[str, Any]:
        body = response.read()
        if not 200 <= response.status < 300:
            detail = self._extract_detail(body)
            raise HttpApiError(
                f"{operation} 返回 HTTP {response.status}"
                + (f"：{_redact(detail, self.deploy_token)}" if detail else "")
            )
        try:
            payload = json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ResponseFormatError(f"{operation} 返回的不是有效 JSON") from exc
        if not isinstance(payload, dict):
            raise ResponseFormatError(f"{operation} 响应必须是 JSON 对象")
        return payload

    @staticmethod
    def _extract_detail(body: bytes) -> str:
        try:
            parsed = json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return ""
        if isinstance(parsed, dict):
            detail = parsed.get("detail")
            if isinstance(detail, str):
                return detail
            if detail is not None:
                return json.dumps(detail, ensure_ascii=False)
        return ""

    def _post_json(
        self, endpoint: str, payload: dict[str, Any], *, operation: str, timeout: float
    ) -> dict[str, Any]:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = self._headers()
        headers["Content-Length"] = str(len(body))
        connection = self._connection(timeout)
        try:
            connection.request("POST", self._path(endpoint), body=body, headers=headers)
            response = connection.getresponse()
            return self._read_response(response, operation=operation)
        except LootDeployError:
            raise
        except (OSError, http.client.HTTPException) as exc:
            raise TransportError(
                f"{operation} 传输失败：{_redact(exc, self.deploy_token)}"
            ) from exc
        finally:
            connection.close()

    def preview(
        self,
        *,
        html: str,
        title: str | None,
        work_id: str | None,
        timeout: float,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"html": html}
        if title:
            payload["title"] = title
        if work_id:
            payload["work_id"] = work_id
        result = self._post_json(
            PREVIEW_PATH, payload, operation="preview", timeout=timeout
        )
        _require_nonempty_string(result, "work_id")
        _require_nonempty_string(result, "preview_url")
        return result

    def commit(
        self,
        *,
        work_id: str,
        html: str | None,
        title: str | None,
        timeout: float,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"work_id": work_id}
        if html is not None:
            payload["html"] = html
        if title:
            payload["title"] = title
        result = self._post_json(
            COMMIT_PATH, payload, operation="commit", timeout=timeout
        )
        _require_nonempty_string(result, "work_id")
        _require_nonempty_string(result, "workspace_url")
        return result


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _positive_timeout(value: str) -> float:
    try:
        timeout = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("timeout 必须是数字") from exc
    if timeout <= 0:
        raise argparse.ArgumentTypeError("timeout 必须大于 0")
    return timeout


def _resolve_base_url(
    explicit: str | None, *, environ: Mapping[str, str] | None = None
) -> str:
    environment = os.environ if environ is None else environ
    if explicit and explicit.strip():
        return explicit.strip()
    env_base = environment.get(API_BASE_ENV, "").strip()
    if env_base:
        return env_base
    return DEFAULT_API_BASE


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="通过 Kiwoo 部署接口预览单文件 HTML 并落成草稿。"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    configure_parser = subparsers.add_parser(
        "configure", help="把部署 token 写入平台配置（从 stdin 读取，不走 argv）"
    )
    configure_parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    configure_parser.add_argument(
        "--from-env",
        action="store_true",
        help=f"从环境变量 {TOKEN_ENV} 读取令牌，而非 stdin",
    )

    preview_parser = subparsers.add_parser(
        "preview", help="上传单文件 HTML，建/更新草稿并签发 10 分钟预览链接"
    )
    preview_parser.add_argument("--html-file", required=True, type=Path)
    preview_parser.add_argument("--title")
    preview_parser.add_argument("--work-id")
    preview_parser.add_argument(
        "--new", action="store_true", help="强制新建草稿（忽略本地作品身份）"
    )
    preview_parser.add_argument("--project-dir", type=Path, default=Path.cwd())
    preview_parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    preview_parser.add_argument("--api", help=f"API 根地址（默认 {DEFAULT_API_BASE}）")
    preview_parser.add_argument("--timeout", type=_positive_timeout, default=300.0)

    deploy_parser = subparsers.add_parser(
        "deploy", help="把最终 HTML 落成草稿（status=0），返回工作台链接"
    )
    deploy_parser.add_argument("--work-id")
    deploy_parser.add_argument(
        "--html-file", type=Path, help="最终 HTML；省略时按已有草稿直接落库"
    )
    deploy_parser.add_argument("--title")
    deploy_parser.add_argument("--project-dir", type=Path, default=Path.cwd())
    deploy_parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    deploy_parser.add_argument("--api", help=f"API 根地址（默认 {DEFAULT_API_BASE}）")
    deploy_parser.add_argument("--timeout", type=_positive_timeout, default=120.0)

    return parser


def _run_configure(
    args: argparse.Namespace, *, environ: Mapping[str, str] | None = None
) -> dict[str, Any]:
    environment = os.environ if environ is None else environ
    if args.from_env:
        raw = environment.get(TOKEN_ENV, "")
        if not raw.strip():
            raise ConfigError(f"环境变量 {TOKEN_ENV} 为空")
    else:
        raw = sys.stdin.read()
        if not raw.strip():
            raise ConfigError("stdin 未读到部署 token")
    path = write_deploy_token(args.config, raw)
    # 只回执路径，绝不回显令牌。
    return {"configured": True, "config_path": str(path)}


def _run_preview(
    args: argparse.Namespace, *, environ: Mapping[str, str] | None = None
) -> dict[str, Any]:
    project = _project_directory(args.project_dir)
    html = read_html_file(args.html_file)
    work_id = resolve_work_id(
        project,
        explicit_work_id=args.work_id,
        new_work=args.new,
        required=False,
    )
    token = load_deploy_token(args.config, environ=environ)
    client = LootDeployClient(token, base_url=_resolve_base_url(args.api, environ=environ))
    result = client.preview(
        html=html, title=args.title, work_id=work_id, timeout=args.timeout
    )
    # 落地稳定作品身份，后续 preview/deploy 复用同一草稿。
    write_artifact_work_id(project, result["work_id"])
    return result


def _run_deploy(
    args: argparse.Namespace, *, environ: Mapping[str, str] | None = None
) -> dict[str, Any]:
    project = _project_directory(args.project_dir)
    work_id = resolve_work_id(
        project,
        explicit_work_id=args.work_id,
        new_work=False,
        required=True,
    )
    assert work_id is not None  # required=True 保证非空
    html = read_html_file(args.html_file) if args.html_file is not None else None
    token = load_deploy_token(args.config, environ=environ)
    client = LootDeployClient(token, base_url=_resolve_base_url(args.api, environ=environ))
    result = client.commit(
        work_id=work_id, html=html, title=args.title, timeout=args.timeout
    )
    write_artifact_work_id(project, result["work_id"])
    return result


def run(
    args: argparse.Namespace, *, environ: Mapping[str, str] | None = None
) -> dict[str, Any]:
    if args.command == "configure":
        return _run_configure(args, environ=environ)
    if args.command == "preview":
        return _run_preview(args, environ=environ)
    if args.command == "deploy":
        return _run_deploy(args, environ=environ)
    raise UsageError(f"未知命令：{args.command}")


def main(argv: list[str] | None = None) -> int:
    configure_standard_streams()
    parser = build_parser()
    args = parser.parse_args(argv)
    token_for_redaction = ""
    try:
        # 提前解出令牌只为脱敏；configure 命令尚未落盘时无需。
        if args.command in {"preview", "deploy"}:
            try:
                token_for_redaction = load_deploy_token(args.config)
            except LootDeployError:
                token_for_redaction = ""
        response = run(args)
        print(json.dumps(response, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except LootDeployError as exc:
        sys.stderr.write(f"ERROR: {_redact(exc, token_for_redaction)}\n")
        return exc.exit_code
    except KeyboardInterrupt:
        sys.stderr.write("ERROR: interrupted\n")
        return 130
    except Exception as exc:  # noqa: BLE001 - 顶层兜底，脱敏后上报
        sys.stderr.write(
            f"ERROR: unexpected {type(exc).__name__}: "
            f"{_redact(exc, token_for_redaction)}\n"
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
