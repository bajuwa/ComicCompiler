# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['comgui-launcher.py'],
             pathex=['C:\\Users\\kayly\\repo\\ComicCompiler'],
             binaries=[('resources', 'resources/')],
             datas=[('comiccompiler', 'comiccompiler/')],
             hiddenimports=['pkg_resources.py2_warn'],
             hookspath=[],
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
          name='comgui.exe',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False , icon='resources/pow_icon.ico')
