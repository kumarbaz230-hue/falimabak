"""p4a hook — gradle öncesi manifest'ten medya izinlerini kaldır."""

import os
import re

_STRIP = (
    'android.permission.READ_MEDIA_IMAGES',
    'android.permission.READ_MEDIA_VIDEO',
)


def _patch_manifest(path):
    if not path or not os.path.isfile(path):
        return
    with open(path, encoding='utf-8') as f:
        text = f.read()
    orig = text
    if 'xmlns:tools' not in text:
        text = re.sub(
            r'(<manifest\b)',
            r'\1 xmlns:tools="http://schemas.android.com/tools"',
            text,
            count=1,
        )
    inserts = []
    for perm in _STRIP:
        line = f'    <uses-permission android:name="{perm}" tools:node="remove" />'
        if line.strip() not in text:
            inserts.append(line)
    if inserts and '<application' in text:
        text = text.replace(
            '<application',
            '\n'.join(inserts) + '\n    <application',
            1,
        )
    if text != orig:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f'p4a_manifest: yamalandi {path}', flush=True)


def _dist_manifest_paths(info):
    paths = []
    dist_dir = None
    if isinstance(info, dict):
        dist_dir = info.get('dist_dir') or info.get('build_dir')
    elif info is not None:
        dist_dir = getattr(info, 'dist_dir', None) or getattr(info, 'build_dir', None)
    if dist_dir:
        paths.append(os.path.join(dist_dir, 'AndroidManifest.xml'))
        paths.append(os.path.join(dist_dir, 'src', 'main', 'AndroidManifest.xml'))
    return paths


def pre_build_apk(info=None, **kwargs):
    for path in _dist_manifest_paths(info or kwargs):
        _patch_manifest(path)


def post_dist(info=None, **kwargs):
    pre_build_apk(info, **kwargs)
