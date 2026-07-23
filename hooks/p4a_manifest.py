"""p4a hook — gradle merge oncesi/sonrasi medya izinlerini manifest'ten kaldir."""

import glob
import os
import re

_STRIP = (
    'android.permission.READ_MEDIA_IMAGES',
    'android.permission.READ_MEDIA_VIDEO',
    'android.permission.READ_MEDIA_AUDIO',
    'android.permission.READ_MEDIA_VISUAL_USER_SELECTED',
    'android.permission.READ_EXTERNAL_STORAGE',
    'android.permission.WRITE_EXTERNAL_STORAGE',
    'android.permission.ACCESS_MEDIA_LOCATION',
    'android.permission.MANAGE_EXTERNAL_STORAGE',
    'android.permission.USE_EXACT_ALARM',
    'android.permission.SCHEDULE_EXACT_ALARM',
)


def _dist_dir(toolchain):
    dist = getattr(toolchain, '_dist', None)
    if dist is None:
        return None
    return getattr(dist, 'dist_dir', None)


def _ensure_tools_ns(text):
    if 'xmlns:tools=' in text:
        return text
    if 'xmlns:android="http://schemas.android.com/apk/res/android"' in text:
        return text.replace(
            'xmlns:android="http://schemas.android.com/apk/res/android"',
            'xmlns:android="http://schemas.android.com/apk/res/android"\n'
            '    xmlns:tools="http://schemas.android.com/tools"',
            1,
        )
    return re.sub(
        r'(<manifest\b)',
        r'\1 xmlns:tools="http://schemas.android.com/tools"',
        text,
        count=1,
    )


_QUERIES_BLOCK = """
    <queries>
        <intent>
            <action android:name="android.media.action.IMAGE_CAPTURE" />
        </intent>
        <intent>
            <action android:name="android.intent.action.GET_CONTENT" />
        </intent>
        <intent>
            <action android:name="android.intent.action.OPEN_DOCUMENT" />
        </intent>
        <intent>
            <action android:name="android.intent.action.PICK" />
        </intent>
        <intent>
            <action android:name="android.provider.action.PICK_IMAGES" />
        </intent>
    </queries>
"""


def _inject_package_queries(text):
    """Android 11+ kamera/galeri intent gorunurlugu."""
    if 'android.media.action.IMAGE_CAPTURE' in text:
        return text
    if '</manifest>' in text:
        return text.replace('</manifest>', _QUERIES_BLOCK + '\n</manifest>', 1)
    return text


_CAMERA_FEATURES = """
    <uses-feature android:name="android.hardware.camera" android:required="false" />
    <uses-feature android:name="android.hardware.camera.autofocus" android:required="false" />
    <uses-feature android:name="android.hardware.camera.front" android:required="false" />
"""


def _inject_camera_features(text):
    if 'android.hardware.camera" android:required="false"' in text:
        return text
    if '<application' in text:
        return text.replace('<application', _CAMERA_FEATURES + '    <application', 1)
    if '</manifest>' in text:
        return text.replace('</manifest>', _CAMERA_FEATURES + '</manifest>', 1)
    return text


def _patch_manifest(path):
    if not path or not os.path.isfile(path):
        return
    with open(path, encoding='utf-8') as f:
        text = f.read()
    orig = text
    text = _ensure_tools_ns(text)
    text = _inject_package_queries(text)
    text = _inject_camera_features(text)

    kept = []
    for line in text.splitlines():
        if 'uses-permission' in line and any(p in line for p in _STRIP):
            if 'tools:node="remove"' in line:
                kept.append(line)
            continue
        kept.append(line)
    text = '\n'.join(kept)

    inserts = []
    for perm in _STRIP:
        marker = f'android:name="{perm}" tools:node="remove"'
        if marker not in text:
            inserts.append(
                f'    <uses-permission android:name="{perm}" tools:node="remove" />'
            )

    if inserts:
        if '<application' in text:
            text = text.replace(
                '<application',
                '\n'.join(inserts) + '\n    <application',
                1,
            )
        elif '</manifest>' in text:
            text = text.replace('</manifest>', '\n'.join(inserts) + '\n</manifest>', 1)

    if text != orig:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f'p4a_manifest: yamalandi {path}', flush=True)


def _manifest_paths(dist_dir):
    paths = [
        os.path.join(dist_dir, 'AndroidManifest.xml'),
        os.path.join(dist_dir, 'src', 'main', 'AndroidManifest.xml'),
    ]
    paths.extend(glob.glob(
        os.path.join(dist_dir, 'build', 'intermediates', '**', 'AndroidManifest.xml'),
        recursive=True,
    ))
    seen = set()
    out = []
    for path in paths:
        if path not in seen and os.path.isfile(path):
            seen.add(path)
            out.append(path)
    return out


def _run(toolchain):
    dist_dir = _dist_dir(toolchain)
    if not dist_dir:
        print('p4a_manifest: dist_dir yok', flush=True)
        return
    for path in _manifest_paths(dist_dir):
        _patch_manifest(path)


def _active_perm_in_line(line):
    if 'uses-permission' not in line:
        return None
    if 'tools:node="remove"' in line:
        return None
    for perm in _STRIP:
        if perm in line:
            return perm
    return None


def _verify_no_media_perms(dist_dir):
    bad = []
    for path in _manifest_paths(dist_dir):
        try:
            with open(path, encoding='utf-8') as f:
                lines = f.read().splitlines()
        except OSError:
            continue
        for line in lines:
            perm = _active_perm_in_line(line)
            if perm:
                bad.append((path, perm, line.strip()))
    if bad:
        for path, perm, line in bad:
            print(f'p4a_manifest HATA: {perm} -> {path} :: {line}', flush=True)
        raise RuntimeError('Medya/storage izinleri merged manifestte kaldi')


def before_apk_build(toolchain):
    _run(toolchain)


def after_apk_build(toolchain):
    _run(toolchain)


def before_apk_assemble(toolchain):
    _run(toolchain)


def after_apk_assemble(toolchain):
    _run(toolchain)
    dist_dir = _dist_dir(toolchain)
    if dist_dir:
        _verify_no_media_perms(dist_dir)
