# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],  # Arquivo principal
    pathex=['D:\app_scanner'],  # Caminho do projeto
    binaries=[],
    datas=[  
        ('TWAINDSM.dll', '.'),   # Inclui a DLL
        ('./data/', '.'),     # Inclui o arquivo JSON de dados
        ('./imgs/', '.')        # Inclui a pasta de logos
    ],
    hiddenimports=[
        'pytwain',  # Inclui a biblioteca pytwain
        'PIL',      # Inclui o Pillow (PIL)
        'requests', # Inclui a requests
        'time',     # Inclui o módulo time (normalmente detectado automaticamente)
        'json',     # Inclui o módulo json (também normalmente detectado automaticamente)
        'logging'   # Inclui a biblioteca logging
    ],  # Adiciono aqui as importações ocultas, se necessário
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='App Scanner',  # Nome do executável
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],  # Adiciono aqui, exclusões do UPX se houver arquivos sensíveis
    runtime_tmpdir=None,
    console=False,  # Define como "False" para não ter uma janela de console
    icon='./imgs/logos/logo-version3.ico'
)