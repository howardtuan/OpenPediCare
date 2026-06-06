
# OpenPediCare
OpenPediCare is a pediatric post-visit care workspace for doctors and parents. A doctor enters only the child's basic details, records the visit, reviews a read-only live transcript, optionally adds physician notes, and generates:
<img width="1306" height="689" alt="img1" src="https://github.com/user-attachments/assets/27f5c2cc-82cd-4401-8c5a-2c678dc8df09" />
<img width="1865" height="834" alt="img2" src="https://github.com/user-attachments/assets/7f96ce6e-05e6-4fb4-8a82-a7dd1a4137bc" />
- Visit summary
- Parent education
- Patient education tailored by age
- Optional four-panel education comic
- Shareable parent portal page and PDF output

[繁體中文說明](README.zh-TW.md)

## Quick Start With Docker

```bash
cp .env.example .env
docker compose up --build
```

Open the app:

```text
http://localhost:8000
```

Demo accounts:

```text
Doctor: doctor@example.test / Doctor123!
Parent: parent@example.test / Parent123!
```

If port `8000` is already used, build and run on `8002`:

```bash
docker build -t openpedicare:local .
docker run -d --name openpedicare_live -p 8002:8000 --env-file .env \
  -v "$PWD/data:/app/data" \
  -v "$PWD/media:/app/media" \
  openpedicare:local
```

## Environment Variables

Copy `.env.example` to `.env` and fill production secrets before deployment.

```text
DJANGO_SECRET_KEY=change-me-to-a-long-random-value
JWT_SECRET=change-me-to-a-different-long-random-value
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,.ngrok-free.app,.ngrok-free.dev,.ngrok.app
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,https://*.ngrok-free.app,https://*.ngrok-free.dev,https://*.ngrok.app
SQLITE_PATH=data/db.sqlite3
```

## AI API

Default provider is ikuncode with an OpenAI-compatible chat completions endpoint:

```text
AI_PROVIDER=ikuncode
IKUNCODE_API_KEY=your_ikuncode_key
IKUNCODE_BASE_URL=https://api.ikuncode.cc/v1
IKUNCODE_MODEL=gpt-5.4-mini
```

Switch to OpenAI-compatible configuration:

```text
AI_PROVIDER=openai
OPENAI_API_KEY=your_openai_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_CHAT_MODEL=gpt-5.4-mini
```

If no AI key is configured, OpenPediCare uses a local mock fallback so the UI and workflow can still be tested. Do not use mock output for production clinical documents.

## Optional Four-Panel Comics

Comic generation uses OpenAI image generation. The “Generate comic” button appears only when an image key is configured:

```text
OPENAI_IMAGE_API_KEY=your_openai_image_key
OPENAI_IMAGE_BASE_URL=https://api.openai.com/v1
OPENAI_IMAGE_MODEL=gpt-image-1-mini
```

The comic prompt adapts by age:

- Ages 3-5: visual, ultra-short, picture-book style.
- Ages 6-11: story-based with simple science explanations.
- Ages 12-17: more professional, semi-clinical, respectful of autonomy.

## Live Speech Transcription

The doctor console uses the browser Web Speech API for live transcription.

- Chrome or Edge is recommended.
- `localhost` can access the microphone directly.
- External mobile testing should use the HTTPS ngrok URL.
- The live transcript is read-only to users.
- Each recognized sentence is shown on a new line.
- Pause and Resume are one toggle button.
- Stopping and starting again continues the current visit without duplicating previous transcript text.
- Audio chunks are temporarily stored and cleaned after `AUDIO_RETENTION_HOURS`.

Clean expired audio:

```bash
docker compose exec web python manage.py clean_expired_audio
```

## User Flows

Doctor flow:

1. Sign in as the doctor.
2. Enter child name, age, and sex.
3. Start recording.
4. Review the read-only live transcript.
5. Pause or resume when needed.
6. Stop recording.
7. Skip notes or add physician notes.
8. Generate post-visit output.
9. Review summary, parent education, patient education, parent link, PDF, and optional comic.

Returning patients:

- Returning patients are selected inside the Visit tab under “Returning patient.”
- The History tab stays focused on recent analyses only.
- A future production extension can add parent-linked patient profiles, follow-up reason, growth chart context, medication history, and previous-visit comparison before recording starts.

Parent flow:

1. Sign in as the parent demo account.
2. Open linked post-visit records.
3. Review parent education, patient education, PDF, and generated comic when available.
4. Parents can also use the share link generated from a doctor visit.

Language:

- UI defaults to English.
- The top-right button toggles English and Traditional Chinese.

## ngrok

Start the app and tunnel:

```bash
docker compose --profile tunnel up --build
```

View the tunnel URL:

```text
http://localhost:4040
```

Optional fixed domain:

```text
NGROK_AUTHTOKEN=your_ngrok_token
NGROK_DOMAIN=https://your-domain.ngrok.app
ALLOWED_HOSTS=localhost,127.0.0.1,.ngrok-free.app,.ngrok-free.dev,.ngrok.app,your-domain.ngrok.app
CSRF_TRUSTED_ORIGINS=http://localhost:8000,https://your-domain.ngrok.app
```

## Local Development

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_demo
.venv/bin/python manage.py runserver 0.0.0.0:8000
```

Run tests:

```bash
.venv/bin/python manage.py test
```

## API Endpoints

- `POST /api/auth/login`
- `GET / POST /api/patient`
- `POST /api/visit/start`
- `WebSocket /api/visit/transcribe/`
- `POST /api/visit/complete`
- `GET /api/output/{visit_id}`
- `POST /api/output/{visit_id}/comic`
- `GET /api/output/{visit_id}/school-note`

## Production Notes

OpenPediCare supports post-visit communication and education. It is not a diagnostic device and does not replace clinician judgment. Before public deployment, rotate all secrets, disable debug mode, configure HTTPS, review data retention, and complete the security and compliance checks required by your clinical setting.
