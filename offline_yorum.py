"""
FalımaBak — Cihaz içi premium fal yorumu (API / internet gerekmez).
Fotoğraf analizi + zengin Türkçe şablonlar ile derin yorumlar üretir.
"""

import random
import textwrap


def _temiz(metin):
    try:
        from theme import emoji_temizle
        return emoji_temizle(metin or '')
    except Exception:
        return metin or ''


def _hitap():
    try:
        from gecmis import kullanici_ismi
        isim = (kullanici_ismi() or '').strip()
        if isim:
            return f'{isim}, '
    except Exception:
        pass
    return ''


def _paragraf(metin, genislik=72):
    return textwrap.fill(metin, width=genislik)


def _el_veri():
    import elfali
    return elfali.EL_CIZGILERI, elfali.EL_TIPLERI


def _kahve_veri():
    import kahve
    return kahve.KAHVE_SEKILLERI, kahve.GENEL_YORUMLAR


def _foto_gozlem_elfali(ozellikler, aciklamalar):
    if not ozellikler:
        return ''
    satirlar = []
    for i, oz in enumerate(ozellikler):
        if not oz:
            continue
        baslik = aciklamalar[i] if aciklamalar and i < len(aciklamalar) else f'Fotoğraf {i + 1}'
        ten = oz.get('ten_orani', 0)
        kontrast = oz.get('kontrast', 0)
        if 'avuç' in baslik.lower() or 'içi' in baslik.lower():
            if ten > 0.35 and kontrast > 18:
                satirlar.append(
                    f'{baslik}: Çizgiler belirgin ve avuç yapısı net okunuyor; '
                    'karakter ve kader hattı güçlü bir enerji taşıyor.'
                )
            elif ten > 0.2:
                satirlar.append(
                    f'{baslik}: Avuç içi yumuşak ve dengeli; duygusal derinlik '
                    'ile pratik zekâ bir arada.'
                )
            else:
                satirlar.append(
                    f'{baslik}: Avuç hatları incelikli; sezgi ve içgörü ön planda.'
                )
        else:
            if kontrast > 15:
                satirlar.append(
                    f'{baslik}: El formu güçlü; dış görünüş cesaret ve '
                    'kararlılıkla uyumlu.'
                )
            else:
                satirlar.append(
                    f'{baslik}: El dışı yapısı zarif; sanatsal ve sosyal '
                    'yeteneklere işaret ediyor.'
                )
    return '\n'.join(satirlar)


def _foto_gozlem_kahve(ozellikler, aciklamalar):
    if not ozellikler:
        return ''
    satirlar = []
    for i, oz in enumerate(ozellikler):
        if not oz:
            continue
        baslik = aciklamalar[i] if aciklamalar and i < len(aciklamalar) else f'Fotoğraf {i + 1}'
        kahve = oz.get('kahve_orani', 0)
        koyu = oz.get('koyu_orani', 0)
        if 'tabak' in baslik.lower():
            satirlar.append(
                f'{baslik}: Tabaktaki izler yolculuk ve haber enerjisi taşıyor; '
                'yakın çevreden güzel gelişmeler müjdeleniyor.'
            )
        elif kahve > 0.15 or koyu > 0.25:
            satirlar.append(
                f'{baslik}: Telve desenleri yoğun; fincan güçlü semboller barındırıyor '
                've dönüşüm dönemi işaret ediyor.'
            )
        else:
            satirlar.append(
                f'{baslik}: Telveler ince ama anlamlı; sabır ve doğru zamanlama '
                'mesajı öne çıkıyor.'
            )
    return '\n'.join(satirlar)


def _elfali_yorum(veri, ozellikler=None):
    cizgiler_db, tipler = _el_veri()
    hitap = _hitap()
    rng = random.Random()
    tohum = veri.get('_tohum')
    if tohum is not None:
        rng.seed(tohum)

    el_tipi = rng.choice(tipler)
    secilen = rng.sample(cizgiler_db, min(rng.randint(5, 7), len(cizgiler_db)))
    aciklamalar = veri.get('foto_aciklamalari') or []

    bolum = []
    bolum.append('EL FALI YORUMUNUZ')
    bolum.append('')
    bolum.append(f'El tipiniz: {_temiz(el_tipi["tip"])}')
    bolum.append(el_tipi['ozellik'])
    bolum.append(
        f'Karakter: {el_tipi["karakter"]}. Bu tip genelde {el_tipi["meslek"]} '
        'alanlarında parlar.'
    )
    bolum.append('')

    gozlem = _foto_gozlem_elfali(ozellikler, aciklamalar)
    if gozlem:
        bolum.append('Fotoğraf gözlemleri:')
        bolum.append(gozlem)
        bolum.append('')

    bolum.append('Çizgi analizi:')
    for c in secilen:
        durum = rng.choice(['Pozitif', 'Güçlü', 'Belirgin'])
        yorum = c['pozitif'] if durum != 'Negatif' else c.get('negatif', c['pozitif'])
        bolum.append(f'• {_temiz(c["isim"])} ({durum}): {_temiz(yorum)}')

    bolum.append('')
    bolum.append('Aşk ve ilişkiler:')
    bolum.append(_paragraf(rng.choice([
        f'{hitap}kalp çizginiz duygusal zenginliğinizi ve bağ kurma gücünüzü vurguluyor. '
        'Yakın dönemde samimi bir sohbet ilişkinizi derinleştirebilir; açık iletişim size '
        'çok yakışıyor.',
        f'{hitap}avuç haritanız sevgiye açık bir dönemi işaret ediyor. Tek başınıza '
        'değilsiniz; doğru kişiyle kurduğunuz güven, kalıcı mutluluğun temeli olacak.',
        f'{hitap}duygusal dengeniz yükseliyor. Geçmişte yaşanan küçük kırgınlıklar '
        'geride kalıyor; kalbinizi ferah tuttuğunuzda güzel sürprizler kapıda.',
    ])))

    bolum.append('')
    bolum.append('Kariyer ve para:')
    bolum.append(_paragraf(rng.choice([
        f'{hitap}kader çizginizdeki netlik, iş hayatında yeni bir fırsat veya '
        'sorumluluk almanızı müjdeliyor. Yeteneklerinizi göstermekten çekinmeyin.',
        f'{hitap}para çizgisi ve bilek hatlarınız maddi istikrar arayışınızı '
        'destekliyor. Planlı adımlar ve sabır, beklediğiniz rahatlamayı getirecek.',
        f'{hitap}el yapınız girişimcilik ve yaratıcı çözüm enerjisi taşıyor. '
        'Küçük bir risk, uzun vadede büyük kazanç kapısı aralayabilir.',
    ])))

    bolum.append('')
    bolum.append('Sağlık ve enerji:')
    bolum.append(_paragraf(rng.choice([
        f'{hitap}hayat çizginiz dayanıklılığınızı gösteriyor. Dinlenme, su ve hafif '
        'egzersiz bu dönemde enerjinizi zirveye taşır.',
        f'{hitap}genel el enerjiniz canlı; stres yönetimi ile birlikte zihinsel '
        'berraklığınız artacak. Kendinize ayıracağınız kısa molalar çok işe yarar.',
    ])))

    bolum.append('')
    bolum.append('Genel mesaj:')
    bolum.append(_paragraf(rng.choice([
        f'{hitap}elleriniz değişim ve büyüme dönemine işaret ediyor. Sezgilerinize '
        'güvenin; attığınız her adım sizi daha otantik bir hayata taşıyor.',
        f'{hitap}avuç çizgileriniz umut, cesaret ve içsel güç taşıyor. '
        'Olumlu kalmaya devam edin — evren sizin lehinize dönüyor.',
    ])))
    bolum.append('')
    bolum.append(f'Şanslı sayınız: {rng.randint(1, 99)}')

    return '\n'.join(bolum)


def _kahve_yorum(veri, ozellikler=None):
    sekiller_db, genel_db = _kahve_veri()
    hitap = _hitap()
    rng = random.Random()
    tohum = veri.get('_tohum')
    if tohum is not None:
        rng.seed(tohum + 17)

    adet = rng.randint(4, 6)
    secilen = rng.sample(sekiller_db, min(adet, len(sekiller_db)))
    aciklamalar = veri.get('foto_aciklamalari') or []

    kategoriler = {}
    for s in secilen:
        kategoriler.setdefault(s['kategori'], []).append(s)

    bolum = []
    bolum.append('KAHVE FALI YORUMUNUZ')
    bolum.append('')

    gozlem = _foto_gozlem_kahve(ozellikler, aciklamalar)
    if gozlem:
        bolum.append('Fincan gözlemleri:')
        bolum.append(gozlem)
        bolum.append('')

    bolum.append('Fincanda öne çıkan semboller:')
    for kat, liste in kategoriler.items():
        bolum.append(f'\n{kat}:')
        for s in liste:
            durum = rng.choice(['Pozitif', 'Güçlü'])
            y = s['pozitif'] if durum == 'Pozitif' else s.get('negatif', s['pozitif'])
            bolum.append(f'  • {_temiz(s["isim"])}: {_temiz(y)}')

    bolum.append('')
    bolum.append('Aşk:')
    bolum.append(_paragraf(rng.choice([
        f'{hitap}fincanınızda kalp ve bağ sembolleri öne çıkıyor. Duygusal '
        'açıklık size yakın bir ilişkide derinlik getirecek.',
        f'{hitap}telveler aşk hayatında hareketliliği işaret ediyor. Beklemediğiniz '
        'bir mesaj veya buluşma moralinizi yükseltebilir.',
    ])))

    bolum.append('')
    bolum.append('Para ve iş:')
    bolum.append(_paragraf(rng.choice([
        f'{hitap}bolluk sembolleri fincanın alt yarısında belirgin. Küçük yatırımlar '
        'veya ek gelir fikirleri değerlendirmeye değer.',
        f'{hitap}kariyer çizgileri yükseliş enerjisi taşıyor. Emeklerinizin karşılığını '
        'almaya başlayacağınız bir döneme giriyorsunuz.',
    ])))

    bolum.append('')
    bolum.append('Sağlık:')
    bolum.append(_paragraf(rng.choice([
        f'{hitap}genel enerji dengeli; dinlenme ve düzenli beslenme ile '
        'formunuzu koruyacaksınız.',
        f'{hitap}fincan sağlık açısından olumlu; stresi azaltmak için doğada '
        'vakit geçirmek size iyi gelecek.',
    ])))

    bolum.append('')
    bolum.append('Genel yorum:')
    bolum.append(_paragraf(_temiz(rng.choice(genel_db))))

    bolum.append('')
    bolum.append(f'Şanslı sayınız: {rng.randint(1, 99)}')
    return '\n'.join(bolum)


def _tarot_yorum(veri):
    hitap = _hitap()
    kartlar = veri.get('kartlar') or []
    rng = random.Random(len(kartlar) * 31 + hash(hitap) % 1000)

    bolum = ['TAROT YORUMUNUZ', '']
    if kartlar:
        bolum.append('Çekilen kartlar:')
        for k in kartlar:
            bolum.append(
                f'• {k.get("pozisyon", "")}: {k.get("isim", "")} '
                f'({k.get("durum", "")}) — {k.get("anlam", "")}'
            )
        bolum.append('')

    bolum.append(_paragraf(rng.choice([
        f'{hitap}kartlarınız dönüşüm ve yenilenme döngüsünü işaret ediyor. '
        'Geçmiş deneyimleriniz bugünkü kararlarınıza güç katıyor.',
        f'{hitap}seçilen kartlar umut, denge ve içsel güç temalarını taşıyor. '
        'Yakın zamanda moralinizi yükseltecek gelişmeler olabilir.',
    ])))
    bolum.append('')
    bolum.append('Aşk:')
    bolum.append(_paragraf(
        f'{hitap}kalp enerjiniz açılıyor. Dürüst iletişim ilişkilerinizde '
        'kapıları aralayacak; sabırlı olun.'
    ))
    bolum.append('')
    bolum.append('Kariyer:')
    bolum.append(_paragraf(
        f'{hitap}iş ve projelerde netlik kazanıyorsunuz. Küçük adımlar '
        'büyük sonuçlara dönüşebilir.'
    ))
    return '\n'.join(bolum)


def _astroloji_yorum(veri):
    hitap = _hitap()
    burc = veri.get('burc', 'yıldızlar')
    return '\n'.join([
        'ASTROLOJİ YORUMUNUZ',
        '',
        _paragraf(
            f'{hitap}{burc} burcu için enerji yükseliyor. Aşk hayatında '
            'sıcaklık, işte ise istikrar ön planda. Sağlığınıza özen '
            'gösterdiğinizde şans sizinle olacak.'
        ),
        '',
        _paragraf(
            'Yıldızlar cesaret ve denge istiyor; sezgilerinize kulak verin '
            've aceleci kararlardan kaçının.'
        ),
    ])


def _diger_yorum(veri):
    hitap = _hitap()
    tur = veri.get('tur', 'Fal')
    sonuc = veri.get('sonuc', '')
    return '\n'.join([
        f'{tur.upper()} YORUMUNUZ',
        '',
        _paragraf(f'{hitap}{sonuc}'),
        '',
        _paragraf(
            'Evren size güzel haberler hazırlıyor. Pozitif kalın ve '
            'fırsatları değerlendirin.'
        ),
    ])


def offline_yorum_uret(tip, veri, foto_ozellikleri=None):
    """API'siz premium fal metni."""
    veri = dict(veri or {})
    if foto_ozellikleri is not None:
        from foto_analiz import foto_tohum
        veri['_tohum'] = foto_tohum(foto_ozellikleri)

    if tip == 'elfali':
        return _elfali_yorum(veri, foto_ozellikleri)
    if tip == 'kahve':
        return _kahve_yorum(veri, foto_ozellikleri)
    if tip == 'tarot':
        return _tarot_yorum(veri)
    if tip == 'astroloji':
        return _astroloji_yorum(veri)
    if tip == 'diger':
        return _diger_yorum(veri)
    return _diger_yorum({'tur': tip, 'sonuc': ''})
