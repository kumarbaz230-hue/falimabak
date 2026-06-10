"""Android geri jesti / tuşu — OnBackPressedCallback ile çıkış onayı."""


def geri_tusu_kur(app):
    """Gesture navigation dahil tüm geri hareketlerini yakala."""
    import os
    if not (
        'ANDROID_ARGUMENT' in os.environ
        or 'ANDROID_ROOT' in os.environ
        or 'ANDROID_BOOTLOGO' in os.environ
    ):
        return

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
                    from kivy.app import App
                    a = App.get_running_app()
                    if a and hasattr(a, '_geri_isle'):
                        a._geri_isle()

            activity = PythonActivity.mActivity
            callback = FalBackCallback(True)
            activity.getOnBackPressedDispatcher().addCallback(activity, callback)
            app._android_geri_cb = callback

        _kur()
    except Exception as e:
        print(f'Geri tuşu (native): {e}', flush=True)
