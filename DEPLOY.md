# Deploy Backend & Frontend

---

## نشر مجاني ١٠٠٪ (Free hosting — تعليمي)

المشروع تعليمي فالأفضل تنشره على خطط **مجانية** بدون بطاقة. أنسب خيارين:

### ١) الباكند (API) — Render مجاني

1. ارفع الكود على **GitHub** (ريبو عام).
2. ادخل [render.com](https://render.com) وسجّل حساب (بريد فقط، بدون فيزا).
3. **New** → **Web Service**.
4. وصّل الريبو (Connect GitHub → اختر `anwarsafy/hackathon`).
5. الإعدادات:
   - **Name:** مثلاً `semantic-guardian-api`
   - **Region:** أي منطقة
   - **Branch:** `main`
   - **Runtime:** **Docker**
   - **Dockerfile path:** `Dockerfile` (اتركه في الجذر)
   - **Instance type:** **Free**
6. **Advanced** → **Add Environment Variable**:  
   - `OPENAI_API_KEY` = مفتاحك (اختياري؛ بدونه يشتغل الفحص بالقواعد فقط).
7. **Create Web Service** وانتظر البناء (دقائق).
8. بعد النشر هتاخد رابط مثل:  
   `https://semantic-guardian-api.onrender.com`  
   **هذا هو الـ Base URL** أرسله لفريق الفرونت مع ملف `API_FOR_FRONTEND.md`.

**ملاحظة:** على الخطة المجانية السيرفس ينام بعد ١٥ دقيقة بدون زيارات؛ أول طلب بعده قد يأخذ ٣٠–٦٠ ثانية (cold start) ثم يرد عادي.

---

### ٢) الداشبورد (واجهة Streamlit) — Streamlit Cloud مجاني

1. الريبو لازم يكون **عام** على GitHub.
2. ادخل [share.streamlit.io](https://share.streamlit.io) وسجّل بـ GitHub.
3. **New app** → اختر الريبو والبرانش.
4. **Main file path:** `dashboard.py`
5. في **Advanced settings** → **Secrets** تقدر تضيف:
   - `OPENAI_API_KEY = sk-...` (اختياري)
6. **Deploy** → بعد دقائق هتاخد رابط للتطبيق.

كلاهما **بدون فلوس** ومناسب للمشاريع التعليمية.

---

## Backend (FastAPI API)

Deploy the API so the frontend team can call it. Options below use the included `Dockerfile`.

### Option A: Railway (requires card for free trial credits)

1. Push the repo to GitHub (e.g. `anwarsafy/hackathon`).
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub.
3. Select the repo; Railway will detect the Dockerfile and deploy the API.
4. Add env var `OPENAI_API_KEY` (and optionally `OPENAI_MODEL`) in the service settings if you want LLM validation.
5. In Settings → Networking, generate a public domain (e.g. `your-app.railway.app`).
6. Share that URL as the **base URL** with the frontend team (see `API_FOR_FRONTEND.md`).

### Option B: Render

1. Push to GitHub.
2. Go to [render.com](https://render.com) → New → Web Service.
3. Connect the repo; set:
   - **Build:** Docker.
   - **Dockerfile path:** `Dockerfile` (root).
   - **Instance type:** Free (or paid).
4. Add env vars: `OPENAI_API_KEY`, optional `OPENAI_MODEL`.
5. Deploy; Render gives a URL like `https://your-service.onrender.com`. Use it as the API base URL.

### Option C: Fly.io

```bash
# Install flyctl, then:
fly launch --no-deploy
# Edit fly.toml if needed (port 8000, http service).
fly secrets set OPENAI_API_KEY=sk-...
fly deploy
```

Use the generated `https://your-app.fly.dev` as the base URL.

### Local Docker (backend)

```bash
docker build -t semantic-guardian-api .
docker run -p 8000:8000 -e OPENAI_API_KEY=sk-... semantic-guardian-api
```

API: `http://localhost:8000`, docs: `http://localhost:8000/docs`.

---

## Frontend (Streamlit dashboard)

To deploy the Streamlit dashboard (optional; for demos or internal use):

### Railway / Render (Docker)

- Use **Dockerfile.dashboard** instead of `Dockerfile`.
- Expose port **8501** (Streamlit).
- Set env vars if the dashboard should call the deployed API (currently it runs validation in-process).

### Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io).
2. Deploy from GitHub; pick repo and branch.
3. Set **Main file:** `dashboard.py`.
4. Add `OPENAI_API_KEY` in Secrets if you want LLM in the cloud app.

---

## Sending the API to the frontend team

1. Deploy the **backend** using one of the options above.
2. Copy the public API URL (e.g. `https://your-api.onrender.com`).
3. Share with the frontend team:
   - **API doc:** `API_FOR_FRONTEND.md` (or link to `{BASE_URL}/docs`).
   - **Base URL:** the deployed URL from step 2.

They can then use the base URL in their app (e.g. `fetch(\`${baseUrl}/validate\`, ...)` as in `API_FOR_FRONTEND.md`).
