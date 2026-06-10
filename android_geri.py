"""Android geri tuşu / jest — uygulama içi navigasyon + ana menüde çıkış onayı."""


def _geri_calistir():
    from kivy.app import App
    app = App.get_running_app()
    if app and hasattr(app, '_geri_isle'):
        try:
            return bool(app._geri_isle())
        except Exception as e:
            print(f'Geri işle: {e}', flush=True)
    return False


def geri_tusu_kur(app):
    import os
    if not (
        'ANDROID_ARGUMENT' in os.environ
        or 'ANDROID_ROOT' in os.environ
        or 'ANDROID_BOOTLOGO' in os.environ
    ):
        return

    # 1) python-for-android activity hook
    try:
        from android import activity

        def _p4a_geri(*_args, **_kw):
            return _geri_calistir()

        activity.bind(on_back_pressed=_p4a_geri)
        app._p4a_geri_bagli = True
    except Exception as e:
        print(f'Geri tuşu (p4a): {e}', flush=True)

    # 2) AndroidX OnBackPressedDispatcher (gesture + fiziksel)
    try:
        from jnius import autoclass, PythonJavaClass, java_method
        from android.runnable import run_on_ui_thread

        @run_on_ui_thread
        def _kur():
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            OnBackPressedCallback = autoclass('androidx.activity.OnBackPressedCallback')

            class FalBackCallback(PythonJavaClass):
                __javaclasses__ = ['androidx/activity/OnBackPressedCallback']

                @java_method('(Z)V')
                def __init__(self, enabled):
                    super().__init__(enabled)

                @java_method('()V')
                def handleOnBackPressed(self):
                    _geri_calistir()

            act = PythonActivity.mActivity
            cb = FalBackCallback(True)
            try:
                cb.setEnabled(True)
            except Exception:
                pass
            act.getOnBackPressedDispatcher().addCallback(act, cb)
            app._android_geri_cb = cb
            print('Geri tuşu (native) kayıtlı', flush=True)

        _kur()
    except Exception as e:
        print(f'Geri tuşu (native): {e}', flush=True)
