# Day 13 — WHOIS Lookup Report

**Topic:** Domain name structure, WHOIS lookups, registrar identification, TLD types (gTLD / ccTLD / new gTLDs)
**Practical:** WHOIS lookups on 5 domains — `.com`, `.gov`, `.org`, and a ccTLD (`.co.uk`)

> **Method note:** This sandbox environment can't open a direct port‑43 WHOIS/RDAP socket, so lookups were run through registry/registrar-sourced WHOIS mirrors (whois.com, whoxy, Nominet's public WHOIS, get.gov, and IANA's TLD delegation records) rather than the raw `whois` command. Field values match what those authoritative sources currently publish.

---

## Summary Table

| # | Domain | TLD Type | Registrar | Creation Date | Expiry Date | WHOIS Privacy | Exposed Info | Redacted Info |
|---|--------|----------|-----------|----------------|-------------|----------------|----------------|----------------|
| 1 | **github.com** | gTLD (`.com`) | MarkMonitor, Inc. | 2007‑10‑09 | 2026‑10‑09 | **On** (privacy/proxy) | Registrar, registry domain ID, creation/updated/expiry dates, domain status codes, name servers (AWS/NS1), DNSSEC status | Registrant, Admin & Tech name, org, address, phone, email — all `REDACTED FOR PRIVACY` |
| 2 | **usa.gov** | Sponsored gTLD (`.gov`) | get.gov (U.S. General Services Administration / CISA `.gov` registry) | 1999‑08‑18 | 2027‑08‑18 | **On** (registry-level redaction) | Registrar (get.gov), WHOIS/RDAP server, creation/updated/expiry dates, `serverTransferProhibited` status | Registrant, Admin & Tech name, org, address, phone, email — all `REDACTED FOR PRIVACY` in the public WHOIS mirror |
| 3 | **wikipedia.org** | gTLD (`.org`) | MarkMonitor, Inc. (registry: Public Interest Registry) | 2001‑01‑13 | Renews annually (~Jan each year) | **On** (privacy/proxy) | Registrar, registry domain ID, creation/updated dates, name servers | Registrant, Admin & Tech name, org, address, phone, email — all `REDACTED FOR PRIVACY` |
| 4 | **bbc.co.uk** | ccTLD (`.uk`, UK — Nominet) | **British Broadcasting Corporation** (registrar tag: `BBC`) | Before Aug‑1996 | 2034‑12‑13 | **Off** — no redaction | Full registrant name & type ("UK Corporation by Royal Charter"), registrant address (Broadcasting House, Portland Place, London W1A 1AA), registrar, registration/expiry/updated dates, name servers | Nothing meaningful redacted — organisational registrants on `.uk` aren't eligible for Nominet's individual address-hiding option |
| 5 | **amazon.com** | gTLD (`.com`) | MarkMonitor, Inc. | 1994‑11‑01 | 2026‑10‑31 | **On** (privacy/proxy) | Registrar, registry domain ID, creation/updated/expiry dates, domain status codes, name servers | Registrant, Admin & Tech name, org, address, phone, email — all `REDACTED FOR PRIVACY` |

---

## Observations

- **4 of 5 domains (all the `.com`/`.org`/`.gov` entries) redact registrant contact details.** This is the post‑GDPR norm for gTLDs: ICANN's 2018 Temporary Specification pushed registrars to mask personal data by default, and corporate registrants (Google/Amazon/GitHub/Wikimedia) route registrations through **MarkMonitor**, a corporate/brand-protection registrar that redacts contact fields as a matter of course regardless of GDPR applicability.
- **`usa.gov` is redacted too**, which is a bit counter‑intuitive for a federal government domain — one might expect agency contact info to be public by default. In practice the `.gov` registry (operated by CISA/GSA via get.gov, now delegated through Cloudflare as registry customer service) still masks registrant contact fields in the public WHOIS output, though the **registrar of record is always shown as `get.gov`** since it's the sole registrar for the entire `.gov` namespace — there's no competitive registrar market for `.gov` like there is for gTLDs.
- **`bbc.co.uk` is the one exception with fully exposed registrant data.** Nominet (the `.uk` registry) only allows *individual, non‑trading registrants* to opt out of publishing their address. Since the BBC is registered as an **organisation** ("UK Corporation by Royal Charter"), its full name and postal address appear in the open WHOIS record. This nicely illustrates that WHOIS privacy protection is generally an *individual* protection, not an organisational one — most companies simply don't qualify for full redaction on ccTLDs the way they can on gTLDs via a proxy service.
- **Registrar concentration:** 3 of 5 domains (github.com, wikipedia.org, amazon.com) use the same registrar, **MarkMonitor**, which specializes in corporate/brand domain defense rather than retail registration — a pattern typical of large, high-value brands protecting their primary domains from hijacking/transfer attacks (note the `clientTransferProhibited` / `clientUpdateProhibited` style locks on these records).
- **`.gov` is a *sponsored* gTLD, not an open one** — there is only one registrar (get.gov) for the entire TLD, and registrants must be verified U.S. government entities. This contrasts with `.com`/`.org`, where any of ~2,800 ICANN-accredited registrars can sell the domain, and with `.uk`, where Nominet accredits its own separate set of registrars.
- **WHOIS → RDAP transition:** As of 28 January 2025, ICANN no longer requires gTLD registries/registrars to run legacy port‑43 WHOIS; RDAP is now the mandated protocol. The mirrors used above still present RDAP data in classic WHOIS-style formatting for readability, which is why the field names (Registry Domain ID, Registrar WHOIS Server, etc.) look like traditional WHOIS output even though the underlying data increasingly comes from RDAP endpoints.

---

## Key Takeaway

Across this sample, **privacy protection correlates more with registrar/registry policy than with domain type**: gTLD registrations funneled through corporate-brand registrars (MarkMonitor, get.gov) are redacted by default, while a ccTLD registration held by an *organisation* rather than an *individual* (bbc.co.uk) stays fully public because the underlying registry's privacy rules simply don't extend redaction to non-individual registrants.
