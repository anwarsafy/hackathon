# خطوات النشر الآن — كل حاجة بالترتيب

الريبو عام: [github.com/anwarsafy/hackathon](https://github.com/anwarsafy/hackathon)

---

## ١) دفع التحديثات لـ GitHub

لو أضفت ملفات جديدة (مثل `Dockerfile`, `render.yaml`, `API_FOR_FRONTEND.md`, `DEPLOY.md`) ولم تدفعها بعد:

```bash
cd /Users/anwr/StudioProjects/hackathon
git add .
git status
git commit -m "Add deploy: Dockerfile, render.yaml, API doc, Streamlit config"
git push origin main
```

---

## ٢) نشر الباكند (API) على Render — مجاني

1. ادخل **[render.com](https://render.com)** وسجّل دخول (أو إنشاء حساب بـ GitHub أو إيميل).
2. من الداشبورد: **New** → **Web Service** (أو **Blueprint** لو حابب ينزل كل الإعدادات من `render.yaml`).
3. **Connect repository:** اختر **GitHub** ثم الريبو **anwarsafy/hackathon**.
4. الإعدادات:
   - **Name:** `semantic-guardian-api` (أو أي اسم)
   - **Region:** أي منطقة
   - **Branch:** `main`
   - **Runtime:** **Docker**
   - **Dockerfile path:** `Dockerfile` (فارغ أو الجذر = يستخدم الـ Dockerfile في الجذر)
   - **Instance type:** **Free**
5. **Advanced** → **Environment Variables** → أضف (اختياري):
   - `OPENAI_API_KEY` = مفتاحك من OpenAI (لو حابب تفعّل التحقق بالـ LLM).
   - `OPENAI_MODEL` = `gpt-4.1-mini` (اختياري).
6. **Create Web Service** وانتظر البناء والنشر (حوالي ٣–٥ دقائق).
7. بعد النجاح هتظهر لك **رابط السيرفس**، مثل:
   - `https://semantic-guardian-api.onrender.com`
   - **احفظ هذا الرابط** — هو **Base URL** للـ API وترسله لفريق الفرونت.

**تجربة سريعة:** افتح في المتصفح:
- `https://اسم-السيرفس.onrender.com/health` → لازم ترى `{"status":"ok"}`
- `https://اسم-السيرفس.onrender.com/docs` → وثائق الـ API التفاعلية

---

## ٣) نشر الداشبورد (Streamlit) — مجاني

1. ادخل **[share.streamlit.io](https://share.streamlit.io)** وسجّل دخول بـ **GitHub**.
2. **New app**.
3. **Repository:** `anwarsafy/hackathon`
4. **Branch:** `main`
5. **Main file path:** `dashboard.py`
6. (اختياري) **Advanced settings** → **Secrets**:
   ```
   OPENAI_API_KEY = sk-...
   ```
7. **Deploy** وانتظر (دقائق).
8. هتاخد رابط للتطبيق، مثل: `https://...streamlit.app`

---

## ٤) إرسال الـ API لفريق الفرونت

أرسل لهم:

1. **رابط الـ API (Base URL):**  
   `https://اسم-السيرفس-على-ريندر.onrender.com`
2. **ملف التوثيق:** من الريبو **[API_FOR_FRONTEND.md](https://github.com/anwarsafy/hackathon/blob/main/API_FOR_FRONTEND.md)** أو الرابط المباشر للوثائق التفاعلية:  
   `https://اسم-السيرفس.onrender.com/docs`

في الكود يستخدمون الـ Base URL كذا:
```js
const baseUrl = 'https://اسم-السيرفس.onrender.com';
const res = await fetch(`${baseUrl}/validate`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
```

---

## ملخص

| الخطوة | الرابط | النتيجة |
|--------|--------|---------|
| 1 | دفع الكود لـ GitHub | الريبو محدّث |
| 2 | render.com → Web Service من الريبو | رابط الـ API (Base URL) |
| 3 | share.streamlit.io → New app من الريبو | رابط الداشبورد |
| 4 | إرسال Base URL + API_FOR_FRONTEND.md للفرونت | جاهز للدمج |

كل الخطوات **مجانية** ومناسبة للمشاريع التعليمية.
