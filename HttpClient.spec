# -*- mode: python ; coding: utf-8 -*-
# Сборка в режиме onedir (папка с exe) — меньше ложных срабатываний антивируса.
# Использование:  pyinstaller --noconfirm HttpClient.spec

from PyInstaller.utils.hooks import collect_all

datas = [("assets/icon.ico", "assets")]
binaries = []
hiddenimports = []
tmp_ret = collect_all("customtkinter")
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

a = Analysis(
    ["http_client.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["numpy", "matplotlib", "scipy", "pytest"],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,      # onedir: бинарники кладутся рядом, а не внутрь exe
    name="HttpClient",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,                  # UPX выключен — провоцирует антивирусы
    console=False,              # оконное приложение, без консоли
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=["assets/icon.ico"],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="HttpClient",
)
