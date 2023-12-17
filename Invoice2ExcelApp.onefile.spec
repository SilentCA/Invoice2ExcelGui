# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

hidden_imports = [
        'pygubu.builder.tkstdwidgets',
        'pygubu.builder.ttkstdwidgets'
        ]

data_files = [
        ('Invoice2ExcelApp.ui','.'),
        ('icon.png','.')
        ]

a = Analysis(['Invoice2ExcelApp.py'],
             pathex=[],
             binaries=[],
             datas=data_files,
             hiddenimports=hidden_imports,
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='Invoice2ExcelApp',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          icon='icon.ico' )
