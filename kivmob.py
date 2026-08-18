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
        FrameLayout = autoclass('android.widget.FrameLayout')
        FrameLayoutParams = autoclass('android.widget.FrameLayout$LayoutParams')
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
                self._app_id = appID or ''
                self._initialized = False
                self._init_listener = None
                self._banner_pending = False
                self._interstitial_pending = False
                self._rewarded_pending = False
                self._banner_container = None
                self._banner_requested = False
                self._banner_loaded = False
                self._banner_listener = None
                self._banner_retry_delay = 15.0
                self._interstitial = None
                self._interstitial_loaded = False
                self._interstitial_unit_id = ''
                self._inter_load_cb = None
                self._inter_fullscreen_cb = None
                self._rewarded = None
                self._rewarded_loaded = False
                self._rewarded_unit_id = ''
                self._reward_load_cb = None
                self._reward_cb = None
                self._reward_fullscreen_cb = None
                self._test_devices = []
                self._adview = AdView(self._activity)

                # Loading before the SDK finishes initialization is a common
                # source of silent failures with a Python/Java bridge. Queue
                # requests until Google's completion callback fires.
                bridge = self
                try:
                    from jnius import PythonJavaClass, java_method

                    class _InitCb(PythonJavaClass):
                        __javainterfaces__ = [
                            'com/google/android/gms/ads/initialization/'
                            'OnInitializationCompleteListener'
                        ]

                        @java_method(
                            '(Lcom/google/android/gms/ads/initialization/'
                            'InitializationStatus;)V'
                        )
                        def onInitializationComplete(self, status):
                            bridge._initialized = True
                            print('AdMob SDK başlatıldı', flush=True)
                            if bridge._banner_pending:
                                bridge._banner_pending = False
                                bridge.request_banner()
                            if bridge._interstitial_pending:
                                bridge._interstitial_pending = False
                                bridge.request_interstitial()
                            if bridge._rewarded_pending:
                                bridge._rewarded_pending = False
                                bridge.request_rewarded()

                    self._init_listener = _InitCb()
                    MobileAds.initialize(self._activity, self._init_listener)
                    # The SDK queues loadAd calls internally while the
                    # adapters finish. Do not make ad delivery depend on a
                    # Python callback being dispatched successfully.
                    self._initialized = True
                    print('AdMob SDK başlatma isteği gönderildi', flush=True)
                except Exception as e:
                    # The one-argument overload is available in older GMA
                    # versions. Requests are still accepted by the SDK, but
                    # keep a clear log instead of failing silently.
                    Logger.error(f'KivMob MobileAds initialize callback: {e}')
                    try:
                        MobileAds.initialize(self._activity)
                        self._initialized = True
                        print('AdMob SDK başlatıldı (callback yok)', flush=True)
                    except Exception as init_error:
                        Logger.error(f'KivMob MobileAds initialize: {init_error}')

            @run_on_ui_thread
            def add_test_device(self, testID):
                self._test_devices.append(testID)

            @run_on_ui_thread
            def new_banner(self, unitID, top_pos=True):
                from jnius import PythonJavaClass, java_method
                from kivy.clock import Clock

                bridge = self
                self._banner_unit_id = unitID or ''
                self._banner_requested = False
                self._banner_loaded = False
                self._adview = AdView(self._activity)
                self._adview.setAdUnitId(self._banner_unit_id)
                try:
                    self._adview.setAdSize(AdSize.BANNER)
                except Exception:
                    # SMART_BANNER was removed from newer SDKs, but this
                    # fallback keeps the bridge compatible with old builds.
                    self._adview.setAdSize(AdSize.SMART_BANNER)

                class _BannerListener(PythonJavaClass):
                    __javaclasses__ = ['com/google/android/gms/ads/AdListener']

                    @java_method('()V')
                    def onAdLoaded(self):
                        bridge._banner_loaded = True
                        bridge._banner_retry_delay = 15.0
                        print('Banner reklam yüklendi', flush=True)
                        if bridge._banner_requested and bridge._banner_container:
                            bridge._adview.setVisibility(View.VISIBLE)
                            bridge._banner_container.setVisibility(View.VISIBLE)

                    @java_method('(Lcom/google/android/gms/ads/LoadAdError;)V')
                    def onAdFailedToLoad(self, error):
                        bridge._banner_loaded = False
                        if bridge._banner_container:
                            bridge._banner_container.setVisibility(View.GONE)
                        try:
                            print(
                                'Banner reklam yüklenemedi: '
                                f'{error.getCode()} / {error.getDomain()} / '
                                f'{error.getMessage()}',
                                flush=True,
                            )
                        except Exception:
                            print('Banner reklam yüklenemedi', flush=True)
                        # No-fill/network failures are often temporary. Retry
                        # with a small exponential backoff instead of making
                        # a single request at app startup and giving up.
                        delay = bridge._banner_retry_delay
                        bridge._banner_retry_delay = min(delay * 2.0, 120.0)
                        Clock.schedule_once(
                            lambda *_: bridge.request_banner(), delay,
                        )

                # Keep the listener alive for the lifetime of AdView. A local
                # PythonJavaClass can otherwise be garbage-collected before
                # the asynchronous Google callback arrives.
                self._banner_listener = _BannerListener()
                self._adview.setAdListener(self._banner_listener)

                self._adview.setVisibility(View.GONE)
                ad_lp = FrameLayoutParams(
                    LayoutParams.MATCH_PARENT,
                    LayoutParams.WRAP_CONTENT,
                )
                self._adview.setLayoutParams(ad_lp)

                # Attach only a wrap-content banner at the edge of the
                # activity. The old full-screen LinearLayout could sit above
                # the Kivy surface and make the ad appear to be missing.
                self._banner_container = FrameLayout(self._activity)
                self._banner_container.setVisibility(View.GONE)
                self._banner_container.addView(self._adview, ad_lp)
                gravity = Gravity.TOP if top_pos else Gravity.BOTTOM
                gravity |= Gravity.CENTER_HORIZONTAL
                try:
                    root_lp = FrameLayoutParams(
                        LayoutParams.MATCH_PARENT,
                        LayoutParams.WRAP_CONTENT,
                        gravity,
                    )
                except Exception:
                    root_lp = FrameLayoutParams(
                        LayoutParams.MATCH_PARENT,
                        LayoutParams.WRAP_CONTENT,
                    )
                    try:
                        root_lp.gravity = gravity
                    except Exception:
                        pass
                self._activity.addContentView(self._banner_container, root_lp)

            @run_on_ui_thread
            def request_banner(self, options=None):
                self._banner_pending = True
                if not self._initialized:
                    print('Banner isteği: AdMob SDK başlatılması bekleniyor', flush=True)
                    return
                self._banner_pending = False
                if not self._adview or not getattr(self, '_banner_unit_id', ''):
                    print('Banner isteği: AdView veya reklam birimi yok', flush=True)
                    return
                try:
                    self._adview.loadAd(self._get_builder(options).build())
                    print('Banner reklam isteği gönderildi', flush=True)
                except Exception as e:
                    Logger.error(f'KivMob request_banner: {e}')

            @run_on_ui_thread
            def show_banner(self):
                self._banner_requested = True
                if self._banner_container:
                    # It is safe to make the container visible before the
                    # async load callback; AdView stays empty until loaded.
                    self._adview.setVisibility(View.VISIBLE)
                    self._banner_container.setVisibility(View.VISIBLE)

            @run_on_ui_thread
            def hide_banner(self):
                self._banner_requested = False
                if self._adview:
                    self._adview.setVisibility(View.GONE)
                if self._banner_container:
                    self._banner_container.setVisibility(View.GONE)

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
                    print('Interstitial isteği atlandı: SDK veya reklam birimi yok', flush=True)
                    return
                if not self._initialized:
                    self._interstitial_pending = True
                    print('Interstitial isteği: AdMob SDK başlatılması bekleniyor', flush=True)
                    return
                self._interstitial_pending = False
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
                                print(
                                    'Interstitial reklam yüklenemedi: '
                                    f'{error.getCode()} / {error.getDomain()} / '
                                    f'{error.getMessage()}',
                                    flush=True,
                                )
                            except Exception:
                                print('Interstitial reklam yüklenemedi', flush=True)

                    self._interstitial = None
                    self._interstitial_loaded = False
                    # Retain the callback; it is invoked asynchronously by
                    # Google after this Python frame has returned.
                    self._inter_load_cb = _InterLoadCb()
                    InterstitialAd.load(
                        self._activity,
                        self._interstitial_unit_id,
                        request,
                        self._inter_load_cb,
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
                    # Keep the callback and the ad reference alive while the
                    # full-screen activity is open.
                    bridge._inter_fullscreen_cb = _InterFullScreenCb()
                    ad.setFullScreenContentCallback(bridge._inter_fullscreen_cb)
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
                    legacy_ad = bridge._interstitial or ad
                    legacy_ad.setAdListener(listener)
                    legacy_ad.show()
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
                    print('Ödüllü isteği atlandı: SDK veya reklam birimi yok', flush=True)
                    return
                if not self._initialized:
                    self._rewarded_pending = True
                    print('Ödüllü isteği: AdMob SDK başlatılması bekleniyor', flush=True)
                    return
                self._rewarded_pending = False
                from jnius import PythonJavaClass, java_method

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
                            print(
                                'Ödüllü reklam yüklenemedi: '
                                f'{error.getCode()} / {error.getDomain()} / '
                                f'{error.getMessage()}',
                                flush=True,
                            )
                        except Exception:
                            print('Ödüllü reklam yüklenemedi', flush=True)

                self._rewarded = None
                self._rewarded_loaded = False
                self._reward_load_cb = _LoadCb()
                try:
                    RewardedAd.load(
                        self._activity,
                        self._rewarded_unit_id,
                        request,
                        self._reward_load_cb,
                    )
                except Exception as e:
                    Logger.error(f'KivMob request_rewarded: {e}')

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
                bridge._reward_fullscreen_cb = _FullScreenCb()
                bridge._reward_cb = _RewardCb()
                ad.setFullScreenContentCallback(bridge._reward_fullscreen_cb)
                ad.show(bridge._activity, bridge._reward_cb)

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
