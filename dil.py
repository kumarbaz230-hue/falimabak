"""FalımaBak — çoklu dil (TR + popüler diller)."""

from gecmis import dil_al as _dil_al, dil_kaydet

DESTEKLENEN = {
    'tr': 'Türkçe',
    'en': 'English',
    'de': 'Deutsch',
    'fr': 'Français',
    'es': 'Español',
    'ar': 'العربية',
    'ru': 'Русский',
    'pt': 'Português',
    'it': 'Italiano',
    'hi': 'हिन्दी',
    'id': 'Indonesia',
    'zh': '中文',
}

_METINLER = {
    'yorum_bekle': {
        'tr': 'FalımaBak yorumluyor...',
        'en': 'FalımaBak is reading...',
        'de': 'FalımaBak deutet...',
        'fr': 'FalımaBak interprète...',
        'es': 'FalımaBak interpreta...',
        'ar': 'FalımaBak يقرأ...',
        'ru': 'FalımaBak толкует...',
        'pt': 'FalımaBak interpreta...',
        'it': 'FalımaBak interpreta...',
        'hi': 'FalımaBak पढ़ रहा है...',
        'id': 'FalımaBak membaca...',
        'zh': 'FalımaBak 解读中...',
    },
    'yorum_baslik': {
        'tr': 'FalımaBak Yorumluyor',
        'en': 'FalımaBak Reading',
        'de': 'FalımaBak Deutung',
        'fr': 'Lecture FalımaBak',
        'es': 'Lectura FalımaBak',
        'ar': 'قراءة FalımaBak',
        'ru': 'Толкование FalımaBak',
        'pt': 'Leitura FalımaBak',
        'it': 'Lettura FalımaBak',
        'hi': 'FalımaBak पढ़ना',
        'id': 'Pembacaan FalımaBak',
        'zh': 'FalımaBak 解读',
    },
    'tus_geri': {'tr': 'Geri', 'en': 'Back', 'de': 'Zurück', 'fr': 'Retour', 'es': 'Atrás', 'ar': 'رجوع', 'ru': 'Назад', 'pt': 'Voltar', 'it': 'Indietro', 'hi': 'वापस', 'id': 'Kembali', 'zh': '返回'},
    'tus_fal_ac': {'tr': 'Fal Aç', 'en': 'Draw Cards', 'de': 'Karten ziehen', 'fr': 'Tirer', 'es': 'Abrir', 'ar': 'افتح', 'ru': 'Открыть', 'pt': 'Abrir', 'it': 'Apri', 'hi': 'खोलें', 'id': 'Buka', 'zh': '开牌'},
    'tus_tekrar': {'tr': 'Tekrar', 'en': 'Again', 'de': 'Nochmal', 'fr': 'Encore', 'es': 'Otra vez', 'ar': 'مرة أخرى', 'ru': 'Снова', 'pt': 'De novo', 'it': 'Ancora', 'hi': 'फिर', 'id': 'Lagi', 'zh': '再来'},
    'tus_galeri': {'tr': 'Galeri', 'en': 'Gallery', 'de': 'Galerie', 'fr': 'Galerie', 'es': 'Galería', 'ar': 'المعرض', 'ru': 'Галерея', 'pt': 'Galeria', 'it': 'Galleria', 'hi': 'गैलरी', 'id': 'Galeri', 'zh': '相册'},
    'tus_kamera': {'tr': 'Kamera', 'en': 'Camera', 'de': 'Kamera', 'fr': 'Caméra', 'es': 'Cámara', 'ar': 'الكamera', 'ru': 'Камера', 'pt': 'Câmera', 'it': 'Fotocamera', 'hi': 'कैमरा', 'id': 'Kamera', 'zh': '相机'},
    'tus_yorumla': {'tr': 'Yorumla', 'en': 'Interpret', 'de': 'Deuten', 'fr': 'Interpréter', 'es': 'Interpretar', 'ar': 'فسّر', 'ru': 'Толковать', 'pt': 'Interpretar', 'it': 'Interpreta', 'hi': 'व्याख्या', 'id': 'Tafsirkan', 'zh': '解读'},
    'tus_fal_bak': {'tr': 'Fala Bak', 'en': 'Read Fortune', 'de': 'Wahrsagen', 'fr': 'Lire', 'es': 'Leer fal', 'ar': 'اقرأ', 'ru': 'Гадать', 'pt': 'Ler', 'it': 'Leggi', 'hi': 'देखें', 'id': 'Baca', 'zh': '占卜'},
    'tus_bekle': {'tr': 'Bekleyin', 'en': 'Please wait', 'de': 'Bitte warten', 'fr': 'Patientez', 'es': 'Espere', 'ar': 'انتظر', 'ru': 'Подождите', 'pt': 'Aguarde', 'it': 'Attendi', 'hi': 'प्रतीक्षा', 'id': 'Tunggu', 'zh': '请稍候'},
    'tus_tamam': {'tr': 'Tamam', 'en': 'OK', 'de': 'OK', 'fr': 'OK', 'es': 'OK', 'ar': 'موافق', 'ru': 'ОК', 'pt': 'OK', 'it': 'OK', 'hi': 'ठीक', 'id': 'OK', 'zh': '确定'},
    'tus_burc_esles': {'tr': 'Eşleştir', 'en': 'Match Signs', 'de': 'Abgleichen', 'fr': 'Comparer', 'es': 'Emparejar', 'ar': 'طابق', 'ru': 'Сопоставить', 'pt': 'Combinar', 'it': 'Abbina', 'hi': 'मिलाएँ', 'id': 'Cocokkan', 'zh': '配对'},
    'tus_ruya_tabir': {'tr': 'Rüyayı Yorumla', 'en': 'Interpret Dream', 'de': 'Traum deuten', 'fr': 'Interpréter', 'es': 'Interpretar', 'ar': 'فسّر الحلم', 'ru': 'Толковать сон', 'pt': 'Interpretar', 'it': 'Interpreta', 'hi': 'सपना समझें', 'id': 'Tafsirkan', 'zh': '解梦'},
    'nav_home': {'tr': 'Ana Sayfa', 'en': 'Home', 'de': 'Start', 'fr': 'Accueil', 'es': 'Inicio', 'ar': 'الرئيسية', 'ru': 'Главная', 'pt': 'Início', 'it': 'Home', 'hi': 'होम', 'id': 'Beranda', 'zh': '首页'},
    'nav_history': {'tr': 'Geçmiş', 'en': 'History', 'de': 'Verlauf', 'fr': 'Historique', 'es': 'Historial', 'ar': 'السجل', 'ru': 'История', 'pt': 'Histórico', 'it': 'Cronologia', 'hi': 'इतिहास', 'id': 'Riwayat', 'zh': '历史'},
    'nav_settings': {'tr': 'Ayarlar', 'en': 'Settings', 'de': 'Einstellungen', 'fr': 'Réglages', 'es': 'Ajustes', 'ar': 'الإعدادات', 'ru': 'Настройки', 'pt': 'Ajustes', 'it': 'Impostazioni', 'hi': 'सेटिंग', 'id': 'Pengaturan', 'zh': '设置'},
    'settings_title': {'tr': 'Ayarlar', 'en': 'Settings', 'de': 'Einstellungen', 'fr': 'Réglages', 'es': 'Ajustes', 'ar': 'الإعدادات', 'ru': 'Настройки', 'pt': 'Ajustes', 'it': 'Impostazioni', 'hi': 'सेटिंग', 'id': 'Pengaturan', 'zh': '设置'},
    'settings_lang': {'tr': 'Dil', 'en': 'Language', 'de': 'Sprache', 'fr': 'Langue', 'es': 'Idioma', 'ar': 'اللغة', 'ru': 'Язык', 'pt': 'Idioma', 'it': 'Lingua', 'hi': 'भाषा', 'id': 'Bahasa', 'zh': '语言'},
    'settings_lang_hint': {'tr': 'Uygulama dili anında değişir', 'en': 'App language changes instantly', 'de': 'Sprache sofort ändern', 'fr': 'Langue instantanée', 'es': 'Cambio instantáneo', 'ar': 'تغيير فوري', 'ru': 'Мгновенная смена', 'pt': 'Mudança instantânea', 'it': 'Cambio immediato', 'hi': 'तुरंत बदलें', 'id': 'Langsung berubah', 'zh': '即时切换'},
    'settings_profile': {'tr': 'Profil', 'en': 'Profile', 'de': 'Profil', 'fr': 'Profil', 'es': 'Perfil', 'ar': 'الملف', 'ru': 'Профиль', 'pt': 'Perfil', 'it': 'Profilo', 'hi': 'प्रोफ़ाइल', 'id': 'Profil', 'zh': '资料'},
    'settings_profile_hint': {'tr': 'Adınız yorumlarda kullanılır', 'en': 'Name used in readings', 'de': 'Name in Deutungen', 'fr': 'Nom dans les lectures', 'es': 'Nombre en lecturas', 'ar': 'الاسم في القراءات', 'ru': 'Имя в толкованиях', 'pt': 'Nome nas leituras', 'it': 'Nome nelle letture', 'hi': 'नाम पढ़ाई में', 'id': 'Nama di bacaan', 'zh': '解读中显示姓名'},
    'settings_name_hint': {'tr': 'İsteğe bağlı', 'en': 'Optional', 'de': 'Optional', 'fr': 'Optionnel', 'es': 'Opcional', 'ar': 'اختياري', 'ru': 'Необязательно', 'pt': 'Opcional', 'it': 'Opzionale', 'hi': 'वैकल्पिक', 'id': 'Opsional', 'zh': '可选'},
    'settings_ai': {'tr': 'Gelişmiş — Bulut yorum', 'en': 'Advanced — Cloud reading', 'de': 'Erweitert — Cloud', 'fr': 'Avancé — Cloud', 'es': 'Avanzado — Nube', 'ar': 'متقدم — سحابة', 'ru': 'Дополнительно — облако', 'pt': 'Avançado — Nuvem', 'it': 'Avanzate — Cloud', 'hi': 'उन्नत — क्लाउड', 'id': 'Lanjutan — Cloud', 'zh': '高级 — 云端'},
    'settings_ai_hint': {'tr': 'Boş bırakırsanız cihaz içi yorum kullanılır', 'en': 'Leave empty for on-device reading', 'de': 'Leer = Gerät', 'fr': 'Vide = appareil', 'es': 'Vacío = dispositivo', 'ar': 'فارغ = الجهاز', 'ru': 'Пусто = на устройстве', 'pt': 'Vazio = dispositivo', 'it': 'Vuoto = dispositivo', 'hi': 'खाली = डिवाइस', 'id': 'Kosong = perangkat', 'zh': '留空=本地'},
    'settings_data': {'tr': 'Veri ve geçmiş', 'en': 'Data & history', 'de': 'Daten & Verlauf', 'fr': 'Données', 'es': 'Datos', 'ar': 'البيانات', 'ru': 'Данные', 'pt': 'Dados', 'it': 'Dati', 'hi': 'डेटा', 'id': 'Data', 'zh': '数据'},
    'settings_save': {'tr': 'Ayarları kaydet', 'en': 'Save settings', 'de': 'Speichern', 'fr': 'Enregistrer', 'es': 'Guardar', 'ar': 'حفظ', 'ru': 'Сохранить', 'pt': 'Salvar', 'it': 'Salva', 'hi': 'सहेजें', 'id': 'Simpan', 'zh': '保存'},
    'settings_clear': {'tr': 'Fal geçmişini temizle', 'en': 'Clear history', 'de': 'Verlauf löschen', 'fr': 'Effacer', 'es': 'Borrar historial', 'ar': 'مسح السجل', 'ru': 'Очişтить', 'pt': 'Limpar', 'it': 'Cancella', 'hi': 'साफ़ करें', 'id': 'Hapus riwayat', 'zh': '清除历史'},
    'settings_saved': {'tr': 'Ayarlar kaydedildi', 'en': 'Settings saved', 'de': 'Gespeichert', 'fr': 'Enregistré', 'es': 'Guardado', 'ar': 'تم الحفظ', 'ru': 'Сохранено', 'pt': 'Salvo', 'it': 'Salvato', 'hi': 'सहेजा गया', 'id': 'Disimpan', 'zh': '已保存'},
    'settings_cleared': {'tr': 'Fal geçmişi temizlendi', 'en': 'History cleared', 'de': 'Gelöscht', 'fr': 'Effacé', 'es': 'Borrado', 'ar': 'تم المسح', 'ru': 'Очищено', 'pt': 'Limpo', 'it': 'Cancellato', 'hi': 'साफ़', 'id': 'Dihapus', 'zh': '已清除'},
    'settings_clear_fail': {'tr': 'Temizleme başarısız', 'en': 'Clear failed', 'de': 'Fehler', 'fr': 'Échec', 'es': 'Error', 'ar': 'فشل', 'ru': 'Ошибка', 'pt': 'Falhou', 'it': 'Errore', 'hi': 'विफल', 'id': 'Gagal', 'zh': '失败'},
    'settings_legal': {'tr': 'Yasal', 'en': 'Legal', 'de': 'Rechtliches', 'fr': 'Mentions légales', 'es': 'Legal', 'ar': 'قانوني', 'ru': 'Правовая информация', 'pt': 'Legal', 'it': 'Legale', 'hi': 'कानूनी', 'id': 'Legal', 'zh': '法律'},
    'settings_legal_hint': {'tr': 'Gizlilik politikası ve veri kullanımı', 'en': 'Privacy policy and data use', 'de': 'Datenschutz', 'fr': 'Confidentialité', 'es': 'Privacidad', 'ar': 'الخصوصية', 'ru': 'Конфиденциальность', 'pt': 'Privacidade', 'it': 'Privacy', 'hi': 'गोपनीयता', 'id': 'Privasi', 'zh': '隐私'},
    'settings_music': {'tr': 'Arka Plan Müziği', 'en': 'Background Music', 'de': 'Hintergrundmusik', 'fr': 'Musique de fond', 'es': 'Música de fondo', 'ar': 'موسيقى الخلفية', 'ru': 'Фоновая музыка', 'pt': 'Música de fundo', 'it': 'Musica di sottofondo', 'hi': 'पृष्ठभूमि संगीत', 'id': 'Musik latar', 'zh': '背景音乐'},
    'settings_music_hint': {'tr': 'Gerilim/atmosfer müziği — istediğiniz zaman kapatabilirsiniz', 'en': 'Atmospheric music — toggle anytime', 'de': 'Atmosphäre — jederzeit aus', 'fr': 'Ambiance — désactivable', 'es': 'Ambiente — apaga cuando quieras', 'ar': 'أجواء — يمكن إيقافها', 'ru': 'Атмосфера — можно выключить', 'pt': 'Ambiente — desligue quando quiser', 'it': 'Atmosfera — disattivabile', 'hi': 'माहौल — बंद कर सकते हैं', 'id': 'Suasana — bisa dimatikan', 'zh': '氛围音乐 — 可随时关闭'},
    'settings_music_on': {'tr': 'Müzik: Açık', 'en': 'Music: On', 'de': 'Musik: An', 'fr': 'Musique: Oui', 'es': 'Música: Sí', 'ar': 'الموسيقى: تشغيل', 'ru': 'Музыка: вкл', 'pt': 'Música: ligada', 'it': 'Musica: on', 'hi': 'संगीत: चालू', 'id': 'Musik: nyala', 'zh': '音乐：开'},
    'settings_music_off': {'tr': 'Müzik: Kapalı', 'en': 'Music: Off', 'de': 'Musik: Aus', 'fr': 'Musique: Non', 'es': 'Música: No', 'ar': 'الموسيقى: إيقاف', 'ru': 'Музыка: выкл', 'pt': 'Música: desligada', 'it': 'Musica: off', 'hi': 'संगीत: बंद', 'id': 'Musik: mati', 'zh': '音乐：关'},
    'settings_volume': {'tr': 'Ses seviyesi', 'en': 'Volume', 'de': 'Lautstärke', 'fr': 'Volume', 'es': 'Volumen', 'ar': 'مستوى الصوت', 'ru': 'Громкость', 'pt': 'Volume', 'it': 'Volume', 'hi': 'आवाज़', 'id': 'Volume', 'zh': '音量'},
    'cookie_title': {'tr': 'Günlük Şans Kurabiyesi', 'en': 'Daily Fortune Cookie', 'de': 'Glückskeks', 'fr': 'Biscuit de fortune', 'es': 'Galleta de la suerte', 'ar': 'كعكة الحظ', 'ru': 'Печенье с предсказанием', 'pt': 'Biscoito da sorte', 'it': 'Biscotto della fortuna', 'hi': 'भाग्य कुकी', 'id': 'Kue keberuntungan', 'zh': '幸运饼干'},
    'cookie_hint': {'tr': 'Dokun ve bugünkü mesajını aç — günde 1 kez!', 'en': 'Tap to open today\'s message — once per day!', 'de': 'Tippen — 1× pro Tag', 'fr': 'Touchez — 1× par jour', 'es': 'Toca — 1 vez al día', 'ar': 'اضغط — مرة واحدة يومياً', 'ru': 'Нажмите — раз в день', 'pt': 'Toque — 1× por dia', 'it': 'Tocca — 1 volta al giorno', 'hi': 'टैप करें — दिन में एक बार', 'id': 'Ketuk — 1× sehari', 'zh': '点击打开 — 每天一次'},
    'cookie_hint_opened': {'tr': 'Bugünkü kurabiyeni açtın ✓ Yarın yeni mesaj!', 'en': 'Opened today ✓ New message tomorrow!', 'de': 'Heute geöffnet ✓', 'fr': 'Ouvert aujourd\'hui ✓', 'es': 'Abierta hoy ✓', 'ar': 'فُتحت اليوم ✓', 'ru': 'Открыто сегодня ✓', 'pt': 'Aberto hoje ✓', 'it': 'Aperto oggi ✓', 'hi': 'आज खोला ✓', 'id': 'Dibuka hari ini ✓', 'zh': '今日已打开 ✓'},
    'cookie_already': {'tr': 'Bugün zaten açtın. Yarın yeni bir mesaj seni bekliyor!', 'en': 'Already opened today. Come back tomorrow!', 'de': 'Heute schon geöffnet.', 'fr': 'Déjà ouvert aujourd\'hui.', 'es': 'Ya abierta hoy.', 'ar': 'فُتحت اليوم بالفعل.', 'ru': 'Уже открыто сегодня.', 'pt': 'Já aberto hoje.', 'it': 'Già aperto oggi.', 'hi': 'आज पहले ही खोला।', 'id': 'Sudah dibuka hari ini.', 'zh': '今日已打开过。'},
    'cookie_close': {'tr': 'Tamam', 'en': 'OK', 'de': 'OK', 'fr': 'OK', 'es': 'OK', 'ar': 'حسناً', 'ru': 'OK', 'pt': 'OK', 'it': 'OK', 'hi': 'ठीक', 'id': 'OK', 'zh': '确定'},
    'exit_title': {'tr': 'Çıkış', 'en': 'Exit', 'de': 'Beenden', 'fr': 'Quitter', 'es': 'Salir', 'ar': 'خروج', 'ru': 'Выход', 'pt': 'Sair', 'it': 'Esci', 'hi': 'बाहर', 'id': 'Keluar', 'zh': '退出'},
    'exit_msg': {'tr': 'Uygulamayı kapatmak istiyor musunuz?', 'en': 'Do you want to close the app?', 'de': 'App schließen?', 'fr': 'Fermer l\'application ?', 'es': '¿Cerrar la aplicación?', 'ar': 'هل تريد إغلاق التطبيق؟', 'ru': 'Закрыть приложение?', 'pt': 'Fechar o aplicativo?', 'it': 'Chiudere l\'app?', 'hi': 'ऐप बंद करें?', 'id': 'Tutup aplikasi?', 'zh': '要关闭应用吗？'},
    'exit_yes': {'tr': 'Evet', 'en': 'Yes', 'de': 'Ja', 'fr': 'Oui', 'es': 'Sí', 'ar': 'نعم', 'ru': 'Да', 'pt': 'Sim', 'it': 'Sì', 'hi': 'हाँ', 'id': 'Ya', 'zh': '是'},
    'exit_no': {'tr': 'Hayır', 'en': 'No', 'de': 'Nein', 'fr': 'Non', 'es': 'No', 'ar': 'لا', 'ru': 'Нет', 'pt': 'Não', 'it': 'No', 'hi': 'नहीं', 'id': 'Tidak', 'zh': '否'},
    'limit_title': {'tr': 'Günlük Fal Limiti', 'en': 'Daily Reading Limit', 'de': 'Tageslimit', 'fr': 'Limite quotidienne', 'es': 'Límite diario', 'ar': 'حد يومي', 'ru': 'Дневной лимит', 'pt': 'Limite diário', 'it': 'Limite giornaliero', 'hi': 'दैनिक सीमा', 'id': 'Batas harian', 'zh': '每日限额'},
    'limit_msg': {'tr': '{tip} için bugünkü ücretsiz falınızı kullandınız. Devam etmek için ödüllü reklam izleyin (+1 fal, bugün {reklam_kalan}/{reklam_max} reklam hakkı).', 'en': 'Today\'s free {tip} reading used. Watch a rewarded ad for +1 ({reklam_kalan}/{reklam_max} left).', 'de': 'Gratis-{tip} verbraucht. Werbung für +1 ({reklam_kalan}/{reklam_max}).', 'fr': '{tip} gratuit utilisé. Pub pour +1 ({reklam_kalan}/{reklam_max}).', 'es': '{tip} gratis usado. Anuncio para +1 ({reklam_kalan}/{reklam_max}).', 'ar': 'انتهى {tip} المجاني. إعلان لـ +1 ({reklam_kalan}/{reklam_max}).', 'ru': 'Бесплатный {tip} использован. Реклама +1 ({reklam_kalan}/{reklam_max}).', 'pt': '{tip} grátis usado. Anúncio +1 ({reklam_kalan}/{reklam_max}).', 'it': '{tip} gratis usato. Annuncio +1 ({reklam_kalan}/{reklam_max}).', 'hi': 'मुफ़्त {tip} खत्म। +1 के लिए विज्ञापन ({reklam_kalan}/{reklam_max})।', 'id': '{tip} gratis habis. Iklan +1 ({reklam_kalan}/{reklam_max}).', 'zh': '今日免费{tip}已用。奖励广告+1（{reklam_kalan}/{reklam_max}）。'},
    'limit_reklam_doldu': {'tr': 'Bugün {tip} için tüm haklarınız doldu (1 ücretsiz + {reklam_max} reklam). Yarın yenilenir.', 'en': 'All {tip} slots used today (1 free + {reklam_max} ads). Resets tomorrow.', 'de': 'Alle {tip}-Haken heute (1 gratis + {reklam_max} Werbung). Morgen neu.', 'fr': 'Tous les {tip} aujourd\'hui (1 gratuit + {reklam_max} pubs). Demain.', 'es': 'Todo {tip} hoy (1 gratis + {reklam_max} anuncios). Mañana.', 'ar': 'نفدت كل {tip} (1 مجاني + {reklam_max} إعلان). غداً.', 'ru': 'Все {tip} сегодня (1 бесплатно + {reklam_max} реклам). Завтра.', 'pt': 'Tudo em {tip} hoje (1 grátis + {reklam_max} anúncios). Amanhã.', 'it': 'Tutto {tip} oggi (1 gratis + {reklam_max} annunci). Domani.', 'hi': 'आज {tip} समाप्त (1 मुफ़्त + {reklam_max} विज्ञापन)।', 'id': 'Semua {tip} hari ini (1 gratis + {reklam_max} iklan). Besok.', 'zh': '今日{tip}已用完（1免费+{reklam_max}广告）。明日重置。'},
    'limit_watch_ad': {'tr': 'Ödüllü Reklam İzle', 'en': 'Watch Rewarded Ad', 'de': 'Belohnte Werbung', 'fr': 'Pub récompensée', 'es': 'Anuncio recompensado', 'ar': 'إعلان بمكافأة', 'ru': 'Реклама с наградой', 'pt': 'Anúncio recompensado', 'it': 'Annuncio premiato', 'hi': 'इनाम वाला विज्ञापन', 'id': 'Iklan berhadiah', 'zh': '观看奖励广告'},
    'limit_no': {'tr': 'Vazgeç', 'en': 'Cancel', 'de': 'Abbrechen', 'fr': 'Annuler', 'es': 'Cancelar', 'ar': 'إلغاء', 'ru': 'Отмена', 'pt': 'Cancelar', 'it': 'Annulla', 'hi': 'रद्द', 'id': 'Batal', 'zh': '取消'},
    'limit_ad_fail': {'tr': 'Reklam yüklenemedi. İnternetinizi kontrol edin. Yeni AdMob hesaplarında onay süreci nedeniyle reklam gelmeyebilir — birkaç saat veya gün sonra tekrar deneyin.', 'en': 'Ad failed to load. Check internet. New AdMob apps may have no fill until approved.', 'de': 'Werbung nicht geladen. AdMob-Freigabe kann dauern.', 'fr': 'Pub non chargée. Approbation AdMob en cours possible.', 'es': 'Anuncio no cargado. AdMob puede tardar en aprobar.', 'ar': 'فشل تحميل الإعلان. قد يكون AdMob قيد الموافقة.', 'ru': 'Реклама не загрузилась. Возможно, AdMob ещё не одобрен.', 'pt': 'Anúncio não carregou. AdMob pode estar pendente.', 'it': 'Annuncio non caricato. AdMob in approvazione.', 'hi': 'विज्ञापन लोड नहीं हुआ। AdMob अनुमोदन लंबित हो सकता है।', 'id': 'Iklan gagal. AdMob mungkin belum disetujui.', 'zh': '广告加载失败。AdMob 可能尚未批准。'},
    'limit_retry': {'tr': 'Tekrar Dene', 'en': 'Retry', 'de': 'Erneut', 'fr': 'Réessayer', 'es': 'Reintentar', 'ar': 'إعادة', 'ru': 'Повторить', 'pt': 'Tentar de novo', 'it': 'Riprova', 'hi': 'पुनः', 'id': 'Coba lagi', 'zh': '重试'},
    'coin_title': {'tr': 'Coinler', 'en': 'Coins', 'de': 'Münzen', 'fr': 'Pièces', 'es': 'Monedas', 'ar': 'عملات', 'ru': 'Монеты', 'pt': 'Moedas', 'it': 'Monete', 'hi': 'सिक्के', 'id': 'Koin', 'zh': '金币'},
    'coin_balance': {'tr': 'Bakiyeniz: {coin} coin', 'en': 'Balance: {coin} coins', 'de': 'Guthaben: {coin}', 'fr': 'Solde : {coin}', 'es': 'Saldo: {coin}', 'ar': 'الرصيد: {coin}', 'ru': 'Баланс: {coin}', 'pt': 'Saldo: {coin}', 'it': 'Saldo: {coin}', 'hi': 'शेष: {coin}', 'id': 'Saldo: {coin}', 'zh': '余额：{coin}'},
    'coin_fal_cost': {'tr': 'Her fal {cost} coin harcar (burç eşleşmesi ve rüya tabiri dahil).', 'en': 'Each reading costs {cost} coin (including zodiac match and dream interpretation).', 'de': 'Jede Deutung kostet {cost} Münze.', 'fr': 'Chaque lecture coûte {cost} pièce.', 'es': 'Cada lectura cuesta {cost} moneda.', 'ar': 'كل قراءة {cost} عملة.', 'ru': 'Каждое гадание — {cost} монета.', 'pt': 'Cada leitura custa {cost} moeda.', 'it': 'Ogni lettura costa {cost} moneta.', 'hi': 'प्रति फ़ाल {cost} सिक्का।', 'id': 'Setiap bacaan {cost} koin.', 'zh': '每次占卜消耗 {cost} 金币。'},
    'coin_ad_info': {'tr': 'Reklam izle → +{odul} coin (bugün {kalan}/{max} hak)', 'en': 'Watch ad → +{odul} coins ({kalan}/{max} today)', 'de': 'Werbung → +{odul} ({kalan}/{max})', 'fr': 'Pub → +{odul} ({kalan}/{max})', 'es': 'Anuncio → +{odul} ({kalan}/{max})', 'ar': 'إعلان → +{odul} ({kalan}/{max})', 'ru': 'Реклама → +{odul} ({kalan}/{max})', 'pt': 'Anúncio → +{odul} ({kalan}/{max})', 'it': 'Annuncio → +{odul} ({kalan}/{max})', 'hi': 'विज्ञापन → +{odul} ({kalan}/{max})', 'id': 'Iklan → +{odul} ({kalan}/{max})', 'zh': '看广告 → +{odul}（今日 {kalan}/{max}）'},
    'coin_watch_ad': {'tr': 'Reklam İzle (+{odul} coin)', 'en': 'Watch Ad (+{odul})', 'de': 'Werbung (+{odul})', 'fr': 'Pub (+{odul})', 'es': 'Anuncio (+{odul})', 'ar': 'إعلان (+{odul})', 'ru': 'Реклама (+{odul})', 'pt': 'Anúncio (+{odul})', 'it': 'Annuncio (+{odul})', 'hi': 'विज्ञापन (+{odul})', 'id': 'Iklan (+{odul})', 'zh': '看广告 (+{odul})'},
    'coin_close': {'tr': 'Kapat', 'en': 'Close', 'de': 'Schließen', 'fr': 'Fermer', 'es': 'Cerrar', 'ar': 'إغلاق', 'ru': 'Закрыть', 'pt': 'Fechar', 'it': 'Chiudi', 'hi': 'बंद', 'id': 'Tutup', 'zh': '关闭'},
    'coin_fal_need': {'tr': '{tip} falı için {cost} coin gerekli. Coin kazanmak için reklam izleyebilirsiniz.', 'en': '{tip} needs {cost} coin. Watch ads to earn coins.', 'de': '{tip} braucht {cost} Münzen.', 'fr': '{tip} nécessite {cost} pièce.', 'es': '{tip} requiere {cost} moneda.', 'ar': '{tip} يحتاج {cost} عملة.', 'ru': 'Для {tip} нужно {cost} монет.', 'pt': '{tip} precisa de {cost} moeda.', 'it': '{tip} richiede {cost} moneta.', 'hi': '{tip} के लिए {cost} सिक्का।', 'id': '{tip} butuh {cost} koin.', 'zh': '{tip} 需要 {cost} 金币。'},
    'coin_get_coins': {'tr': 'Coin Kazan', 'en': 'Get Coins', 'de': 'Münzen', 'fr': 'Gagner', 'es': 'Obtener', 'ar': 'اكسب', 'ru': 'Получить', 'pt': 'Ganhar', 'it': 'Ottieni', 'hi': 'सिक्के', 'id': 'Dapatkan', 'zh': '获取金币'},
    'coin_welcome_title': {'tr': 'Hoş Geldin!', 'en': 'Welcome!', 'de': 'Willkommen!', 'fr': 'Bienvenue !', 'es': '¡Bienvenido!', 'ar': 'مرحباً!', 'ru': 'Добро пожаловать!', 'pt': 'Bem-vindo!', 'it': 'Benvenuto!', 'hi': 'स्वागत!', 'id': 'Selamat datang!', 'zh': '欢迎！'},
    'coin_welcome': {'tr': 'FalımaBak\'a hoş geldin! Hediye olarak {bonus} coin kazandın. Her fal 1 coin harcar.', 'en': 'Welcome! You received {bonus} coins. Each reading costs 1 coin.', 'de': 'Willkommen! {bonus} Münzen geschenkt.', 'fr': 'Bienvenue ! {bonus} pièces offertes.', 'es': '¡Bienvenido! {bonus} monedas de regalo.', 'ar': 'مرحباً! {bonus} عملة هدية.', 'ru': 'Добро пожаловать! {bonus} монет в подарок.', 'pt': 'Bem-vindo! {bonus} moedas de presente.', 'it': 'Benvenuto! {bonus} monete in regalo.', 'hi': 'स्वागत! {bonus} सिक्के मिले।', 'id': 'Selamat datang! {bonus} koin hadiah.', 'zh': '欢迎！赠送 {bonus} 金币。'},
    'coin_welcome_ok': {'tr': 'Harika!', 'en': 'Great!', 'de': 'Super!', 'fr': 'Super !', 'es': '¡Genial!', 'ar': 'رائع!', 'ru': 'Отлично!', 'pt': 'Ótimo!', 'it': 'Ottimo!', 'hi': 'बढ़िया!', 'id': 'Mantap!', 'zh': '太好了！'},
    'coin_welcome_first': {'tr': 'FalımaBak\'a hoş geldin! {bonus} coin hoşgeldin hediyesi + {gunluk} coin bugünkü giriş bonusu. Toplam: {toplam} coin. Her fal 1 coin harcar.', 'en': 'Welcome! {bonus} welcome + {gunluk} daily login bonus. Total: {toplam} coins.', 'de': 'Willkommen! {bonus}+{gunluk} Münzen. Gesamt: {toplam}.', 'fr': 'Bienvenue ! {bonus}+{gunluk} pièces. Total : {toplam}.', 'es': '¡Bienvenido! {bonus}+{gunluk} monedas. Total: {toplam}.', 'ar': 'مرحباً! {bonus}+{gunluk} عملة. المجموع: {toplam}.', 'ru': 'Добро пожаловать! {bonus}+{gunluk}. Итого: {toplam}.', 'pt': 'Bem-vindo! {bonus}+{gunluk}. Total: {toplam}.', 'it': 'Benvenuto! {bonus}+{gunluk}. Totale: {toplam}.', 'hi': 'स्वागत! {bonus}+{gunluk}। कुल: {toplam}.', 'id': 'Selamat datang! {bonus}+{gunluk}. Total: {toplam}.', 'zh': '欢迎！{bonus}+{gunluk}。共 {toplam} 金币。'},
    'coin_daily_title': {'tr': 'Günlük Bonus', 'en': 'Daily Bonus', 'de': 'Tagesbonus', 'fr': 'Bonus quotidien', 'es': 'Bonus diario', 'ar': 'مكافأة يومية', 'ru': 'Ежедневный бонус', 'pt': 'Bônus diário', 'it': 'Bonus giornaliero', 'hi': 'दैनिक बोनस', 'id': 'Bonus harian', 'zh': '每日奖励'},
    'coin_daily': {'tr': 'Bugünkü giriş bonusun: +{bonus} coin! Bakiyen: {toplam} coin. Her gün uygulamaya gir, coin kazan.', 'en': 'Daily login bonus: +{bonus} coins! Balance: {toplam}. Come back every day!', 'de': 'Tagesbonus: +{bonus}! Guthaben: {toplam}.', 'fr': 'Bonus du jour : +{bonus} ! Solde : {toplam}.', 'es': 'Bonus diario: +{bonus}. Saldo: {toplam}.', 'ar': 'مكافأة اليوم: +{bonus}. الرصيد: {toplam}.', 'ru': 'Бонус дня: +{bonus}. Баланс: {toplam}.', 'pt': 'Bônus diário: +{bonus}. Saldo: {toplam}.', 'it': 'Bonus giornaliero: +{bonus}. Saldo: {toplam}.', 'hi': 'दैनिक बोनस: +{bonus}। शेष: {toplam}.', 'id': 'Bonus harian: +{bonus}. Saldo: {toplam}.', 'zh': '每日奖励 +{bonus}！余额 {toplam}。'},
    'settings_privacy': {'tr': 'Gizlilik Politikasını Aç', 'en': 'Open Privacy Policy', 'de': 'Datenschutz öffnen', 'fr': 'Politique de confidentialité', 'es': 'Política de privacidad', 'ar': 'سياسة الخصوصية', 'ru': 'Политика конфиденциальности', 'pt': 'Política de privacidade', 'it': 'Informativa privacy', 'hi': 'गोपनीयता नीति', 'id': 'Kebijakan privasi', 'zh': '隐私政策'},
    'settings_rate': {'tr': 'Uygulamayı Değerlendir ⭐', 'en': 'Rate the App ⭐', 'de': 'App bewerten ⭐', 'fr': 'Noter l\'app ⭐', 'es': 'Valorar la app ⭐', 'ar': 'قيّم التطبيق ⭐', 'ru': 'Оценить ⭐', 'pt': 'Avaliar ⭐', 'it': 'Valuta ⭐', 'hi': 'ऐप रेट करें ⭐', 'id': 'Nilai aplikasi ⭐', 'zh': '评价应用 ⭐'},
    'privacy_title': {'tr': 'Gizlilik Politikası', 'en': 'Privacy Policy', 'de': 'Datenschutz', 'fr': 'Confidentialité', 'es': 'Privacidad', 'ar': 'الخصوصية', 'ru': 'Конфиденциальность', 'pt': 'Privacidade', 'it': 'Privacy', 'hi': 'गोपनीयता', 'id': 'Privasi', 'zh': '隐私政策'},
    'privacy_body': {
        'tr': (
            'FalımaBak tarot, kahve, el, astroloji ve benzeri fal yorumları sunar.\n\n'
            'Toplanan veriler:\n'
            '• İsteğe bağlı profil adı (cihazınızda)\n'
            '• Fal geçmişi (cihazınızda, ayarlardan silinebilir)\n'
            '• Kahve/el falı fotoğrafları (yorum için işlenir)\n'
            '• Dil tercihi\n'
            '• Reklam kimliği (Google AdMob)\n\n'
            'Üçüncü taraf: Google AdMob (reklamlar), bulut yorum servisi (internet gerekir).\n\n'
            'İzinler: Kamera, internet.\n\n'
            'Uygulama 13 yaş altına yönelik değildir. Fal yorumları eğlence amaçlıdır.\n\n'
            'İletişim: github.com/kumarbaz230-hue/falimabak'
        ),
        'en': (
            'FalımaBak offers fortune readings (tarot, coffee, palm, astrology).\n\n'
            'Data: optional name, reading history (on device), photos for readings, language, ad ID (AdMob).\n'
            'Third parties: Google AdMob, cloud reading service (internet required).\n'
            'Entertainment only. Not for users under 13.'
        ),
    },
    'menu_fortunes': {'tr': 'Fallarınız', 'en': 'Your Fortunes', 'de': 'Ihre Fall', 'fr': 'Vos oracles', 'es': 'Tus lecturas', 'ar': 'قراءاتك', 'ru': 'Ваши гадания', 'pt': 'Suas leituras', 'it': 'I tuoi oracoli', 'hi': 'आपके फ़ाल', 'id': 'Ramalan Anda', 'zh': '您的占卜'},
    'menu_tarot': {'tr': 'Tarot Falı', 'en': 'Tarot Reading', 'de': 'Tarot', 'fr': 'Tarot', 'es': 'Tarot', 'ar': 'تاروت', 'ru': 'Таро', 'pt': 'Tarô', 'it': 'Tarocchi', 'hi': 'टैरो', 'id': 'Tarot', 'zh': '塔罗'},
    'menu_tarot_desc': {'tr': '78 kartlık deste ile geleceğinizi görün', 'en': 'See your future with 78 cards', 'de': '78 Karten', 'fr': '78 cartes', 'es': '78 cartas', 'ar': '78 بطاقة', 'ru': '78 карт', 'pt': '78 cartas', 'it': '78 carte', 'hi': '78 कार्ड', 'id': '78 kartu', 'zh': '78张牌'},
    'menu_kahve': {'tr': 'Kahve Falı', 'en': 'Coffee Reading', 'de': 'Kaffeesatz', 'fr': 'Café', 'es': 'Café', 'ar': 'فنجان', 'ru': 'Кофе', 'pt': 'Café', 'it': 'Caffè', 'hi': 'कॉफ़ी', 'id': 'Kopi', 'zh': '咖啡占卜'},
    'menu_kahve_desc': {'tr': 'Fincanınızı fotoğraflayın, yorumlayalım', 'en': 'Photograph your cup', 'de': 'Tasse fotografieren', 'fr': 'Photographiez la tasse', 'es': 'Fotografía la taza', 'ar': 'صوّر الفنجان', 'ru': 'Сфотографируйте чашку', 'pt': 'Fotografe a xícara', 'it': 'Fotografa la tazza', 'hi': 'कप की फोटो', 'id': 'Foto cangkir', 'zh': '拍摄咖啡杯'},
    'menu_astro': {'tr': 'Yıldız Falı', 'en': 'Astrology', 'de': 'Astrologie', 'fr': 'Astrologie', 'es': 'Astrología', 'ar': 'الأبراج', 'ru': 'Аstro', 'pt': 'Astrologia', 'it': 'Astrologia', 'hi': 'ज्योतिष', 'id': 'Astrologi', 'zh': '星座'},
    'menu_astro_desc': {'tr': 'Burcunuza özel yorumlar', 'en': 'Sign-based readings', 'de': 'Nach Sternzeichen', 'fr': 'Par signe', 'es': 'Por signo', 'ar': 'حسب البرج', 'ru': 'По знаку', 'pt': 'Por signo', 'it': 'Per segno', 'hi': 'राशि अनुसार', 'id': 'Menurut zodiak', 'zh': '星座解读'},
    'menu_el': {'tr': 'El Falı', 'en': 'Palm Reading', 'de': 'Handlesen', 'fr': 'Chiromancie', 'es': 'Quiromancia', 'ar': 'قراءة الكف', 'ru': 'Хиромантия', 'pt': 'Quiromancia', 'it': 'Chiromanzia', 'hi': 'हस्तरेखा', 'id': 'Palmistry', 'zh': '手相'},
    'menu_el_desc': {'tr': 'Avuç içi çizgilerinizi okuyun', 'en': 'Read your palm lines', 'de': 'Handlinien', 'fr': 'Lignes de la main', 'es': 'Líneas de la mano', 'ar': 'خطوط الكف', 'ru': 'Линии ладони', 'pt': 'Linhas da mão', 'it': 'Linee del palmo', 'hi': 'हथेली की रेखाएँ', 'id': 'Garis telapak', 'zh': '掌纹解读'},
    'menu_diger': {'tr': 'Diğer Fallar', 'en': 'More Readings', 'de': 'Weitere', 'fr': 'Autres', 'es': 'Más lecturas', 'ar': 'المزيد', 'ru': 'Другие', 'pt': 'Outros', 'it': 'Altri', 'hi': 'अन्य', 'id': 'Lainnya', 'zh': '更多'},
    'menu_diger_desc': {'tr': 'İskambil, çiçek, nazar ve daha fazlası', 'en': 'Cards, flowers, evil eye & more', 'de': 'Karten, Blumen & mehr', 'fr': 'Cartes, fleurs & plus', 'es': 'Cartas, flores y más', 'ar': 'المزيد من الفال', 'ru': 'И многое другое', 'pt': 'Cartas, flores e mais', 'it': 'Carte, fiori e altro', 'hi': 'और भी', 'id': 'Dan lainnya', 'zh': '更多占卜'},
    'menu_burc_esles': {'tr': 'Burç Eşleşmesi', 'en': 'Zodiac Match', 'de': 'Sternzeichen-Match', 'fr': 'Compatibilité', 'es': 'Compatibilidad', 'ar': 'توافق الأبراج', 'ru': 'Совместимость', 'pt': 'Compatibilidade', 'it': 'Compatibilità', 'hi': 'राशि मिलान', 'id': 'Kecocokan Zodiak', 'zh': '星座配对'},
    'menu_burc_esles_desc': {'tr': 'İki kişinin burç uyumunu keşfedin', 'en': 'Discover zodiac compatibility', 'de': 'Sternzeichen-Harmonie', 'fr': 'Harmonie des signes', 'es': 'Armonía de signos', 'ar': 'اكتشف التوافق', 'ru': 'Узнайте совместимость', 'pt': 'Descubra a harmonia', 'it': 'Scopri l\'armonia', 'hi': 'राशि मेल जानें', 'id': 'Temukan kecocokan', 'zh': '探索星座契合度'},
    'menu_ruya': {'tr': 'Rüya Tabiri', 'en': 'Dream Interpretation', 'de': 'Traumdeutung', 'fr': 'Interprétation des rêves', 'es': 'Interpretación de sueños', 'ar': 'تفسير الأحلام', 'ru': 'Толкование снов', 'pt': 'Interpretação de sonhos', 'it': 'Interpretazione dei sogni', 'hi': 'सपने की व्याख्या', 'id': 'Tafsir Mimpi', 'zh': '解梦'},
    'menu_ruya_desc': {'tr': 'Rüyanızı yazın, FalımaBak tabir etsin', 'en': 'Describe your dream — FalımaBak interprets it', 'de': 'Traum beschreiben — FalımaBak deutet', 'fr': 'Décrivez votre rêve', 'es': 'Describe tu sueño', 'ar': 'صف حلمك', 'ru': 'Опишите свой сон', 'pt': 'Descreva seu sonho', 'it': 'Descrivi il tuo sogno', 'hi': 'अपना सपना लिखें', 'id': 'Ceritakan mimpimu', 'zh': '描述您的梦境'},
    'ruya_title': {'tr': 'Rüya Tabiri', 'en': 'Dream Interpretation', 'de': 'Traumdeutung', 'fr': 'Interprétation des rêves', 'es': 'Interpretación de sueños', 'ar': 'تفسير الأحلام', 'ru': 'Толкование снов', 'pt': 'Interpretação de sonhos', 'it': 'Interpretazione dei sogni', 'hi': 'सपने की व्याख्या', 'id': 'Tafsir Mimpi', 'zh': '解梦'},
    'ruya_aciklama': {'tr': 'Gördüğünüz rüyayı olabildiğince ayrıntılı yazın. FalımaBak sembolleri yorumlar.', 'en': 'Describe your dream in detail. FalımaBak interprets the symbols.', 'de': 'Beschreiben Sie Ihren Traum ausführlich. FalımaBak deutet die Symbole.', 'fr': 'Décrivez votre rêve en détail. FalımaBak interprète les symboles.', 'es': 'Describe tu sueño con detalle. FalımaBak interpreta los símbolos.', 'ar': 'صف حلمك بالتفصيل. FalımaBak يفسر الرموز.', 'ru': 'Опишите сон подробно. FalımaBak толкует символы.', 'pt': 'Descreva seu sonho. FalımaBak interpreta os símbolos.', 'it': 'Descrivi il sogno. FalımaBak interpreta i simboli.', 'hi': 'सपना विस्तार से लिखें। FalımaBak प्रतीकों की व्याख्या करता है।', 'id': 'Ceritakan mimpi Anda. FalımaBak menafsirkan simbol.', 'zh': '详细描述梦境。FalımaBak 解读符号。'},
    'ruya_input_label': {'tr': 'Rüyanız', 'en': 'Your dream', 'de': 'Ihr Traum', 'fr': 'Votre rêve', 'es': 'Tu sueño', 'ar': 'حلمك', 'ru': 'Ваш сон', 'pt': 'Seu sonho', 'it': 'Il tuo sogno', 'hi': 'आपका सपना', 'id': 'Mimpimu', 'zh': '您的梦'},
    'ruya_input_hint': {'tr': 'Örn: Deniz kenarında uçuyordum, sonra bir yılan gördüm…', 'en': 'E.g. I was flying by the sea, then saw a snake…', 'de': 'z.B. Ich flog am Meer…', 'fr': 'Ex. Je volais près de la mer…', 'es': 'Ej. Volaba junto al mar…', 'ar': 'مثال: كنت أطير…', 'ru': 'Напр. я летел над морем…', 'pt': 'Ex. Voava perto do mar…', 'it': 'Es. Volavo sul mare…', 'hi': 'जैसे समुद्र किनारे उड़ रहा था…', 'id': 'Contoh: Terbang di pantai…', 'zh': '例如：在海边飞翔…'},
    'ruya_hata_kisa': {'tr': 'Lütfen rüyanızı en az 15 karakter olacak şekilde yazın.', 'en': 'Please write at least 15 characters about your dream.', 'de': 'Mindestens 15 Zeichen.', 'fr': 'Au moins 15 caractères.', 'es': 'Al menos 15 caracteres.', 'ar': '15 حرفاً على الأقل.', 'ru': 'Минимум 15 символов.', 'pt': 'Pelo menos 15 caracteres.', 'it': 'Almeno 15 caratteri.', 'hi': 'कम से कम 15 अक्षर।', 'id': 'Minimal 15 karakter.', 'zh': '至少 15 个字符。'},
    'ruya_ozet_baslik': {'tr': 'Rüyanız', 'en': 'Your dream', 'de': 'Ihr Traum', 'fr': 'Votre rêve', 'es': 'Tu sueño', 'ar': 'حلمك', 'ru': 'Ваш сон', 'pt': 'Seu sonho', 'it': 'Il tuo sogno', 'hi': 'आपका सपना', 'id': 'Mimpimu', 'zh': '您的梦'},
    'ruya_yorumlaniyor': {'tr': 'FalımaBak yorumluyor…', 'en': 'FalımaBak is interpreting…', 'de': 'FalımaBak deutet…', 'fr': 'FalımaBak interprète…', 'es': 'FalımaBak interpreta…', 'ar': 'FalımaBak يفسر…', 'ru': 'FalımaBak толкует…', 'pt': 'FalımaBak interpreta…', 'it': 'FalımaBak interpreta…', 'hi': 'FalımaBak व्याख्या कर रहा है…', 'id': 'FalımaBak menafsirkan…', 'zh': 'FalımaBak 解读中…'},
    'burc_eslesme_title': {'tr': 'Burç Eşleşmesi', 'en': 'Zodiac Match', 'de': 'Sternzeichen-Match', 'fr': 'Compatibilité', 'es': 'Compatibilidad', 'ar': 'توافق الأبراج', 'ru': 'Совместимость', 'pt': 'Compatibilidade', 'it': 'Compatibilità', 'hi': 'राशि मिलान', 'id': 'Kecocokan Zodiak', 'zh': '星座配对'},
    'burc_eslesme_aciklama': {'tr': 'İki kişinin doğum tarihini girin; burçları ve uyumlarını FalımaBak yorumlasın.', 'en': 'Enter two birth dates for a compatibility reading.', 'de': 'Zwei Geburtsdaten eingeben.', 'fr': 'Entrez deux dates de naissance.', 'es': 'Introduce dos fechas de nacimiento.', 'ar': 'أدخل تاريخي الميلاد.', 'ru': 'Введите две даты рождения.', 'pt': 'Digite duas datas de nascimento.', 'it': 'Inserisci due date di nascita.', 'hi': 'दो जन्म तिथियाँ दर्ज करें।', 'id': 'Masukkan dua tanggal lahir.', 'zh': '输入两个出生日期。'},
    'burc_kisi1': {'tr': '1. Kişi', 'en': 'Person 1', 'de': 'Person 1', 'fr': 'Personne 1', 'es': 'Persona 1', 'ar': 'الشخص 1', 'ru': 'Человек 1', 'pt': 'Pessoa 1', 'it': 'Persona 1', 'hi': 'व्यक्ति 1', 'id': 'Orang 1', 'zh': '第1人'},
    'burc_kisi2': {'tr': '2. Kişi', 'en': 'Person 2', 'de': 'Person 2', 'fr': 'Personne 2', 'es': 'Persona 2', 'ar': 'الشخص 2', 'ru': 'Человек 2', 'pt': 'Pessoa 2', 'it': 'Persona 2', 'hi': 'व्यक्ति 2', 'id': 'Orang 2', 'zh': '第2人'},
    'burc_isim1': {'tr': 'İsim (isteğe bağlı)', 'en': 'Name (optional)', 'de': 'Name (optional)', 'fr': 'Nom (optionnel)', 'es': 'Nombre (opcional)', 'ar': 'الاسم (اختياري)', 'ru': 'Имя (необяз.)', 'pt': 'Nome (opcional)', 'it': 'Nome (opz.)', 'hi': 'नाम (वैक.)', 'id': 'Nama (opsional)', 'zh': '姓名（可选）'},
    'burc_isim2': {'tr': 'İsim (isteğe bağlı)', 'en': 'Name (optional)', 'de': 'Name (optional)', 'fr': 'Nom (optionnel)', 'es': 'Nombre (opcional)', 'ar': 'الاسم (اختياري)', 'ru': 'Имя (необяз.)', 'pt': 'Nome (opcional)', 'it': 'Nome (opz.)', 'hi': 'नाम (वैक.)', 'id': 'Nama (opsional)', 'zh': '姓名（可选）'},
    'burc_dogum_tarihi': {'tr': 'Doğum tarihi', 'en': 'Birth date', 'de': 'Geburtsdatum', 'fr': 'Date de naissance', 'es': 'Fecha de nacimiento', 'ar': 'تاريخ الميلاد', 'ru': 'Дата рождения', 'pt': 'Data de nascimento', 'it': 'Data di nascita', 'hi': 'जन्म तिथि', 'id': 'Tanggal lahir', 'zh': '出生日期'},
    'burc_gun': {'tr': 'Gün', 'en': 'Day', 'de': 'Tag', 'fr': 'Jour', 'es': 'Día', 'ar': 'يوم', 'ru': 'День', 'pt': 'Dia', 'it': 'Giorno', 'hi': 'दिन', 'id': 'Hari', 'zh': '日'},
    'burc_ay': {'tr': 'Ay', 'en': 'Month', 'de': 'Monat', 'fr': 'Mois', 'es': 'Mes', 'ar': 'شهر', 'ru': 'Месяц', 'pt': 'Mês', 'it': 'Mese', 'hi': 'महीना', 'id': 'Bulan', 'zh': '月'},
    'burc_yil': {'tr': 'Yıl', 'en': 'Year', 'de': 'Jahr', 'fr': 'Année', 'es': 'Año', 'ar': 'سنة', 'ru': 'Год', 'pt': 'Ano', 'it': 'Anno', 'hi': 'वर्ष', 'id': 'Tahun', 'zh': '年'},
    'burc_hata_bos': {'tr': 'Lütfen her iki kişi için gün, ay ve yıl girin.', 'en': 'Enter day, month and year for both people.', 'de': 'Bitte alle Datumsfelder ausfüllen.', 'fr': 'Remplissez toutes les dates.', 'es': 'Completa todas las fechas.', 'ar': 'أكمل جميع التواريخ.', 'ru': 'Заполните все поля дат.', 'pt': 'Preencha todas as datas.', 'it': 'Compila tutte le date.', 'hi': 'सभी तिथियाँ भरें।', 'id': 'Isi semua tanggal.', 'zh': '请填写全部日期。'},
    'burc_hata_sayi': {'tr': 'Tarih alanlarına sadece sayı girin.', 'en': 'Use numbers only in date fields.', 'de': 'Nur Zahlen eingeben.', 'fr': 'Chiffres uniquement.', 'es': 'Solo números.', 'ar': 'أرقام فقط.', 'ru': 'Только цифры.', 'pt': 'Apenas números.', 'it': 'Solo numeri.', 'hi': 'केवल संख्या।', 'id': 'Angka saja.', 'zh': '仅数字。'},
    'burc_hata_tarih': {'tr': 'Geçersiz doğum tarihi. Lütfen kontrol edin.', 'en': 'Invalid birth date.', 'de': 'Ungültiges Datum.', 'fr': 'Date invalide.', 'es': 'Fecha no válida.', 'ar': 'تاريخ غير صالح.', 'ru': 'Неверная дата.', 'pt': 'Data inválida.', 'it': 'Data non valida.', 'hi': 'अमान्य तिथि।', 'id': 'Tanggal tidak valid.', 'zh': '日期无效。'},
    'hello': {'tr': 'Merhaba, {name}!', 'en': 'Hello, {name}!', 'de': 'Hallo, {name}!', 'fr': 'Bonjour, {name}!', 'es': 'Hola, {name}!', 'ar': 'مرحباً {name}!', 'ru': 'Привет, {name}!', 'pt': 'Olá, {name}!', 'it': 'Ciao, {name}!', 'hi': 'नमस्ते, {name}!', 'id': 'Halo, {name}!', 'zh': '你好，{name}！'},
    'discover': {'tr': 'Geleceğinizi Keşfedin', 'en': 'Discover Your Future', 'de': 'Entdecken Sie Ihre Zukunft', 'fr': 'Découvrez votre avenir', 'es': 'Descubre tu futuro', 'ar': 'اكتشف مستقبلك', 'ru': 'Откройте будущее', 'pt': 'Descubra seu futuro', 'it': 'Scopri il futuro', 'hi': 'अपना भविष्य', 'id': 'Temukan masa depan', 'zh': '探索未来'},
    'loading': {'tr': 'Yükleniyor', 'en': 'Loading', 'de': 'Laden', 'fr': 'Chargement', 'es': 'Cargando', 'ar': 'جاري التحميل', 'ru': 'Загрузка', 'pt': 'Carregando', 'it': 'Caricamento', 'hi': 'लोड हो रहा', 'id': 'Memuat', 'zh': '加载中'},
    'loading_hint': {'tr': 'Lütfen bekleyin', 'en': 'Please wait', 'de': 'Bitte warten', 'fr': 'Veuillez patienter', 'es': 'Espere por favor', 'ar': 'يرجى الانتظار', 'ru': 'Подождите', 'pt': 'Aguarde', 'it': 'Attendere', 'hi': 'कृपया प्रतीक्षा करें', 'id': 'Harap tunggu', 'zh': '请稍候'},
    'history_title': {'tr': 'Fal Geçmişi', 'en': 'Reading History', 'de': 'Verlauf', 'fr': 'Historique', 'es': 'Historial', 'ar': 'السجل', 'ru': 'История', 'pt': 'Histórico', 'it': 'Cronologia', 'hi': 'इतिहास', 'id': 'Riwayat', 'zh': '历史'},
    'history_empty': {'tr': 'Henüz kayıtlı fal yok.\nBir fal baktır, burada görünsün.', 'en': 'No readings yet.\nGet a reading to see it here.', 'de': 'Noch keine Einträge.', 'fr': 'Aucune lecture.', 'es': 'Sin lecturas aún.', 'ar': 'لا قراءات بعد.', 'ru': 'Пока пусто.', 'pt': 'Sem leituras.', 'it': 'Nessuna lettura.', 'hi': 'अभी खाली.', 'id': 'Belum ada.', 'zh': '暂无记录。'},
    'daily_fal': {'tr': 'Günlük Fal', 'en': 'Daily Reading', 'de': 'Tagesorakel', 'fr': 'Oracle du jour', 'es': 'Lectura diaria', 'ar': 'قراءة اليوم', 'ru': 'На сегодня', 'pt': 'Leitura diária', 'it': 'Del giorno', 'hi': 'दैनिक', 'id': 'Harian', 'zh': '每日占卜'},
    'luck': {'tr': 'Şans', 'en': 'Luck', 'de': 'Glück', 'fr': 'Chance', 'es': 'Suerte', 'ar': 'حظ', 'ru': 'Удача', 'pt': 'Sorte', 'it': 'Fortuna', 'hi': 'भाग्य', 'id': 'Keberuntungan', 'zh': '幸运'},
    'cam_denied': {'tr': 'Kamera izni kapalı. Ayarlar > Uygulamalar > FalımaBak > İzinler', 'en': 'Camera permission denied. Enable in Settings > Apps > FalımaBak', 'de': 'Kamera verweigert.', 'fr': 'Caméra refusée.', 'es': 'Permiso denegado.', 'ar': 'تم رفض الكamera.', 'ru': 'Нет доступа к камере.', 'pt': 'Permissão negada.', 'it': 'Permesso negato.', 'hi': 'अनुमति नहीं.', 'id': 'Izin ditolak.', 'zh': '相机权限被拒绝。'},
    'cam_fail': {'tr': 'Kamera hatası. Tekrar deneyin.', 'en': 'Camera error. Try again.', 'de': 'Kamerafehler.', 'fr': 'Erreur caméra.', 'es': 'Error de cámara.', 'ar': 'خطأ في الكamera.', 'ru': 'Ошибка камеры.', 'pt': 'Erro na câmera.', 'it': 'Errore fotocamera.', 'hi': 'कैमरा त्रुटि.', 'id': 'Error kamera.', 'zh': '相机错误。'},
    'cam_no_app': {'tr': 'Kamera uygulaması bulunamadı', 'en': 'No camera app found', 'de': 'Keine Kamera-App', 'fr': 'Pas d\'appareil photo', 'es': 'Sin app de cámara', 'ar': 'لا تطبيق كamera', 'ru': 'Нет приложения', 'pt': 'Sem app', 'it': 'Nessuna app', 'hi': 'ऐप नहीं', 'id': 'Tidak ada app', 'zh': '无相机应用'},
    'cam_cancel': {'tr': 'Fotoğraf çekilmedi', 'en': 'Photo not taken', 'de': 'Kein Foto', 'fr': 'Photo annulée', 'es': 'Sin foto', 'ar': 'لم تُلتقط', 'ru': 'Не снято', 'pt': 'Não capturada', 'it': 'Non scattata', 'hi': 'नहीं ली', 'id': 'Tidak diambil', 'zh': '未拍摄'},
    'galeri_fail': {'tr': 'Galeri açılamadı. Tekrar deneyin veya kamerayı kullanın.', 'en': 'Gallery failed. Try again or use camera.', 'de': 'Galerie fehlgeschlagen.', 'fr': 'Galerie indisponible.', 'es': 'Galería no disponible.', 'ar': 'تعذر فتح المعرض.', 'ru': 'Галерея недоступна.', 'pt': 'Galeria indisponível.', 'it': 'Galleria non disponibile.', 'hi': 'गैलरी नहीं खुली.', 'id': 'Galeri gagal.', 'zh': '无法打开相册。'},
    'galeri_cancel': {'tr': 'Fotoğraf seçilmedi', 'en': 'No photo selected', 'de': 'Kein Foto gewählt', 'fr': 'Aucune photo', 'es': 'Sin foto', 'ar': 'لم يُختر صورة', 'ru': 'Фото не выбрано', 'pt': 'Nenhuma foto', 'it': 'Nessuna foto', 'hi': 'फ़ोटो नहीं चुनी', 'id': 'Tidak dipilih', 'zh': '未选择照片'},
    'foto_el_yok': {'tr': '{baslik} fotoğrafında el görünmüyor. Avuç içi veya el dışını net çekin.', 'en': 'No hand visible in {baslik}. Photograph your palm clearly.', 'de': 'Keine Hand in {baslik}.', 'fr': 'Pas de main visible.', 'es': 'No se ve la mano.', 'ar': 'اليد غير ظاهرة.', 'ru': 'Рука не видна.', 'pt': 'Mão não visível.', 'it': 'Mano non visibile.', 'hi': 'हाथ नहीं दिख रहा.', 'id': 'Tangan tidak terlihat.', 'zh': '未检测到手掌。'},
    'foto_kahve_yok': {'tr': '{baslik} fotoğrafında fincan ve telve birlikte net görünmüyor. Fincanı içten çekin; telvenin göründüğünden emin olun.', 'en': 'Cup and coffee grounds not clear together in {baslik}. Photograph inside the cup with visible grounds.', 'de': 'Tasse und Telves fehlen.', 'fr': 'Tasse et marc non visibles.', 'es': 'Taza y posos no visibles.', 'ar': 'الفنجان والتفل غير واضحين.', 'ru': 'Чашка и кофе не видны.', 'pt': 'Xícara e borra não visíveis.', 'it': 'Tazza e fondi non visibili.', 'hi': 'कप और तलवा साफ नहीं।', 'id': 'Cangkir dan ampas tidak jelas.', 'zh': '未同时检测到杯子和咖啡渣。'},
    'premium_tag': {'tr': 'Premium', 'en': 'Premium', 'de': 'Premium', 'fr': 'Premium', 'es': 'Premium', 'ar': 'Premium', 'ru': 'Premium', 'pt': 'Premium', 'it': 'Premium', 'hi': 'Premium', 'id': 'Premium', 'zh': 'Premium'},
}


def t(anahtar, **kwargs):
    lang = _dil_al()
    sozluk = _METINLER.get(anahtar, {})
    metin = sozluk.get(lang) or sozluk.get('en') or sozluk.get('tr') or anahtar
    if kwargs:
        try:
            metin = metin.format(**kwargs)
        except Exception:
            pass
    return metin


def dil_listesi():
    return list(DESTEKLENEN.items())


def dil_etiket(kod):
    return DESTEKLENEN.get(kod, kod)


def dil_degistir(kod):
    if kod in DESTEKLENEN:
        dil_kaydet(kod)
