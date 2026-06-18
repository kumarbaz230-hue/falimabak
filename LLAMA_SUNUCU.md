# Kendi Llama Sunucun — Kurulum Rehberi

FalımaBak, tarot / rüya / burç gibi **metin fallarında** önce sizin sunucunuzdaki Llama modelini dener. Kahve falı varsayılan olarak **sembol kütüphanesi** kullanır (API maliyeti yok); **AI Detaylı** butonu Gemini Vision ister.

Sunucuyu kurduktan sonra bana HTTPS adresinizi yazmanız yeterli — uygulamaya bağlantıyı ben tamamlarım.

---

## 1. Sunucu seçimi

| Seçenek | RAM | Aylık maliyet (yaklaşık) |
|---------|-----|--------------------------|
| Hetzner CX32 (4 vCPU, 8 GB) | 8 GB | ~€6 |
| Hetzner CX42 (8 vCPU, 16 GB) | 16 GB | ~€12 (daha rahat) |

Ubuntu 22.04 veya 24.04 LTS önerilir.

---

## 2. Ollama kurulumu

SSH ile sunucuya bağlanın:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1:8b
ollama serve
```

Test (sunucuda):

```bash
curl http://127.0.0.1:11434/api/generate -d '{
  "model": "llama3.1:8b",
  "prompt": "Merhaba, kısa bir fal yorumu yaz.",
  "stream": false
}'
```

---

## 3. HTTPS ile dışarı açma

Telefon uygulaması yalnızca **HTTPS** adresine bağlanır (localhost hariç).

### Seçenek A — Nginx + Let's Encrypt (klasik)

```bash
sudo apt install nginx certbot python3-certbot-nginx -y
```

`/etc/nginx/sites-available/ollama`:

```nginx
server {
    listen 443 ssl;
    server_name ai.sizindomain.com;

    ssl_certificate /etc/letsencrypt/live/ai.sizindomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ai.sizindomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:11434;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_read_timeout 300s;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/ollama /etc/nginx/sites-enabled/
sudo certbot --nginx -d ai.sizindomain.com
sudo nginx -t && sudo systemctl reload nginx
```

### Seçenek B — Cloudflare Tunnel (domain + firewall kolay)

1. [Cloudflare Zero Trust](https://one.dash.cloudflare.com/) → Tunnel oluştur
2. `localhost:11434` → `https://ai.sizindomain.com` yönlendir
3. Sunucuda port 443 açmanız gerekmez

---

## 4. Güvenlik (önemli)

Ollama varsayılan olarak kimlik doğrulaması yapmaz. En azından:

```bash
sudo ufw allow 22
sudo ufw allow 443
sudo ufw enable
```

İsteğe bağlı API anahtarı (Nginx `auth_request` veya basit Bearer header):

```nginx
# Örnek: sabit token
if ($http_authorization != "Bearer GIZLI_TOKEN_BURAYA") {
    return 401;
}
```

---

## 5. FalımaBak'a bağlama

Sunucu hazır olduktan sonra proje klasöründe `secrets.json`:

```json
{
  "ollama_sunucu_url": "https://ai.sizindomain.com",
  "ollama_api_key": "GIZLI_TOKEN_BURAYA"
}
```

Veya `config.json`:

```json
{
  "ollama_sunucu_url": "https://ai.sizindomain.com",
  "ollama_model": "llama3.1:8b",
  "ollama_api_key": ""
}
```

**Notlar:**
- URL'de `/api/generate` yazmayın; uygulama otomatik ekler.
- `ollama_sunucu_url` doluysa Android telefon da bu sunucuyu kullanır.
- Yerel PC testi için `ollama_url`: `http://127.0.0.1:11434/api/generate` yeterli.

---

## 6. Çalışma sırası (v1.7.0)

| Fal türü | Varsayılan | Yedek |
|----------|------------|-------|
| Kahve | Sembol kütüphanesi (ücretsiz) | AI Detaylı → Gemini Vision |
| Tarot, rüya, burç… | Llama sunucunuz | Groq → OpenRouter → xAI → Gemini → cihaz içi |

---

## 7. Sorun giderme

| Belirti | Çözüm |
|---------|--------|
| Telefon bağlanmıyor | URL `https://` ile başlamalı; sertifika geçerli olmalı |
| 401 hatası | `ollama_api_key` ile Nginx Bearer eşleşmeli |
| Çok yavaş | Daha küçük model: `llama3.2:3b` veya RAM artırın |
| Timeout | `config.json` → `"ai_timeout": 120` |

---

## Bana ne göndermelisiniz?

Sunucu kurulumunu bitirince şunları yazın:

1. HTTPS adresi (ör. `https://ai.sizindomain.com`)
2. Model adı (ör. `llama3.1:8b`)
3. API anahtarı varsa token

Ben `secrets.json` / build ayarlarını günceller, test eder ve gerekirse yeni APK sürümünü hazırlarım.
