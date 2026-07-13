# Welcome sequence (5 emails over 14 days)

Load these into any ESP (Resend, Postmark templates, Mailchimp, Klaviyo) when
SMTP is wired. Placeholders — {metro}, {ooh_rate}, {plan_summary}, {fast_wins},
{operator_teaser}, {seasonal_hint}, {app_url} — fill from /api/plan for the
lead's saved metro+budget (leads table stores both).

Cadence: 0 / 2 / 5 / 9 / 14 days. Only email 5 sells; 1–4 must be genuinely
useful standalone. Every send teases exactly one gated thing.
