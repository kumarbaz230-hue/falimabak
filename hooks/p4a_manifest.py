"""p4a hook — gradle öncesi manifest'ten medya izinlerini kaldır."""

import os
import re

_STRIP = (
    'android.permission.READ_MEDIA_IMAGES',
    'android.permission.READ_MEDIA_VIDEO',
    'android.permission.READ_EXTERNAL_STORAGE',
    'android.permission.WRITE_EXTERNAL_STORAGE',
)


def _dist_dir(toolchain):
    dist = getattr(toolchain, '_dist', None)
    if dist is None:
        return None
    return getattr(dist, 'dist_dir', None)


def _patch_manifest(path):
    if not path or not os.path.isfile(path):
        return
    with open(path, encoding='utf-8') as f:
        text = f.read()
    orig = text
    for perm in _STRIP:
        text = re.sub(
            rf'\s*<uses-permission[^>]*android:name="{re.escape(perm)}"[^>]*/>\s*',
            '\n',
            text,
        )
    if text != orig:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f'p4a_manifest: temizlendi {path}', flush=True)


def _run(toolchain):
    dist_dir = _dist_dir(toolchain)
    if not dist_dir:
        print('p4a_manifest: dist_dir yok', flush=True)
        return
    for rel in ('AndroidManifest.xml', os.path.join('src', 'main', 'AndroidManifest.xml')):
        _patch_manifest(os.path.join(dist_dir, rel))


def before_apk_build(toolchain):
    _run(toolchain)


def after_apk_build(toolchain):
    _run(toolchain)


def before_apk_assemble(toolchain):
    _run(toolchain)
