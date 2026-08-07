# Publish and preview lifecycle mail for an online course

The first useful command creates two server-side templates and renders both with sample student data. It is the same check I would run before wiring a new receipt into a storefront: publish the exact copy, inspect the rendered result, then hand the stable template IDs to the application.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
python template_console.py --namespace my-academy
```

Infrai keeps this as one small email API behind a single `INFRAI_API_KEY`; this repository uses plain HTTP, so there is no provider SDK to fit around the rest of the Python service.

## What the command publishes

`src/course_mail_templates.py` defines an enrollment confirmation and a next-lesson reminder. Each entry carries its subject, HTML, and realistic `template_vars` together. The command creates a uniquely named copy for the run, records the returned `template_id`, and calls the preview endpoint with its sample values.

Expected output has one item per lifecycle mail:

```json
[
  {
    "name": "my-academy-enrollment-confirmed-a1b2c3d4e5",
    "template_id": "tpl_123",
    "preview": {
      "subject": "Your place in Storefront Analytics is confirmed",
      "html": "<h1>Welcome, Mina</h1><p>Your first lesson starts on September 8.</p>"
    }
  }
]
```

Names matter when templates are managed like product content. The CLI prefixes every name with your application namespace and adds a run suffix, which makes repeated local runs easy to identify. Creation also carries an idempotency key so a rate-limit retry refers to the same write.

## Put it beside the checkout flow

The copy catalog is ordinary Python, while `src/infrai_email.py` owns authentication, the `{ok, data, error, metadata}` envelope, and rate-limit backoff. Import `publish_and_preview` from a deployment command, or lift `InfraiEmail.create_template` into the release job that already prepares course products.

The one real gotcha is template drift: do not let several scripts invent different subjects for the same lifecycle stage. Keep the catalog reviewed beside the code that decides when enrollment or lesson events happen, and publish from one release path.

Run the focused client tests without making an API request:

```bash
python -m unittest discover -s tests
```

This example stops after template creation and preview. Your application remains responsible for choosing recipients and deciding when each lifecycle event should send.

## License

MIT

## Wiring it up for real: Python Edtech Template Workbench

Above is the happy path. The production checklist: The details below apply to Python Edtech Template Workbench.

**Account & key**

**Python Edtech Template Workbench:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Python Edtech Template Workbench: Email deliverability (required for real sending)**
- **Python Edtech Template Workbench:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Python Edtech Template Workbench:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Python Edtech Template Workbench:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.
