"""KivMob — AdMob bridge (FalımaBak, banner + interstitial + rewarded)."""

from kivy.utils import platform
from kivy.logger import Logger

AndroidBridge = None

if platform == 'android':
    try:
        from jnius import autoclass
        from android.runnable import run_on_ui_thread

        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        AdRequestBuilder = autoclass('com.google.android.gms.ads.AdRequest$Builder')
        AdSize = autoclass('com.google.android.gms.ads.AdSize')
        AdView = autoclass('com.google.android.gms.ads.AdView')
        Gravity = autoclass('android.view.Gravity')
        LayoutParams = autoclass('android.view.ViewGroup$LayoutParams')
        LinearLayout = autoclass('android.widget.LinearLayout')
        MobileAds = autoclass('com.google.android.gms.ads.MobileAds')
        View = autoclass('android.view.View')

        try:
            InterstitialAd = autoclass('com.google.android.gms.ads.interstitial.InterstitialAd')
            _INTERSTITIAL_OK = True
        except Exception:
            try:
                InterstitialAd = autoclass('com.google.android.gms.ads.InterstitialAd')
                _INTERSTITIAL_OK = True
            except Exception:
                InterstitialAd = None
                _INTERSTITIAL_OK = False

        try:
            RewardedAd = autoclass('com.google.android.gms.ads.rewarded.RewardedAd')
            _REWARDED_OK = True
        except Exception:
            RewardedAd = None
            _REWARDED_OK = False

        class AndroidBridge:
            @run_on_ui_thread
            def __init__(self, appID):
                self._loaded = False
                self._activity = PythonActivity.mActivity
                self._interstitial = None
                self._interstitial_loaded = False
                self._interstitial_unit_id = ''
                self._rewarded = None
                self._rewarded_loaded = False
                self._rewarded_unit_id = ''
                self._test_devices = []
                try:
                    MobileAds.initialize(self._activity)
                except Exception:
                    try:
                        MobileAds.initialize(self._activity, appID)
                    except Exception as e:
                        Logger.error(f'KivMob MobileAds: {e}')
                self._adview = AdView(self._activity)

            @run_on_ui_thread
            def add_test_device(self, testID):
                self._test_devices.append(testID)

            @run_on_ui_thread
            def new_banner(self, unitID, top_pos=True):
                self._adview = AdView(self._activity)
                self._adview.setAdUnitId(unitID)
                try:
                    self._adview.setAdSize(AdSize.BANNER)
                except Exception:
                    self._adview.setAdSize(AdSize.SMART_BANNER)
                self._adview.setVisibility(View.GONE)
                ad_lp = LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.WRAP_CONTENT)
                self._adview.setLayoutParams(ad_lp)
                layout = LinearLayout(self._activity)
                if not top_pos:
                    layout.setGravity(Gravity.BOTTOM)
                layout.addView(self._adview)
                root_lp = LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT)
                layout.setLayoutParams(root_lp)
                self._activity.addContentView(layout, root_lp)

            @run_on_ui_thread
            def request_banner(self, options=None):
                self._adview.loadAd(self._get_builder(options).build())

            @run_on_ui_thread
            def show_banner(self):
                self._adview.setVisibility(View.VISIBLE)

            @run_on_ui_thread
            def hide_banner(self):
                self._adview.setVisibility(View.GONE)

            @run_on_ui_thread
            def new_interstitial(self, unitID):
                self._interstitial_unit_id = unitID or ''
                self._interstitial = None
                self._interstitial_loaded = False

            def is_interstitial_loaded(self):
                if hasattr(self, '_interstitial_unit_id') and self._interstitial_unit_id:
                    return bool(self._interstitial_loaded and self._interstitial)
                self._is_interstitial_loaded()
                return self._loaded

            @run_on_ui_thread
            def _is_interstitial_loaded(self):
                if self._interstitial is None:
                    self._loaded = False
                    return
                try:
                    self._loaded = self._interstitial.isLoaded()
                except Exception:
                    self._loaded = bool(self._interstitial_loaded and self._interstitial)

            @run_on_ui_thread
            def request_interstitial(self, options=None):
                if not _INTERSTITIAL_OK or not self._interstitial_unit_id:
                    self._interstitial_loaded = False
                    return
                from jnius import PythonJavaClass, java_method
                bridge = self
                request = self._get_builder(options).build()

                try:
                    class _InterLoadCb(PythonJavaClass):
                        __javaclasses__ = ['com/google/android/gms/ads/interstitial/InterstitialAdLoadCallback']

                        @java_method('(Lcom/google/android/gms/ads/interstitial/InterstitialAd;)V')
                        def onAdLoaded(self, ad):
                            bridge._interstitial = ad
                            bridge._interstitial_loaded = True
                            print('Interstitial reklam yüklendi', flush=True)

                        @java_method('(Lcom/google/android/gms/ads/LoadAdError;)V')
                        def onAdFailedToLoad(self, error):
                            bridge._interstitial = None
                            bridge._interstitial_loaded = False
                            try:
                                print(f'Interstitial reklam yüklenemedi: {error.getMessage()}', flush=True)
                            except Exception:
                                print('Interstitial reklam yüklenemedi', flush=True)

                    self._interstitial = None
                    self._interstitial_loaded = False
                    InterstitialAd.load(
                        self._activity,
                        self._interstitial_unit_id,
                        request,
                        _InterLoadCb(),
                    )
                except Exception as e:
                    Logger.error(f'KivMob request_interstitial: {e}')
                    try:
                        old_inst = InterstitialAd(self._activity)
                        old_inst.setAdUnitId(self._interstitial_unit_id)
                        old_inst.loadAd(request)
                        self._interstitial = old_inst
                    except Exception:
                        pass

            @run_on_ui_thread
            def show_interstitial(self):
                if self._interstitial is not None:
                    try:
                        self._interstitial.show(self._activity)
                        self._interstitial_loaded = False
                        self._interstitial = None
                    except Exception:
                        try:
                            self._interstitial.show()
                            self._interstitial_loaded = False
                            self._interstitial = None
                        except Exception as e:
                            Logger.error(f'KivMob show_interstitial: {e}')

            @run_on_ui_thread
            def show_interstitial_callback(self, py_callback):
                from jnius import PythonJavaClass, java_method
                from kivy.clock import Clock

                if not self.is_interstitial_loaded():
                    Clock.schedule_once(lambda *_: py_callback(False), 0)
                    return

                bridge = self
                fired = [False]

                def _once(ok):
                    if fired[0]:
                        return
                    fired[0] = True
                    py_callback(ok)

                try:
                    class _InterFullScreenCb(PythonJavaClass):
                        __javaclasses__ = ['com/google/android/gms/ads/FullScreenContentCallback']

                        @java_method('()V')
                        def onAdDismissedFullScreenContent(self):
                            Clock.schedule_once(lambda *_: _once(True), 0)
                            bridge._interstitial = None
                            bridge._interstitial_loaded = False
                            try:
                                bridge.request_interstitial()
                            except Exception:
                                pass

                        @java_method('(Lcom/google/android/gms/ads/AdError;)V')
                        def onAdFailedToShowFullScreenContent(self, ad_error):
                            Clock.schedule_once(lambda *_: _once(False), 0)
                            bridge._interstitial = None
                            bridge._interstitial_loaded = False
                            try:
                                bridge.request_interstitial()
                            except Exception:
                                pass

                    ad = bridge._interstitial
                    bridge._interstitial_loaded = False
                    bridge._interstitial = None
                    ad.setFullScreenContentCallback(_InterFullScreenCb())
                    ad.show(bridge._activity)
                    return
                except Exception as e:
                    Logger.error(f'KivMob show_interstitial_callback modern error: {e}')

                try:
                    AdListener = autoclass('com.google.android.gms.ads.AdListener')
                    class _CloseListener(PythonJavaClass):
                        __javaclasses__ = ['com/google/android/gms/ads/AdListener']

                        @java_method('()V')
                        def onAdClosed(self):
                            Clock.schedule_once(lambda *_: py_callback(True), 0)
                            try:
                                bridge.request_interstitial()
                            except Exception:
                                pass

                        @java_method('(I)V')
                        def onAdFailedToLoad(self, error_code):
                            Clock.schedule_once(lambda *_: py_callback(False), 0)

                    listener = _CloseListener()
                    bridge._close_listener = listener
                    bridge._interstitial.setAdListener(listener)
                    bridge._interstitial.show()
                except Exception as e:
                    Logger.error(f'KivMob show_interstitial_callback legacy error: {e}')
                    Clock.schedule_once(lambda *_: py_callback(False), 0)

            @run_on_ui_thread
            def new_rewarded(self, unitID):
                self._rewarded_unit_id = unitID or ''
                self._rewarded = None
                self._rewarded_loaded = False

            def is_rewarded_loaded(self):
                return bool(self._rewarded_loaded and self._rewarded)

            @run_on_ui_thread
            def request_rewarded(self, options=None):
                if not _REWARDED_OK or not self._rewarded_unit_id:
                    self._rewarded_loaded = False
                    return
                from jnius import PythonJavaClass, java_method
                from kivy.clock import Clock

                bridge = self
                request = self._get_builder(options).build()

                class _LoadCb(PythonJavaClass):
                    __javaclasses__ = ['com/google/android/gms/ads/rewarded/RewardedAdLoadCallback']

                    @java_method('(Lcom/google/android/gms/ads/rewarded/RewardedAd;)V')
                    def onAdLoaded(self, ad):
                        bridge._rewarded = ad
                        bridge._rewarded_loaded = True

                    @java_method('(Lcom/google/android/gms/ads/LoadAdError;)V')
                    def onAdFailedToLoad(self, error):
                        bridge._rewarded = None
                        bridge._rewarded_loaded = False
                        try:
                            print(f'Ödüllü reklam yüklenemedi: {error.getMessage()}', flush=True)
                        except Exception:
                            print('Ödüllü reklam yüklenemedi', flush=True)

                self._rewarded = None
                self._rewarded_loaded = False
                RewardedAd.load(
                    self._activity,
                    self._rewarded_unit_id,
                    request,
                    _LoadCb(),
                )

            @run_on_ui_thread
            def show_rewarded_callback(self, py_callback):
                from jnius import PythonJavaClass, java_method
                from kivy.clock import Clock

                if not self.is_rewarded_loaded():
                    Clock.schedule_once(lambda *_: py_callback(False), 0)
                    return

                bridge = self
                fired = [False]

                def _once(ok):
                    if fired[0]:
                        return
                    fired[0] = True
                    py_callback(ok)

                earned = [False]

                class _RewardCb(PythonJavaClass):
                    __javaclasses__ = ['com/google/android/gms/ads/OnUserEarnedRewardListener']

                    @java_method('(Lcom/google/android/gms/ads/rewarded/RewardItem;)V')
                    def onUserEarnedReward(self, reward_item):
                        earned[0] = True
                        Clock.schedule_once(lambda *_: _once(True), 0)

                class _FullScreenCb(PythonJavaClass):
                    __javaclasses__ = ['com/google/android/gms/ads/FullScreenContentCallback']

                    @java_method('()V')
                    def onAdDismissedFullScreenContent(self):
                        if not earned[0]:
                            Clock.schedule_once(lambda *_: _once(False), 0)
                        bridge._rewarded = None
                        bridge._rewarded_loaded = False
                        try:
                            bridge.request_rewarded()
                        except Exception:
                            pass

                    @java_method('(Lcom/google/android/gms/ads/AdError;)V')
                    def onAdFailedToShowFullScreenContent(self, ad_error):
                        if not earned[0]:
                            Clock.schedule_once(lambda *_: _once(False), 0)
                        bridge._rewarded = None
                        bridge._rewarded_loaded = False
                        try:
                            bridge.request_rewarded()
                        except Exception:
                            pass

                ad = bridge._rewarded
                bridge._rewarded_loaded = False
                ad.setFullScreenContentCallback(_FullScreenCb())
                ad.show(bridge._activity, _RewardCb())

            def _get_builder(self, options):
                builder = AdRequestBuilder()
                for test_device in self._test_devices:
                    try:
                        builder.addTestDevice(test_device)
                    except Exception:
                        pass
                return builder

    except BaseException as exc:
        Logger.error(f'KivMob: AdMob yüklenemedi — {exc}')
else:

    def run_on_ui_thread(fn):
        return fn


class TestIds:
    APP = 'ca-app-pub-3940256099942544~3347511713'
    BANNER = 'ca-app-pub-3940256099942544/6300978111'
    INTERSTITIAL = 'ca-app-pub-3940256099942544/1033173712'
    REWARDED = 'ca-app-pub-3940256099942544/5224354917'


class AdMobBridge:
    def __init__(self, appID):
        pass

    def add_test_device(self, testID):
        pass

    def is_interstitial_loaded(self):
        return False

    def new_banner(self, unitID, top_pos=True):
        pass

    def new_interstitial(self, unitID):
        pass

    def request_banner(self, options=None):
        pass

    def request_interstitial(self, options=None):
        pass

    def show_banner(self):
        pass

    def show_interstitial(self):
        pass

    def show_interstitial_callback(self, callback):
        from kivy.clock import Clock
        Clock.schedule_once(lambda *_: callback(True), 0.2)

    def new_rewarded(self, unitID):
        pass

    def is_rewarded_loaded(self):
        return True

    def request_rewarded(self, options=None):
        pass

    def show_rewarded_callback(self, callback):
        from kivy.clock import Clock
        Clock.schedule_once(lambda *_: callback(True), 0.2)

    def hide_banner(self):
        pass


class KivMob:
    def __init__(self, appID):
        if platform == 'android' and AndroidBridge is not None:
            self.bridge = AndroidBridge(appID)
        else:
            self.bridge = AdMobBridge(appID)

    def add_test_device(self, device):
        self.bridge.add_test_device(device)

    def new_banner(self, unitID, top_pos=True):
        self.bridge.new_banner(unitID, top_pos)

    def new_interstitial(self, unitID):
        self.bridge.new_interstitial(unitID)

    def is_interstitial_loaded(self):
        return self.bridge.is_interstitial_loaded()

    def request_banner(self, options=None):
        self.bridge.request_banner(options)

    def request_interstitial(self, options=None):
        self.bridge.request_interstitial(options)

    def show_banner(self):
        self.bridge.show_banner()

    def show_interstitial(self):
        self.bridge.show_interstitial()

    def show_interstitial_callback(self, callback):
        if hasattr(self.bridge, 'show_interstitial_callback'):
            self.bridge.show_interstitial_callback(callback)
        else:
            from kivy.clock import Clock
            Clock.schedule_once(lambda *_: callback(False), 0)

    def new_rewarded(self, unitID):
        if hasattr(self.bridge, 'new_rewarded'):
            self.bridge.new_rewarded(unitID)

    def is_rewarded_loaded(self):
        if hasattr(self.bridge, 'is_rewarded_loaded'):
            return self.bridge.is_rewarded_loaded()
        return False

    def request_rewarded(self, options=None):
        if hasattr(self.bridge, 'request_rewarded'):
            self.bridge.request_rewarded(options)

    def show_rewarded_callback(self, callback):
        if hasattr(self.bridge, 'show_rewarded_callback'):
            self.bridge.show_rewarded_callback(callback)
        else:
            from kivy.clock import Clock
            Clock.schedule_once(lambda *_: callback(False), 0)

    def hide_banner(self):
        self.bridge.hide_banner()
