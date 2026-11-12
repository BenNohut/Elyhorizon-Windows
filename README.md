# Elyhorizon Windows Edition

Elyhorizon Windows Edition, [Elyhorizon](https://github.com/Tsifrokayf/Elyhorizon) projesinin Windows x64 için hazırlanmış, taşınabilir bir dağıtım ve uyarlama çalışmasıdır. Temel hedef, mevcut Elyhorizon/Horizon tabanını Windows üzerinde çalıştırılabilir bir paket halinde sunmak ve Windows'a özgü başlatıcı/çalıştırma ihtiyaçlarına uygun hale getirmektir.

> Bu proje Minecraft, Mojang, Microsoft veya Ely.by ile resmî olarak bağlantılı değildir, onlar tarafından onaylanmamıştır ve onlar adına geliştirilmemiştir.

## Upstream projeler ve krediler

- **Orijinal Horizon projesi ve katkıcıları:** Horizon projesinin özgün çalışması ve katkıda bulunanlar (bkz. [horizon-rust/horizon](https://github.com/horizon-rust/horizon)).
- **Elyhorizon upstream projesi:** [Tsifrokayf/Elyhorizon](https://github.com/Tsifrokayf/Elyhorizon) tarafından yayımlanan Elyhorizon çalışması.
- **Bu depo / Windows uyarlaması:** Windows uyarlaması, Windows entegrasyonu ve taşınabilir dağıtım hazırlığı: **BenNohut**.

Bu depo, BenNohut'u orijinal Horizon veya Elyhorizon kod tabanının yazarı ya da Ely.by OAuth sisteminin yazarı olarak göstermez. Upstream projelere ve katkıcılarına ait kredi ve sorumluluklar ilgili projelerde kalır.

## Neler sunar?

- **Windows x64 odaklı çalışma:** Windows x64 ortamı için hazırlanmış başlatıcı ve paket düzeni.
- **Taşınabilir dağıtım mantığı:** Paket klasörü içinden çalıştırılacak şekilde tasarlanmış yapı; uygun koşullarda başlatıcı/veri dizinlerini paket yanına yerleştirmeyi hedefler (aşağıdaki sınırlamalara bakın).
- **Ely.by ile giriş desteği:** Mevcut hazırlanmış dağıtım paketinde Ely.by hesabı ile giriş akışı bulunur. Bu davranış, mevcut dağıtım/çalışma bağlamına bağlıdır; yeniden derleme veya farklı CI/derleme ortamlarında aynı yapılandırmanın otomatik olarak garanti edildiği iddia edilmez.
- **Minecraft 26.3 hedefi:** Proje, Minecraft: Java Edition 26.3 ile uyumlu hazırlanmış bileşenler ve kaynak hazırlama akışını temel alır.

## Sistem gereksinimleri

- Windows x64
- Uygun bir ekran kartı/sürücü (projenin grafik altyapısı için gereklidir)
- Minecraft: Java Edition 26.3 dosyalarına sahip olmak (bkz. aşağıda)
- İlk hazırlık/çalıştırma senaryolarına bağlı olarak Java çalışma zamanı gerekebilir

## Kurulum ve çalıştırma (dağıtım paketi)

1. Windows x64 için hazırlanmış dağıtım paketini indirin ve bir klasöre çıkarın.
2. Paketi çıkarılan klasörden çalıştırın (taşınabilir kullanım için paket bütünlüğünü koruyun).
3. Başlatıcıyı (`horizon-launcher.exe` veya paketle birlikte verilen çalıştırma dosyası) başlatın.
4. Ely.by hesabınızla giriş yapabilir ve yönergeleri izleyebilirsiniz.

> **Önemli:** Minecraft: Java Edition 26.3 oyun dosyaları bu depoda/pakette sağlanmaz ve dağıtılmaz. Kullanıcının, yasal olarak sahip olduğu kendi Minecraft 26.3 kopyasından gerekli dosyaları sağlaması gerekir. Horizon/Elyhorizon, Minecraft kodunu, varlıklarını veya verilerini içermez.

## Minecraft 26.3 dosyalarını sağlama

Hazırlama ve çalıştırma adımları, kullanıcının kendi Minecraft: Java Edition 26.3 kurulumuna ait dosyalara dayanır. Gerekli istemci/sunucu/varlık dosyalarının temini ve kullanımı kullanıcının sorumluluğundadır. Dosyaları nasıl elde edeceğiniz ve hangi yolların kullanılacağı, sahip olduğunuz yasal kopya ve kurulum düzeninize bağlıdır; bu README gizli anahtar, istemci kimliği (Client ID), token veya benzeri yapılandırma değerleri içermez.

## Taşınabilir paket mantığı

Paketlenmiş çalıştırmada başlatıcı, uygun durumlarda paket klasörü yanındaki dizinleri (ör. başlatıcı verisi ve oyun verisi) kullanmayı hedefler. Mevcut ortam değişkenleri varsa bunlar korunur. Paket klasörü yazılabilir değilse, veri konumları için alternatif/fallback davranışlar uygulanabilir. Taşınabilirlik; dosya izinleri, antivirus kısıtlamaları, yol uzunlukları ve kullanıcı ortamı gibi etkenlerden etkilenebilir.

## Bilinen sınırlamalar

- **Ely.by ve derleme yapılandırması:** Ely.by girişi, mevcut dağıtım paketinde çalışacak şekilde hazırlanmıştır; ancak yeniden derleme veya CI ortamlarında gerekli yapılandırmanın mevcut/aynı olacağı garanti edilmez.
- **Lisans/üçüncü taraf durumu:** Üçüncü taraf bileşenler ve lisans bildirimleri için [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) dosyasına bakın. Bağımlılıkların, gömülü bileşenlerin veya türetilmiş içeriklerin tamamının lisans/provenance açısından eksiksiz ve nihai olarak çözümlendiği bu belgede iddia edilmez.
- **Minecraft lisans/EULA:** Minecraft kullanımı ve dosyaları Mojang/Microsoft tarafından belirlenen lisans ve kullanım koşullarına tabidir. Gerekli uyumluluğun değerlendirilmesi kullanıcıya ve dağıtım bağlamına bağlıdır.
- **Çalışma zamanı doğrulaması:** Farklı sistemlerde başlatma, giriş, oyun başlatma/hazırlama ve ağ koşullarına bağlı davranışlar değişebilir. Belirli bir ortamda gözlemlenen sonuçlar tüm kurulumlar için garanti değildir.

## Kaynaktan geliştirme notu

Bu depo, upstream Horizon/Elyhorizon kaynak yapısını ve araçlarını içerir. Kaynaktan derleme, hazırlama ve doğrulama adımları; Rust toolchain, JDK, platform araçları ve kullanıcının sağladığı Minecraft 26.3 dosyaları gibi ek gereksinimlere bağlıdır. Genel upstream geliştirme akışı için [CONTRIBUTING.md](CONTRIBUTING.md) dosyasına bakabilirsiniz; bu dosyadaki süreçler upstream proje akışını yansıtabilir ve Windows Edition dağıtımıyla birebir aynı olmayabilir.

## Katkı

Katkılar ve geri bildirimler değerlidir. Katkı süreci ve beklentiler için [CONTRIBUTING.md](CONTRIBUTING.md) dosyasına bakın. Upstream projelerin kendi katkı kuralları ve yol haritaları ayrıca geçerlidir.

## Lisans

Bu projenin özgün çalışmalarına ilişkin lisans bilgisi için [LICENSE](LICENSE) dosyasına bakın. Bağımlılıklar ve üçüncü taraf bileşenler kendi lisanslarını korur; ayrıntılar ve bildirimler için [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) dosyasını inceleyin.
