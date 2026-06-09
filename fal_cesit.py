"""
FalımaBak — Fal yorum çeşitliliği (rastgele tohum + zengin paragraf havuzları).
"""

import random
import time


def rng_olustur(veri=None, foto_tohum=0):
    """Her fal bakışında farklı sonuç — zaman + rastgele + isteğe bağlı foto."""
    veri = veri or {}
    nonce = veri.get('_nonce')
    if nonce is None:
        nonce = (time.time_ns() % 2_000_000_000) + random.randint(0, 999_999)
    tohum = int(nonce) ^ int(foto_tohum or 0) ^ random.randint(0, 99999)
    return random.Random(tohum % 999_983)


def paragraf_sec(rng, havuz, adet=1):
    havuz = list(havuz)
    if not havuz:
        return []
    adet = min(adet, len(havuz))
    return rng.sample(havuz, adet)


def premium_uzun_mu(rng):
    """~%45 ihtimalle ekstra uzun premium yorum."""
    return rng.random() < 0.45


# --- Ortak premium paragraflar ---

ASK_UZUN = [
    'Kalp alanınızda yumuşama var; geçmişte susturduğunuz duygular konuşmak istiyor. '
    'Doğru kişiye küçük bir jest, ilişkinin ritmini güzelleştirebilir. Acele etmeden, '
    'samimiyetle ilerleyin.',
    'Aşk enerjiniz yükseliyor. Bekar iseniz tanışmalara açık olun; birlikte iseniz '
    'ortak bir plan yapmak bağınızı tazeleyecek. Kıskançlık yerine güveni seçin.',
    'Venüs etkisiyle romantizm ön planda. Mesaj atın, randevu planlayın, sevdiğinize '
    'zaman ayırın. Kalbinizin sesini dinlemek bu dönemde sizi doğru yönlendirir.',
    'Duygusal derinlik arayan bir dönemdesiniz. Yüzeysel ilişkilerden sıkılmış '
    'olabilirsiniz; bu normal. Gerçek bağ kurmak için kendinize de şefkat gösterin.',
    'Geçmişten gelen bir hatıra aklınıza düşebilir; kapıyı kapatmak zorunda değilsiniz '
    'ama yeniye yer açmak için hafifletmek iyi gelir. Yeni bir sayfa mümkün.',
    'İlişkilerde dürüstlük size şans getiriyor. Sakladığınız bir düşünceyi paylaşmak '
    'rahatlatıcı olabilir. Karşı tarafın da sizden beklediği şey netlik.',
]

KARIYER_UZUN = [
    'İş hayatında görünürlük artıyor. Yeteneğinizi göstermekten çekinmeyin; '
    'küçük bir sunum bile kapı aralayabilir. Disiplin ve yaratıcılık bir arada.',
    'Maddi konularda planlı adımlar öne çıkıyor. Harcamaları gözden geçirmek ve '
    'küçük birikimler yapmak uzun vadede rahatlatır. Fırsat kapıda — hazırlıklı olun.',
    'Kariyerinde yeni bir beceri edinmek veya kursa yazılmak yıldızlarınızı parlatır. '
    'Emek verdiğiniz alan karşılık bulmaya başlıyor; sabır sürdürün.',
    'Ortaklık veya ekip çalışması gündeme gelebilir. İletişiminiz güçlüyse anlaşma '
    'kolaylaşır. Tek başına ilerlemek istiyorsanız sınırlarınızı net çizin.',
    'Terfi, zam veya yeni teklif ihtimali var. Kendinizi satmakta utangaç olmayın; '
    'başarılarınızı görünür kılın. Ofis içi söylentilere kapılmayın, işinize odaklanın.',
]

SAGLIK_UZUN = [
    'Bedeniniz dinlenme ve düzenli uyku istiyor. Su tüketimini artırmak ve hafif '
    'yürüyüşler enerjinizi toparlar. Stresi azaltmak için nefes egzersizi deneyin.',
    'Sağlık açısından dengeli bir dönem; aşırıya kaçmadan spor ve beslenmeye '
    'dikkat edin. Baş ağrısı veya yorgunluk uyarı ise molayı ertelemeyin.',
    'Ruhsal sağlık fiziksel sağlık kadar önemli. Sevdiğiniz bir müziği açın, '
    'doğada kısa bir mola verin. Zihniniz ferahlayınca kararlar netleşir.',
]

GENEL_UZUN = [
    'Evren sizin lehinize dönüyor; küçük sürprizler moralinizi yükseltecek. '
    'Olumsuz düşünceleri zorla kovmak yerine, yapabileceğiniz bir iyiliğe odaklanın.',
    'Sezgileriniz güçlü — iç sesinize kulak verin. Bir davetiye veya teklif '
    'gelse değerlendirin; reddetmek de kabul etmek kadar bilinçli olabilir.',
    'Bu dönemde sabır ve nezaket size kapı açar. Tartışmalardan uzak durun, '
    'niyetinizi net tutun. Sonuçlar beklediğinizden daha yapıcı olabilir.',
    'Yeni bir hobi veya kısa bir seyahat ruhunuza iyi gelecek. Rutinden çıkmak '
    'yaratıcılığınızı tetikler; fırsatları küçük adımlarla değerlendirin.',
    'Aile ve dost çevreniz destek kaynağınız. Yardım istemekten çekinmeyin; '
    'verdiğiniz sevgi de size geri dönecek.',
]

KAPANIS_CUMLE = [
    'Falınız eğlence amaçlıdır; kalbinizin sesini her zaman dinleyin.',
    'Yıldızlar yol gösterir, yürüyen sizsiniz — güzel günler dileriz.',
    'Pozitif enerjinizi koruyun; nazar boncuğunuz sizi korusun.',
    'Umutla ilerleyin; en güzel hikâye henüz yazılıyor.',
]

# --- İskambil ---

ISKAMBIL_BAGLANTI = [
    'Üç kart birlikte okunduğunda geçmişten gelen bir ders, bugünkü kararınızı '
    'şekillendiriyor; gelecek kartı ise sabır ve net niyetle açılacak bir kapıyı işaret ediyor.',
    'Geçmiş kartınız tamamlanan bir döngüyü, şimdiki kart mevcut enerjinizi, '
    'gelecek kart ise birkaç hafta içinde netleşecek bir gelişmeyi anlatıyor.',
    'Kartlarınız bir hikâye anlatıyor: geçmişte öğrenilen, şimdi uygulanan ve '
    'yakında müjdelenecek üç aşamalı bir yolculuk.',
]

ISKAMBIL_TAVSIYE = [
    'Kalbinizin sesini dinleyin ama önemli kararları bir gece uyuyup düşünerek alın.',
    'Mantık ve sezgi bir arada en iyi sonucu verir; aceleci mesajlar göndermeyin.',
    'Güvendiğiniz bir dostla konuşmak fikirlerinizi netleştirir.',
    'Cesaret gösterin ama riskleri hesaplayın; küçük adımlar büyük kapılar açar.',
    'Geçmişi fazla kurcalamayın; bugün atacağınız adım geleceği değiştirir.',
    'Paylaşmak güzelleştirir — sevdiklerinizle kaliteli vakit geçirin.',
    'Kendinize yatırım yapın: kitap, kurs veya kısa bir dinlenme tatili.',
    'Sabırlı olun; kartlar zamanın sizin lehinize işlediğini söylüyor.',
]

# --- Çiçek ---

CICEK_BUKET = [
    'Seçilen çiçekler bir buket gibi okunuyor: renkler ve kokular hayatınızdaki '
    'farklı alanların aynı anda çiçek açtığını müjdeliyor.',
    'Çiçek diline göre doğa size nazik bir mesaj gönderiyor; acele etmeden '
    'bu mesajın kök salmasına izin verin.',
    'Her çiçek farklı bir duyguyu temsil ediyor; birlikte okunduklarında '
    'bütünsel bir dönüşüm hikâyesi ortaya çıkıyor.',
]

CICEK_OZEL = [
    'Evde taze çiçek bulundurmak enerjinizi yükseltir.',
    'Doğada yürüyüş yapmak bu falın mesajını güçlendirir.',
    'Sevdiklerinize küçük bir çiçek jesti ilişkilerinizi tazeler.',
    'Saksı bitkisi bakmak sabır ve bereket enerjisi getirir.',
]

# --- Nazar ---

NAZAR_DURUM = [
    'Nazar boncuğunuz sağlam ve sizi koruyor; enerji kalkanı aktif.',
    'Boncuğunuzda hafif matlık var — negatif enerji emilmiş olabilir, güneşte dinlendirin.',
    'Boncuk parlak görünüyor; moraliniz ve çevrenizdeki olumlu akış güçlü.',
    'Yeni bir boncuk takmanız veya evde mavi nazar bulundurmanız önerilir.',
    'Boncuk çatlamışsa sizi büyük bir nazardan koruduğunu düşünün; minnetle yenileyin.',
]

NAZAR_UZUN = [
    'Nazar enerjisi görünmez ama hissedilir. Başarılarınız arttıkça çevrenizdeki '
    'kıskanç bakışlara karşı bilinçli olun; kendinizi küçümsemeyin, paylaşımı dengeleyin.',
    'Mavi renk ve nazar sembolü sizin için koruyucu. Önemli günlerde boncuğunuzu '
    'yanınızda taşıyın; olumlu niyetiniz kalkanınız olsun.',
    'İç huzurunuz en güçlü nazar korumasıdır. Meditasyon, dua veya sadece derin '
    'nefes ile enerjinizi tazeleyin; dış etkiler zayıflar.',
    'Bu hafta nazara karşı biraz daha dikkatli olun; yeni başlangıçlarınızı '
    'herkese anlatmak zorunda değilsiniz. Sevdikleriniz yeter.',
]

NAZAR_KORUNMA = [
    'Mavi tonlu kıyafet veya aksesuar kullanın.',
    'Ev girişine nazar boncuğu asın.',
    'Tuz ritüeli: bir tutam tuzu omuz üzerinden atıp arkanıza bakmadan devam edin.',
    'Nane veya limon kokusu odayı ferahlatır.',
    'Olumlu affirmasyonlar tekrarlayın: “Korunuyorum, huzurluyum.”',
    'Üzerlik otu yakmak geleneksel bir temizlik yöntemidir.',
    'Su içerken niyet edin; bedeniniz arınmış olsun.',
    'Kıskançlık uyandıran ortamlardan uzak durun.',
]

# --- Tarot ek ---

TAROT_GIRIS = [
    'Kartlarınız bir araya geldiğinde güçlü bir hikâye ortaya çıkıyor. Her kart '
    'tek başına bir mesaj taşır; birlikte okunduklarında hayatınızdaki akış netleşir.',
    'Tarot size ayna tutuyor: geçmişten gelen izler, bugünkü gücünüz ve yarının '
    'potansiyeli aynı masada buluşuyor.',
    'Çekilen kartlar tesadüf değil; o anki enerjinizle rezonansa girmiş semboller bunlar.',
]

TAROT_KART_EK = [
    'Bu kartın enerjisi birkaç hafta boyunca etkisini sürdürebilir.',
    'Kart mesajını günlük hayata taşımak için küçük bir adım atın.',
    'Ters gelmişse içsel bir direnç veya gecikme vardır; sabır gösterin.',
    'Düz konumda kartın gücü rahatlıkla akıyor; fırsatı kaçırmayın.',
]

# --- Astroloji ek ---

ELEMENT_YORUM = {
    'Ateş': 'Ateş elementiniz cesaret ve hareketi destekliyor. İçten gelen tutku '
            'projelerinize can verecek; öfkeyi yapıcı kanala yönlendirin.',
    'Toprak': 'Toprak elementi istikrar ve pratiklik getiriyor. Somut planlar '
              'yapmak, bütçe düzenlemek ve sabırlı olmak size kazandırır.',
    'Hava': 'Hava elementi iletişim ve fikirlerin ön planda. Yazmak, konuşmak, '
            'öğrenmek ve sosyalleşmek yıldızlarınızı parlatır.',
    'Su': 'Su elementi duygu ve sezgiyi güçlendiriyor. Sanat, müzik veya su '
          'kenarında vakit geçirmek ruhunuzu besler.',
}
