from __future__ import annotations

import ctypes
import hashlib
import json
import locale
import logging
import os
import sys
import time
import unicodedata
import uuid
from pathlib import Path

# ----------------------------- Const -----------------------------

APP_NAME = "Minimal"
APP_VERSION = "1.5"


def _script_dir() -> Path:
    try:
        return Path(os.path.abspath(sys.argv[0])).parent
    except Exception:
        return Path.cwd()


APP_DIR = _script_dir()
BACKUP_FILE = APP_DIR / "backup.json"

_uid = hashlib.md5(
    f"{os.environ.get('USERNAME', 'u')}@{os.environ.get('COMPUTERNAME', 'h')}".encode()
).hexdigest()[:8]
LOG_FILE = APP_DIR / f"minimal_{_uid}.log"
LOG_MAX_BYTES = 20 * 1024

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_NAME = "MinimalDesktopTweak"

INVISIBLE_CHARS = ["\u2800", "\u3164", "\uFFA0"]
LEGACY_INVISIBLE_CHARS = {"\u200B", "\u200C", "\u200D", "\u2060", "\uFEFF"}
ALL_INVISIBLE_CHARS = set(INVISIBLE_CHARS) | LEGACY_INVISIBLE_CHARS
INVALID_FILENAME_CHARS = set('<>:"/\\|?*')
WINDOWS_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}
SHORTCUT_EXTS = {".lnk", ".url", ".appref-ms"}


# ----------------------------- Cores ANSI -----------------------------


class C:
    RESET   = "\033[0m"
    DIM     = "\033[2m"
    BOLD    = "\033[1m"
    CYAN    = "\033[36m"
    MAGENTA = "\033[35m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    RED     = "\033[31m"
    BLUE    = "\033[34m"
    WHITE   = "\033[97m"
    GRAY    = "\033[90m"


def enable_ansi() -> None:
    if os.name != "nt":
        return
    try:
        k = ctypes.windll.kernel32
        h = k.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if k.GetConsoleMode(h, ctypes.byref(mode)):
            k.SetConsoleMode(h, mode.value | 0x0004)
    except Exception:
        pass


# ----------------------------- i18n -----------------------------

LANGS = {
    "pt": {
        "title": "Tweak para Tornar sua Area de Trabalho Minimalista",
        "menu_1": "Aplicar    renomeia atalhos para invisivel",
        "menu_2": "Restaurar  restaura nomes originais",
        "menu_0": "Sair",
        "choose": "Selecione",
        "invalid": "Opcao invalida.",
        "bye": "Ate logo.",
        "scanning": "Varrendo atalhos da Area de Trabalho",
        "applied": "ok",
        "reapplied": "ok",
        "restored": "ok",
        "error": "erro",
        "no_backup": "Nenhum backup encontrado.",
        "backup_ok": "Backup salvo em",
        "backup_fail": "Falha ao criar backup. Operacao cancelada.",
        "persist_off": "Inicializacao antiga removida (se existia).",
        "done": "Concluido.",
        "press_enter": "Pressione ENTER para continuar...",
        "no_shortcuts": "Nenhum atalho encontrado.",
        "positions_saved": "posicoes salvas",
        "positions_restored": "posicoes restauradas",
        "positions_backup_used": "posicoes originais reaplicadas",
        "positions_unavailable": "posicoes mantidas pelo Explorer",
        "icon_guard_on": "protegeu icone no .lnk",
        "icon_guard_keep": "icone ja protegido",
        "icon_guard_skip": "icone mantido pelo Windows",
        "icon_guard_fail": "nao foi possivel proteger icone",
        "white_icon_title": "Se algum icone ficou branco:",
        "white_icon_hint": (
            "clique com o botao direito no atalho, abra Propriedades,\n"
            "      clique em Alterar icone, selecione o icone original e clique em Aplicar."
        ),
    },
    "en": {
        "title": "A tweak to make your homescreen minimalist",
        "menu_1": "Apply     rename shortcuts to invisible",
        "menu_2": "Restore   restore original names",
        "menu_0": "Exit",
        "choose": "Select",
        "invalid": "Invalid option.",
        "bye": "Goodbye.",
        "scanning": "Scanning desktop shortcuts",
        "applied": "ok",
        "reapplied": "ok",
        "restored": "ok",
        "error": "error",
        "no_backup": "No backup found.",
        "backup_ok": "Backup saved at",
        "backup_fail": "Backup failed. Operation cancelled.",
        "persist_off": "Old startup entry removed (if existed).",
        "done": "Done.",
        "press_enter": "Press ENTER to continue...",
        "no_shortcuts": "No shortcuts found.",
        "positions_saved": "positions saved",
        "positions_restored": "positions restored",
        "positions_backup_used": "original positions reapplied",
        "positions_unavailable": "positions kept by Explorer",
        "icon_guard_on": "protected icon inside .lnk",
        "icon_guard_keep": "icon already protected",
        "icon_guard_skip": "icon kept by Windows",
        "icon_guard_fail": "could not protect icon",
        "white_icon_title": "If any icon turned white:",
        "white_icon_hint": (
            "right-click the shortcut, open Properties,\n"
            "      click Change Icon, pick the original icon and click Apply."
        ),
    },
}



def detect_lang() -> str:
    try:
        buf = ctypes.create_unicode_buffer(85)
        ctypes.windll.kernel32.GetUserDefaultLocaleName(buf, 85)
        if buf.value.lower().startswith("pt"):
            return "pt"
    except Exception:
        try:
            lc = (locale.getdefaultlocale()[0] or "").lower()
            if lc.startswith("pt"):
                return "pt"
        except Exception:
            pass
    return "en"


L = LANGS[detect_lang()]


# ----------------------------- Logging -----------------------------

_logger: logging.Logger | None = None
_file_handler: logging.FileHandler | None = None


def _prune_log() -> None:
    try:
        if LOG_FILE.exists() and LOG_FILE.stat().st_size > LOG_MAX_BYTES:
            global _file_handler
            if _file_handler:
                try:
                    _logger.removeHandler(_file_handler)  # type: ignore[union-attr]
                    _file_handler.close()
                except Exception:
                    pass
                _file_handler = None
            try:
                LOG_FILE.unlink()
            except Exception:
                pass
    except Exception:
        pass


def setup_logging() -> None:
    global _logger
    _logger = logging.getLogger("minimal")
    _logger.setLevel(logging.INFO)
    _logger.handlers.clear()
    sh = logging.StreamHandler(sys.stderr)     # Console handler
    sh.setLevel(logging.WARNING)
    sh.setFormatter(logging.Formatter(f"{C.DIM}[%(levelname)s]{C.RESET} %(message)s"))
    _logger.addHandler(sh)
    _prune_log()


def _ensure_file_handler() -> None:
    global _file_handler
    if not _logger or _file_handler:
        return
    try:
        APP_DIR.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(str(LOG_FILE), encoding="utf-8")
        fh.setLevel(logging.WARNING)
        fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        _logger.addHandler(fh)
        _file_handler = fh
    except Exception:
        pass


def log(level: str, msg: str, *args) -> None:
    if not _logger:
        return
    try:
        lvl = level.lower()
        if lvl in ("warning", "error", "exception", "critical"):
            _ensure_file_handler()
        getattr(_logger, lvl, _logger.info)(msg, *args)
        _prune_log()
    except Exception:
        pass


# ----------------------------- UI -----------------------------

ASCII_ART_LINES = [
    "    ███╗   ███╗ ██╗ ███╗   ██╗ ██╗ ███╗   ███╗  █████╗  ██╗     ",
    "    ████╗ ████║ ██║ ████╗  ██║ ██║ ████╗ ████║ ██╔══██╗ ██║     ",
    "    ██╔████╔██║ ██║ ██╔██╗ ██║ ██║ ██╔████╔██║ ███████║ ██║     ",
    "    ██║╚██╔╝██║ ██║ ██║╚██╗██║ ██║ ██║╚██╔╝██║ ██╔══██║ ██║     ",
    "    ██║ ╚═╝ ██║ ██║ ██║ ╚████║ ██║ ██║ ╚═╝ ██║ ██║  ██║ ███████╗",
    "    ╚═╝     ╚═╝ ╚═╝ ╚═╝  ╚═══╝ ╚═╝ ╚═╝     ╚═╝ ╚═╝  ╚═╝ ╚══════╝",
]

_GRAD = ["\033[38;5;51m", "\033[38;5;45m", "\033[38;5;39m",
         "\033[38;5;33m", "\033[38;5;99m", "\033[38;5;165m"]


def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def _banner() -> str:
    return "\n".join(f"{_GRAD[i % len(_GRAD)]}{ln}{C.RESET}" for i, ln in enumerate(ASCII_ART_LINES))


def header() -> None:
    clear()
    print()
    print(_banner())
    sub = ("A tweak to make your homescreen minimalist" if L is LANGS["en"]
           else "Tweak para tornar sua area de trabalho minimalista")
    pad = max(0, (66 - len(sub)) // 2)
    print(f"    {' ' * pad}{C.DIM}{C.MAGENTA}{sub}{C.RESET}")
    print(f"    {C.GRAY}{'─' * 62}{C.RESET}")
    lang = "pt-br" if L is LANGS["pt"] else "en-us"
    print(f"    {C.DIM}v{APP_VERSION}  ·  {lang}  ·  uid {_uid}{C.RESET}")
    print()


def show_menu() -> str:
    header()
    items = [
        (C.GREEN,   "1", "▶", L["menu_1"]),
        (C.BLUE,    "2", "↶", L["menu_2"]),
        (C.RED,     "0", "×", L["menu_0"]),
    ]
    for color, num, glyph, text in items:
        print(f"    {C.GRAY}┃{C.RESET} {color}{glyph}{C.RESET} "
              f"{C.BOLD}{color}{num}{C.RESET} {C.GRAY}·{C.RESET} {text}")
    print(f"    {C.GRAY}{'─' * 62}{C.RESET}")
    try:
        return input(f"    {C.MAGENTA}❯{C.RESET} {C.BOLD}{L['choose']}{C.RESET} {C.GRAY}›{C.RESET} ").strip()
    except (KeyboardInterrupt, EOFError):
        return "0"


def line_ok(name: str, label: str | None = None):
    print(f"   {C.GREEN}✓{C.RESET}  {name:<36} {C.DIM}{label or L['applied']}{C.RESET}")


def line_res(name: str):
    print(f"   {C.GREEN}↶{C.RESET}  {name:<36} {C.DIM}{L['restored']}{C.RESET}")


def line_err(msg: str):
    print(f"   {C.RED}✗{C.RESET}  {msg}")


def line_info(msg: str):
    print(f"   {C.CYAN}»{C.RESET}  {msg}")


# ----------------------------- Desktop paths -----------------------------


def desktop_dirs() -> list[Path]:
    out: list[Path] = []
    up = os.environ.get("USERPROFILE", str(Path.home()))
    public = os.environ.get("PUBLIC", r"C:\Users\Public")
    onedrive = os.environ.get("OneDrive")
    out.append(Path(up) / "Desktop")
    out.append(Path(public) / "Desktop")
    if onedrive:
        out.append(Path(onedrive) / "Desktop")
    return [p for p in out if p.exists()]


def list_shortcuts() -> list[Path]:
    items: list[Path] = []
    for d in desktop_dirs():
        try:
            for f in d.iterdir():
                if f.is_file() and f.suffix.lower() in SHORTCUT_EXTS:
                    items.append(f)
        except Exception:
            log("exception", "Erro ao listar %s", d)
    return items


# ----------------------------- Desktop Position Guard -----------------------------

LVM_FIRST = 0x1000
LVM_GETITEMCOUNT = LVM_FIRST + 4
LVM_GETITEMPOSITION = LVM_FIRST + 16
LVM_SETITEMPOSITION32 = LVM_FIRST + 49
LVM_GETITEMTEXTW = LVM_FIRST + 115
PROCESS_VM_OPERATION = 0x0008
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_QUERY_INFORMATION = 0x0400
MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000
MEM_RELEASE = 0x8000
PAGE_READWRITE = 0x04
SMTO_ABORTIFHUNG = 0x0002


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


class LVITEMW(ctypes.Structure):
    _fields_ = [
        ("mask", ctypes.c_uint),
        ("iItem", ctypes.c_int),
        ("iSubItem", ctypes.c_int),
        ("state", ctypes.c_uint),
        ("stateMask", ctypes.c_uint),
        ("pszText", ctypes.c_void_p),
        ("cchTextMax", ctypes.c_int),
        ("iImage", ctypes.c_int),
        ("lParam", ctypes.c_void_p),
        ("iIndent", ctypes.c_int),
        ("iGroupId", ctypes.c_int),
        ("cColumns", ctypes.c_uint),
        ("puColumns", ctypes.c_void_p),
        ("piColFmt", ctypes.c_void_p),
        ("iGroup", ctypes.c_int),
    ]


def _class_name(hwnd: int) -> str:
    try:
        ctypes.windll.user32.GetClassNameW.restype = ctypes.c_int
        ctypes.windll.user32.GetClassNameW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_int]
        buf = ctypes.create_unicode_buffer(256)
        ctypes.windll.user32.GetClassNameW(ctypes.c_void_p(hwnd), buf, 256)
        return buf.value
    except Exception:
        return ""


def _find_desktop_listview() -> int | None:
    if os.name != "nt":
        return None
    user32 = ctypes.windll.user32
    user32.FindWindowW.restype = ctypes.c_void_p
    user32.FindWindowW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p]
    user32.FindWindowExW.restype = ctypes.c_void_p
    user32.FindWindowExW.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_wchar_p]
    found = ctypes.c_void_p()

    def check_parent(hwnd: int) -> bool:
        defview = user32.FindWindowExW(ctypes.c_void_p(hwnd), None, "SHELLDLL_DefView", None)
        if defview:
            lv = user32.FindWindowExW(ctypes.c_void_p(defview), None, "SysListView32", "FolderView")
            if lv:
                found.value = lv
                return True
        return False

    progman = user32.FindWindowW("Progman", None)
    if progman and check_parent(progman):
        return int(found.value)

    enum_proc_type = getattr(ctypes, "WINFUNCTYPE", ctypes.CFUNCTYPE)(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

    @enum_proc_type
    def enum_proc(hwnd, _lparam):
        if found.value:
            return False
        if _class_name(int(hwnd)) in {"WorkerW", "Progman"}:
            check_parent(int(hwnd))
        return not bool(found.value)

    try:
        user32.EnumWindows(enum_proc, None)
    except Exception:
        pass
    return int(found.value) if found.value else None


def _send(hwnd: int, msg: int, wparam: int = 0, lparam: int = 0, timeout_ms: int = 1000) -> int | None:
    try:
        ctypes.windll.user32.SendMessageTimeoutW.restype = ctypes.c_void_p
        ctypes.windll.user32.SendMessageTimeoutW.argtypes = [
            ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_size_t,
            ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_size_t),
        ]
        result = ctypes.c_size_t()
        ok = ctypes.windll.user32.SendMessageTimeoutW(
            ctypes.c_void_p(hwnd), ctypes.c_uint(msg), ctypes.c_size_t(wparam),
            ctypes.c_size_t(lparam), SMTO_ABORTIFHUNG, timeout_ms, ctypes.byref(result),
        )
        return int(result.value) if ok else None
    except Exception:
        return None


def _open_process_for_window(hwnd: int) -> tuple[int | None, int | None]:
    try:
        ctypes.windll.user32.GetWindowThreadProcessId.restype = ctypes.c_ulong
        ctypes.windll.user32.GetWindowThreadProcessId.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
        ctypes.windll.kernel32.OpenProcess.restype = ctypes.c_void_p
        ctypes.windll.kernel32.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_bool, ctypes.c_ulong]
        pid = ctypes.c_ulong()
        ctypes.windll.user32.GetWindowThreadProcessId(ctypes.c_void_p(hwnd), ctypes.byref(pid))
        access = PROCESS_VM_OPERATION | PROCESS_VM_READ | PROCESS_VM_WRITE | PROCESS_QUERY_INFORMATION
        handle = ctypes.windll.kernel32.OpenProcess(access, False, pid.value)
        return (int(handle), int(pid.value)) if handle else (None, None)
    except Exception:
        return None, None


def _remote_alloc(process: int, size: int) -> int | None:
    try:
        ctypes.windll.kernel32.VirtualAllocEx.restype = ctypes.c_void_p
        ctypes.windll.kernel32.VirtualAllocEx.argtypes = [
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_ulong, ctypes.c_ulong,
        ]
        addr = ctypes.windll.kernel32.VirtualAllocEx(
            ctypes.c_void_p(process), None, size, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE,
        )
        return int(addr) if addr else None
    except Exception:
        return None


def _remote_free(process: int, addr: int) -> None:
    try:
        ctypes.windll.kernel32.VirtualFreeEx.restype = ctypes.c_bool
        ctypes.windll.kernel32.VirtualFreeEx.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_ulong]
        ctypes.windll.kernel32.VirtualFreeEx(ctypes.c_void_p(process), ctypes.c_void_p(addr), 0, MEM_RELEASE)
    except Exception:
        pass


def _remote_write(process: int, addr: int, data: bytes) -> bool:
    try:
        ctypes.windll.kernel32.WriteProcessMemory.restype = ctypes.c_bool
        ctypes.windll.kernel32.WriteProcessMemory.argtypes = [
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t),
        ]
        written = ctypes.c_size_t()
        buf = ctypes.create_string_buffer(data)
        return bool(ctypes.windll.kernel32.WriteProcessMemory(
            ctypes.c_void_p(process), ctypes.c_void_p(addr), buf, len(data), ctypes.byref(written),
        ))
    except Exception:
        return False


def _remote_read(process: int, addr: int, size: int) -> bytes | None:
    try:
        ctypes.windll.kernel32.ReadProcessMemory.restype = ctypes.c_bool
        ctypes.windll.kernel32.ReadProcessMemory.argtypes = [
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t),
        ]
        buf = ctypes.create_string_buffer(size)
        read = ctypes.c_size_t()
        ok = ctypes.windll.kernel32.ReadProcessMemory(
            ctypes.c_void_p(process), ctypes.c_void_p(addr), buf, size, ctypes.byref(read),
        )
        return bytes(buf.raw[:read.value]) if ok else None
    except Exception:
        return None


def desktop_position_snapshot() -> dict[str, dict[str, int]]:
    hwnd = _find_desktop_listview()
    if not hwnd:
        return {}
    count = _send(hwnd, LVM_GETITEMCOUNT)
    if count is None or count <= 0:
        return {}
    process, _pid = _open_process_for_window(hwnd)
    if not process:
        return {}

    text_chars = 520
    text_bytes = text_chars * ctypes.sizeof(ctypes.c_wchar)
    item_size = ctypes.sizeof(LVITEMW)
    point_size = ctypes.sizeof(POINT)
    total = item_size + text_bytes + point_size
    remote = _remote_alloc(process, total)
    out: dict[str, dict[str, int]] = {}
    try:
        if not remote:
            return {}
        remote_text = remote + item_size
        remote_point = remote + item_size + text_bytes
        for i in range(int(count)):
            item = LVITEMW()
            item.iSubItem = 0
            item.pszText = remote_text
            item.cchTextMax = text_chars
            if not _remote_write(process, remote, bytes(item)):
                continue
            _send(hwnd, LVM_GETITEMTEXTW, i, remote)
            raw_text = _remote_read(process, remote_text, text_bytes)
            if not raw_text:
                continue
            name = raw_text.decode("utf-16-le", errors="ignore").split("\x00", 1)[0]
            if not name:
                continue
            if _send(hwnd, LVM_GETITEMPOSITION, i, remote_point) is None:
                continue
            raw_point = _remote_read(process, remote_point, point_size)
            if not raw_point or len(raw_point) < point_size:
                continue
            point = POINT.from_buffer_copy(raw_point[:point_size])
            out[name] = {"x": int(point.x), "y": int(point.y)}
        return out
    except Exception:
        log("exception", "Falha ao capturar posicoes do Desktop")
        return {}
    finally:
        if remote:
            _remote_free(process, remote)
        try:
            ctypes.windll.kernel32.CloseHandle(ctypes.c_void_p(process))
        except Exception:
            pass


def _position_for(snapshot: dict[str, dict[str, int]], path: Path) -> dict[str, int] | None:
    return snapshot.get(path.stem) or snapshot.get(path.name)


def _clean_position(pos) -> dict[str, int] | None:
    if not isinstance(pos, dict):
        return None
    try:
        return {"x": int(pos["x"]), "y": int(pos["y"])}
    except Exception:
        return None


def _entry_position(entry: dict) -> dict[str, int] | None:
    return _clean_position(entry.get("desktop_position"))


def _set_entry_position(entry: dict, pos: dict[str, int] | None) -> None:
    clean = _clean_position(pos)
    if clean is not None:
        entry["desktop_position"] = clean


def restore_desktop_positions(requests: list[tuple[list[str], dict[str, int]]], retries: int = 10) -> int:
    if not requests:
        return 0
    hwnd = _find_desktop_listview()
    if not hwnd:
        return 0
    restored: set[str] = set()
    for _ in range(retries):
        snapshot = desktop_position_snapshot()
        if not snapshot:
            time.sleep(0.15)
            continue
        visible_names = list(snapshot.keys())
        for labels, pos in requests:
            if any(label in restored for label in labels):
                continue
            target_label = next((label for label in labels if label in snapshot), None)
            if target_label is None:
                continue
            index = visible_names.index(target_label)
            x = int(pos.get("x", 0)) & 0xFFFF
            y = int(pos.get("y", 0)) & 0xFFFF
            lparam = x | (y << 16)
            if _send(hwnd, LVM_SETITEMPOSITION32, index, lparam) is not None:
                restored.update(labels)
        if len(restored) >= len(requests):
            break
        time.sleep(0.15)
    return len(restored)


# ----------------------------- Naming -----------------------------


def is_invisible_name(stem: str) -> bool:
    if not stem:
        return False
    return all(ch in ALL_INVISIBLE_CHARS for ch in stem)


def is_safe_invisible_stem(stem: str) -> bool:
    return bool(stem) and all(ch in INVISIBLE_CHARS for ch in stem)


def safe_restore_stem(stem: str | None, fallback: str = "Minimal Shortcut") -> str:
    value = "" if stem is None else str(stem)
    out: list[str] = []
    for ch in value:
        cat = unicodedata.category(ch)
        if ch in INVALID_FILENAME_CHARS or ch in ALL_INVISIBLE_CHARS or cat[0] == "C":
            out.append("_")
        else:
            out.append(ch)
    cleaned = "".join(out).strip(" ._")
    if not cleaned or is_invisible_name(cleaned):
        cleaned = fallback
    if cleaned.upper() in WINDOWS_RESERVED_NAMES:
        cleaned = f"_{cleaned}"
    return cleaned[:180]


def failed_temp_invisible_stem(stem: str) -> str | None:
    marker = "_tmp_"
    if marker not in stem:
        return None
    prefix, suffix = stem.rsplit(marker, 1)
    if len(suffix) == 4 and all(ch in "0123456789abcdefABCDEF" for ch in suffix):
        if is_invisible_name(prefix):
            return prefix
    return None


def make_invisible(index: int) -> str:
    chars = INVISIBLE_CHARS
    base = len(chars)
    n = max(1, index)
    result: list[str] = []
    while n > 0:
        n -= 1
        result.append(chars[n % base])
        n //= base
    result.reverse()
    return "".join(result)


def next_available_invisible_name(
    shortcut: Path,
    occupied_names: dict[str, set[str]],
    idx_ref: list[int],
) -> str:
    dir_key = str(shortcut.parent)
    occupied = occupied_names.setdefault(dir_key, set())
    current_name = shortcut.name.casefold()
    occupied.discard(current_name)
    try:
        while True:
            inv = make_invisible(idx_ref[0])
            idx_ref[0] += 1
            candidate_name = f"{inv}{shortcut.suffix}".casefold()
            if candidate_name not in occupied:
                occupied.add(candidate_name)
                return inv
    finally:
        occupied.add(current_name)


# ----------------------------- Backup -----------------------------


def load_backup() -> dict:
    if BACKUP_FILE.exists():
        try:
            data = json.loads(BACKUP_FILE.read_text(encoding="utf-8"))
            items = data.setdefault("items", {})
            for info in items.values():
                if isinstance(info, dict):
                    original = info.get("original_name")
                    if (not original or original == "?" or is_invisible_name(str(original))
                            or any(ch in INVALID_FILENAME_CHARS for ch in str(original))):
                        info["original_name"] = safe_restore_stem(original)
            return data
        except Exception:
            log("exception", "Falha ao ler backup")
    return {"items": {}}


def backup_key(path: Path) -> str:
    return str(path).casefold()


def find_backup_entry(items: dict, path: Path) -> tuple[str | None, dict | None]:
    key = backup_key(path)
    info = items.get(key)
    if isinstance(info, dict):
        return key, info

    info = items.get(path.name)
    if isinstance(info, dict) and info.get("dir") == str(path.parent):
        return path.name, info

    temp_base = failed_temp_invisible_stem(path.stem)
    for bkey, binfo in list(items.items()):
        if not isinstance(binfo, dict):
            continue
        if binfo.get("dir") != str(path.parent) or binfo.get("ext") != path.suffix:
            continue
        if binfo.get("current_name") == path.name or binfo.get("invisible_name") in {path.stem, temp_base}:
            return bkey, binfo
    return None, None


def save_backup(data: dict) -> bool:
    try:
        APP_DIR.mkdir(parents=True, exist_ok=True)
        tmp = BACKUP_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(BACKUP_FILE)
        return True
    except Exception:
        log("exception", "Falha ao salvar backup")
        return False


def ensure_backup(shortcuts: list[Path], position_snapshot: dict[str, dict[str, int]] | None = None) -> dict | None:
    """Carrega/cria backup. Adiciona somente atalhos realmente novos.
    Nao mexe nem armazena icones."""
    data = load_backup()
    items = data.setdefault("items", {})
    position_snapshot = position_snapshot or {}
    for sc in shortcuts:
        _, existing = find_backup_entry(items, sc)
        if existing:
            existing.setdefault("dir", str(sc.parent))
            existing.setdefault("ext", sc.suffix)
            existing.setdefault("original_ext", sc.suffix)
            existing["current_name"] = sc.name
            _set_entry_position(existing, _position_for(position_snapshot, sc))
            continue
        if is_invisible_name(sc.stem) or failed_temp_invisible_stem(sc.stem):
            continue
        items[backup_key(sc)] = {
            "original_name": safe_restore_stem(sc.stem),
            "original_ext": sc.suffix,
            "ext": sc.suffix,
            "dir": str(sc.parent),
            "current_name": sc.name,
            "invisible_name": "",
            "desktop_position": _position_for(position_snapshot, sc),
        }
    if not save_backup(data):
        line_err(L["backup_fail"])
        return None
    line_info(f"{L['backup_ok']} {BACKUP_FILE}")
    return data


# ----------------------------- LNK Icon Guard -----------------------------

MAX_PATH_LONG = 32768
CLSCTX_INPROC_SERVER = 0x1
STGM_READWRITE = 0x00000002
S_OK = 0
S_FALSE = 1
RPC_E_CHANGED_MODE = 0x80010106
CLSID_SHELL_LINK = "00021401-0000-0000-C000-000000000046"
IID_ISHELL_LINK_W = "000214F9-0000-0000-C000-000000000046"
IID_IPERSIST_FILE = "0000010B-0000-0000-C000-000000000046"


class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", ctypes.c_ulong),
        ("Data2", ctypes.c_ushort),
        ("Data3", ctypes.c_ushort),
        ("Data4", ctypes.c_ubyte * 8),
    ]


def _guid(value: str) -> GUID:
    u = uuid.UUID(value)
    return GUID(u.time_low, u.time_mid, u.time_hi_version, (ctypes.c_ubyte * 8)(*u.bytes[8:]))


def _hr_failed(hr: int) -> bool:
    return bool(int(hr) & 0x80000000)


def _release_com(ptr: ctypes.c_void_p | None) -> None:
    if not ptr:
        return
    try:
        proto = getattr(ctypes, "WINFUNCTYPE", ctypes.CFUNCTYPE)(ctypes.c_ulong, ctypes.c_void_p)
        vtbl = ctypes.cast(ptr, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
        proto(vtbl[2])(ptr)
    except Exception:
        pass


def _com_method(ptr: ctypes.c_void_p, index: int, restype, *argtypes):
    proto = getattr(ctypes, "WINFUNCTYPE", ctypes.CFUNCTYPE)(restype, ctypes.c_void_p, *argtypes)
    vtbl = ctypes.cast(ptr, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
    return proto(vtbl[index])


def guard_lnk_icon(shortcut: Path) -> str:
    """Fixa o IconLocation de .lnk no proprio atalho, sem guardar cache.
    Retorna: guarded, already, skipped ou error."""
    if shortcut.suffix.lower() != ".lnk" or os.name != "nt":
        return "skipped"

    ole32 = ctypes.windll.ole32
    shell_link: ctypes.c_void_p | None = None
    persist_file: ctypes.c_void_p | None = None
    did_init = False

    try:
        hr = ole32.CoInitialize(None)
        if hr in (S_OK, S_FALSE):
            did_init = True
        elif (hr & 0xFFFFFFFF) != RPC_E_CHANGED_MODE and _hr_failed(hr):
            return "error"

        ole32.CoCreateInstance.argtypes = [
            ctypes.POINTER(GUID), ctypes.c_void_p, ctypes.c_ulong,
            ctypes.POINTER(GUID), ctypes.POINTER(ctypes.c_void_p),
        ]
        ole32.CoCreateInstance.restype = ctypes.c_long

        clsid = _guid(CLSID_SHELL_LINK)
        iid_shell = _guid(IID_ISHELL_LINK_W)
        iid_persist = _guid(IID_IPERSIST_FILE)
        shell_link = ctypes.c_void_p()
        hr = ole32.CoCreateInstance(
            ctypes.byref(clsid), None, CLSCTX_INPROC_SERVER,
            ctypes.byref(iid_shell), ctypes.byref(shell_link),
        )
        if _hr_failed(hr) or not shell_link.value:
            return "error"

        query_interface = _com_method(
            shell_link, 0, ctypes.c_long,
            ctypes.POINTER(GUID), ctypes.POINTER(ctypes.c_void_p),
        )
        persist_file = ctypes.c_void_p()
        hr = query_interface(shell_link, ctypes.byref(iid_persist), ctypes.byref(persist_file))
        if _hr_failed(hr) or not persist_file.value:
            return "error"

        load = _com_method(persist_file, 5, ctypes.c_long, ctypes.c_wchar_p, ctypes.c_ulong)
        save = _com_method(persist_file, 6, ctypes.c_long, ctypes.c_wchar_p, ctypes.c_bool)
        hr = load(persist_file, str(shortcut), STGM_READWRITE)
        if _hr_failed(hr):
            return "error"

        get_path = _com_method(
            shell_link, 3, ctypes.c_long,
            ctypes.c_wchar_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_ulong,
        )
        get_icon_location = _com_method(
            shell_link, 16, ctypes.c_long,
            ctypes.c_wchar_p, ctypes.c_int, ctypes.POINTER(ctypes.c_int),
        )
        set_icon_location = _com_method(
            shell_link, 17, ctypes.c_long,
            ctypes.c_wchar_p, ctypes.c_int,
        )

        icon_buf = ctypes.create_unicode_buffer(MAX_PATH_LONG)
        icon_index = ctypes.c_int(0)
        hr = get_icon_location(shell_link, icon_buf, MAX_PATH_LONG, ctypes.byref(icon_index))
        if not _hr_failed(hr) and icon_buf.value.strip():
            return "already"

        target_buf = ctypes.create_unicode_buffer(MAX_PATH_LONG)
        hr = get_path(shell_link, target_buf, MAX_PATH_LONG, None, 0)
        target = target_buf.value.strip()
        if _hr_failed(hr) or not target or not Path(target).exists():
            return "skipped"

        hr = set_icon_location(shell_link, target, 0)
        if _hr_failed(hr):
            return "error"
        hr = save(persist_file, str(shortcut), True)
        if _hr_failed(hr):
            return "error"
        return "guarded"
    except Exception:
        log("exception", "Falha no LNK Icon Guard: %s", shortcut)
        return "error"
    finally:
        _release_com(persist_file)
        _release_com(shell_link)
        if did_init:
            try:
                ole32.CoUninitialize()
            except Exception:
                pass


def print_white_icon_hint() -> None:
    print()
    print(f"   {C.YELLOW}!{C.RESET}  {C.BOLD}{L['white_icon_title']}{C.RESET}")
    print(f"      {C.DIM}{L['white_icon_hint']}{C.RESET}")



def apply_tweak(silent: bool = False) -> None:
    shortcuts = list_shortcuts()
    position_snapshot = desktop_position_snapshot()
    position_requests: list[tuple[list[str], dict[str, int]]] = []
    data = ensure_backup(shortcuts, position_snapshot)
    if data is None:
        return
    items = data["items"]
    if not silent:
        line_info(L["scanning"])
        print()

    if not shortcuts:
        if not silent:
            line_err(L["no_shortcuts"])
        return

    occupied_names: dict[str, set[str]] = {}
    for existing in shortcuts:
        occupied_names.setdefault(str(existing.parent), set()).add(existing.name.casefold())
    idx_ref = [1]

    for sc in shortcuts:
        try:
            entry_key, entry = find_backup_entry(items, sc)

            if entry and is_safe_invisible_stem(sc.stem):
                entry["current_name"] = sc.name
                entry["invisible_name"] = sc.stem
                _set_entry_position(entry, _position_for(position_snapshot, sc))
                if not silent:
                    line_ok(entry.get("original_name", sc.name), L["reapplied"])
                continue

            if is_invisible_name(sc.stem) and not entry:
                log("warning", "Atalho invisivel sem backup ignorado: %s", sc)
                if not silent:
                    line_err(f"{sc.name}: sem backup, ignorado")
                continue

            if not entry:
                temp_base = failed_temp_invisible_stem(sc.stem)
                entry_key = backup_key(sc)
                entry = {
                    "original_name": safe_restore_stem(sc.stem if not temp_base else None),
                    "original_ext": sc.suffix,
                    "ext": sc.suffix,
                    "dir": str(sc.parent),
                    "current_name": sc.name,
                    "invisible_name": "",
                }
                items[entry_key] = entry

            original = safe_restore_stem(entry.get("original_name"), sc.stem)
            icon_guard = guard_lnk_icon(sc)
            current_position = _position_for(position_snapshot, sc)
            _set_entry_position(entry, current_position)
            old_position = _entry_position(entry)

            inv = next_available_invisible_name(sc, occupied_names, idx_ref)
            new_path = sc.with_name(inv + sc.suffix)

            if new_path == sc:
                if not silent:
                    line_ok(original, L["reapplied"])
                continue

            while True:
                try:
                    sc.rename(new_path)
                    if old_position:
                        position_requests.append(([new_path.stem, new_path.name], old_position))
                    break
                except FileExistsError:
                    occupied_names.setdefault(str(sc.parent), set()).add(new_path.name.casefold())
                    inv = next_available_invisible_name(sc, occupied_names, idx_ref)
                    new_path = sc.with_name(inv + sc.suffix)

            entry.update({
                "original_name": original,
                "original_ext": entry.get("original_ext") or sc.suffix,
                "ext": sc.suffix,
                "dir": str(sc.parent),
                "current_name": new_path.name,
                "invisible_name": inv,
            })
            if entry_key and entry_key not in items:
                items[entry_key] = entry

            if not silent:
                guard_label = {
                    "guarded": L["icon_guard_on"],
                    "already": L["icon_guard_keep"],
                    "skipped": L["icon_guard_skip"],
                    "error": L["icon_guard_fail"],
                }.get(icon_guard, L["applied"])
                line_ok(original, guard_label)

        except Exception as e:
            log("exception", "Erro ao aplicar em %s: %s", sc, e)
            if not silent:
                line_err(f"{sc.name}: {e}")

    save_backup(data)
    restored_positions = restore_desktop_positions(position_requests)
    if not silent:
        if position_requests:
            label = L["positions_restored"] if restored_positions else L["positions_unavailable"]
            line_info(label)
        print()
        line_info(L["done"])
        print_white_icon_hint()



def restore_tweak() -> None:
    data = load_backup()
    items = data.get("items", {})
    if not items:
        line_err(L["no_backup"])
        return
    line_info(L["scanning"])
    print()

    shortcuts = list_shortcuts()
    position_snapshot = desktop_position_snapshot()
    position_requests: list[tuple[list[str], dict[str, int]]] = []
    current_by_full = {backup_key(p): p for p in shortcuts}
    current_by_name = {p.name: p for p in shortcuts}

    for name, info in list(items.items()):
        try:
            d = Path(info.get("dir", ""))
            current_name = info.get("current_name") or name
            path = current_by_full.get(str(d / current_name).casefold())
            if path is None:
                path = current_by_name.get(current_name) or current_by_name.get(name)
            if path is None and d.exists():
                for f in d.iterdir():
                    if (f.is_file()
                            and f.suffix.lower() in SHORTCUT_EXTS
                            and f.suffix == info.get("ext")
                            and (f.stem == info.get("invisible_name") or is_invisible_name(f.stem))):
                        path = f
                        break
            if path is None:
                log("warning", "Nao encontrado para restaurar: %s", info.get("original_name"))
                continue

            original_stem = safe_restore_stem(info.get("original_name"), "Minimal Shortcut")
            original_ext = info.get("original_ext") or info.get("ext") or path.suffix
            target = path.with_name(original_stem + original_ext)
            old_position = _entry_position(info) or _position_for(position_snapshot, path)

            if target == path:
                continue
            if target.exists():
                i = 2
                while target.exists():
                    target = path.with_name(f"{original_stem} ({i}){original_ext}")
                    i += 1

            path.rename(target)
            if old_position:
                position_requests.append(([target.stem, target.name], old_position))
            line_res(original_stem)

        except Exception as e:
            log("exception", "Erro ao restaurar %s: %s", name, e)
            line_err(f"{name}: {e}")

    save_backup({"items": {}})
    restored_positions = restore_desktop_positions(position_requests)
    if position_requests:
        label = L["positions_backup_used"] if restored_positions else L["positions_unavailable"]
        line_info(label)
    print()
    line_info(L["done"])
    print_white_icon_hint()



# ----------------------------- Persistence -----------------------------


def _winreg():
    try:
        import winreg
        return winreg
    except Exception:
        return None


def disable_persistence() -> None:
    winreg = _winreg()
    if not winreg:
        return
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0,
                            winreg.KEY_SET_VALUE | winreg.KEY_READ) as k:
            try:
                winreg.DeleteValue(k, RUN_NAME)
                line_info(L["persist_off"])
            except FileNotFoundError:
                pass
    except Exception:
        log("exception", "Falha persistencia OFF")


# ----------------------------- Actions -----------------------------


def action_enable():
    disable_persistence()
    apply_tweak()


def action_restore():
    disable_persistence()
    restore_tweak()


# ----------------------------- Main -----------------------------


def main() -> None:
    if os.name != "nt":
        print("Windows only.")
        sys.exit(1)

    enable_ansi()
    setup_logging()

    args = [a.lower() for a in sys.argv[1:]]

    if "--watch" in args:
        disable_persistence()
        return
    if "--enable" in args:
        action_enable()
        return
    if "--restore" in args:
        action_restore()
        return

    while True:
        choice = show_menu()
        print()
        if choice == "1":
            action_enable()
        elif choice == "2":
            action_restore()
        elif choice == "0":
            print(f"   {C.CYAN}{L['bye']}{C.RESET}")
            break
        else:
            line_err(L["invalid"])
        print()
        try:
            input(f"   {C.DIM}{L['press_enter']}{C.RESET}")
        except (KeyboardInterrupt, EOFError):
            print()
            break


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print(f"\n   {C.CYAN}{L['bye']}{C.RESET}")
        sys.exit(0)
