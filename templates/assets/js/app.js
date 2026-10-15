const qs = (sel, scope = document) => scope.querySelector(sel);
const qsa = (sel, scope = document) => [...scope.querySelectorAll(sel)];

document.addEventListener("DOMContentLoaded", () => {
    const productContainer = document.getElementById("product-list-container");

    // Agar hozirgi sahifada mahsulotlar konteyneri bo'lmasa, funksiya ishlamaydi
    if (!productContainer) return;

    // API manzili: backend (Django REST Framework) mahsulotlarni GET /product/ orqali qaytaradi
    const API_URL = "https://birzumdadrf.onrender.com/product/";
    // Render'dagi server uyqudan uyg'onishi uchun ko'proq vaqt kerak bo'lishi mumkin
    const REQUEST_TIMEOUT_MS = 60000;
    const pagination = qs(".product-pagination");

    // API'dan kelgan matnni HTML'ga xavfsiz qo'yish uchun
    const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (ch) => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    }[ch]));

    // Narxni mavjud dizayndagidek ko'rsatish: 12 999 000 so'm
    const formatPrice = (value) => {
        const number = Number(value);
        if (value === null || value === "" || !Number.isFinite(number)) return "Narx ko'rsatilmagan";
        return `${String(Math.round(number)).replace(/\B(?=(\d{3})+(?!\d))/g, " ")} so'm`;
    };

    // Reytingni yulduzchalar ko'rinishida chiqarish (0-5)
    const buildStars = (value) => {
        const rating = Math.min(5, Math.max(0, Number(value) || 0));
        const full = Math.floor(rating);
        const half = rating - full >= 0.5 ? 1 : 0;
        return Array.from({ length: 5 }, (_, i) => {
            if (i < full) return '<i class="fa-solid fa-star"></i>';
            if (i < full + half) return '<i class="fa-solid fa-star-half-stroke"></i>';
            return '<i class="fa-regular fa-star"></i>';
        }).join("");
    };

    // API faqat toifa ID'sini beradi; agar nom kelsa, o'shani ishlatamiz
    const getCategoryLabel = (category) => {
        if (category && typeof category === "object") return category.name || category.title || "";
        if (typeof category === "string" && category.trim()) return category.trim();
        if (Number.isFinite(Number(category)) && category !== null && category !== "") return `Toifa #${category}`;
        return "";
    };

    // Faqat http(s) rasm manzillariga ruxsat beramiz
    const getImageSrc = (image, alt) => (
        typeof image === "string" && /^https?:\/\//i.test(image.trim()) ? image.trim() : fallbackImage(alt)
    );

    const setPaginationVisible = (visible) => {
        if (pagination) pagination.style.display = visible ? "" : "none";
    };

    // Yuklanmoqda / xato / bo'sh holatlari (mavjud .empty-state dizayni asosida)
    const showState = (type) => {
        setPaginationVisible(false);
        const states = {
            loading: `<div class="product-state empty-state"><i class="fa-solid fa-spinner fa-spin"></i><p>Mahsulotlar yuklanmoqda...</p></div>`,
            error: `<div class="product-state empty-state"><i class="fa-solid fa-triangle-exclamation"></i><p>Ma'lumotlarni yuklab bo'lmadi. Qaytadan urinib ko'ring.</p><button type="button" class="btn btn-outline" data-retry>Qayta urinish</button></div>`,
            empty: `<div class="product-state empty-state"><i class="fa-solid fa-box-open"></i><p>Hozircha mahsulotlar mavjud emas.</p></div>`
        };
        productContainer.innerHTML = states[type];
    };

    // Javob massiv yoki { results: [...] } ko'rinishida bo'lishi mumkin (DRF paginatsiyasi)
    const extractProducts = (data) => {
        const list = Array.isArray(data) ? data : (data && Array.isArray(data.results) ? data.results : null);
        if (!list) throw new Error("API kutilmagan formatda javob qaytardi");
        return list.filter((item) => item && typeof item === "object");
    };

    // Mahsulotlarni olish funksiyasi
    async function fetchProducts() {
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

        try {
            showState("loading");

            const response = await fetch(API_URL, { headers: { Accept: "application/json" }, signal: controller.signal });
            if (!response.ok) {
                throw new Error("Serverdan ma'lumot olishda xatolik yuz berdi!");
            }

            const data = await response.json();
            displayProducts(extractProducts(data));

        } catch (error) {
            console.error("Xatolik:", error);
            showState("error");
        } finally {
            clearTimeout(timer);
        }
    }

    // Mahsulotlarni mavjud kartochka (.product-card) dizaynida ekranga chiqarish
    function displayProducts(products) {
        if (products.length === 0) {
            showState("empty");
            return;
        }

        productContainer.innerHTML = products.map((product) => {
            const title = String(product.title || product.name || "Nomsiz mahsulot");
            const category = getCategoryLabel(product.category);
            const description = typeof product.description === "string" ? product.description.trim() : "";
            const quantity = Number(product.quantity);
            const hasQuantity = product.quantity !== null && product.quantity !== undefined && Number.isFinite(quantity);
            const rating = Math.min(5, Math.max(0, Number(product.rating) || 0));
            const detailUrl = product.id !== undefined && product.id !== null
                ? `mahsulot-detail.html?id=${encodeURIComponent(product.id)}`
                : "mahsulot-detail.html";

            return `
<div class="product-card">
        ${hasQuantity && quantity <= 0 ? '<div class="badge sold-out">Tugagan</div>' : ""}
        <a href="${detailUrl}" class="product-img"><img src="${escapeHtml(getImageSrc(product.image, title))}" alt="${escapeHtml(title)}" loading="lazy"></a>
        <div class="product-info">${category ? `<div class="product-category">${escapeHtml(category)}</div>` : ""}<h3 class="product-title"><a href="${detailUrl}">${escapeHtml(title)}</a></h3>${description ? `<p class="product-desc">${escapeHtml(description)}</p>` : ""}<div class="product-rating"><div class="rating-stars">${buildStars(rating)}</div><span class="rating-count">${rating.toFixed(1)} reyting</span></div>${hasQuantity ? `<div class="product-stock">${quantity > 0 ? `Omborda: ${quantity} dona` : "Omborda yo'q"}</div>` : ""}<div class="product-price-row"><div class="price-box"><span class="price">${escapeHtml(formatPrice(product.price))}</span></div><a href="savatcha.html" class="add-cart-btn"><i class="fa-solid fa-cart-plus"></i></a></div><a href="${detailUrl}" class="btn btn-outline" style="margin-top:14px;width:100%;">Batafsil</a></div>
    </div>`;
        }).join("");

        // Rasm yuklanmasa, zaxira rasm ko'rsatiladi
        qsa("img", productContainer).forEach((img) => {
            img.addEventListener("error", function handleImageError() {
                if (this.dataset.fallbackApplied === "true") return;
                this.dataset.fallbackApplied = "true";
                this.src = fallbackImage(this.alt || "Rasm topilmadi");
            });
        });

        // API sahifalamaydi (barcha mahsulotlar bir javobda keladi), shuning uchun statik sahifalash yashirilgan
        setPaginationVisible(false);
    }

    // "Qayta urinish" tugmasi
    productContainer.addEventListener("click", (event) => {
        if (event.target.closest("[data-retry]")) fetchProducts();
    });

    // Funksiyani ishga tushirish
    fetchProducts();
});

const fallbackImage = (alt = 'Mahsulot rasmi') => {
  const label = encodeURIComponent(alt);
  return `data:image/svg+xml;charset=UTF-8,<svg xmlns='http://www.w3.org/2000/svg' width='800' height='600' viewBox='0 0 800 600'><rect width='800' height='600' rx='28' fill='%23EEF2FF'/><rect x='110' y='120' width='580' height='360' rx='26' fill='%23C7D2FE'/><text x='400' y='305' text-anchor='middle' fill='%23312E81' font-family='Arial,sans-serif' font-size='42' font-weight='700'>${label}</text></svg>`;
};

const initImageFallbacks = () => {
  qsa('img').forEach((img) => {
    img.addEventListener('error', function handleImageError() {
      if (this.dataset.fallbackApplied === 'true') return;

      this.dataset.fallbackApplied = 'true';
      this.src = fallbackImage(this.alt || 'Rasm topilmadi');
    });
  });
};