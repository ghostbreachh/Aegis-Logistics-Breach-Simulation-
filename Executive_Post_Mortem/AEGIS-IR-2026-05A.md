<div align="center">
  <h1>███████ PRIVILEGED & CONFIDENTIAL ███████</h1>
  <h3>PREPARED UNDER DIRECTION OF OUTSIDE COUNSEL (ATTORNEY-CLIENT PRIVILEGE)</h3>
</div>

**To:** The Board of Directors & Risk Committee, Aegis Logistics  
**From:** Office of the Chief Information Security Officer (CISO)  
**Date:** May 19, 2026  
**Subject:** QILIN INCIDENT POST-MORTEM & ZERO-TRUST REMEDIATION MANDATE  
**Document ID:** AEGIS-IR-2026-05A  

---

## I. BOTTOM LINE UP FRONT (BLUF)

> 🚨 **CRITICAL INCIDENT SUMMARY**
> 
> * **The Incident:** Aegis Logistics was compromised via a sophisticated Adversary-in-the-Middle (AitM) phishing campaign, bypassing our MFA. The Qilin Cartel exfiltrated 4.2TB of Tier-1 data. No ransomware was deployed; this is a pure data extortion event.
> * **Business Impact:** Extracted data includes unencrypted shipping manifests, client PII, and vendor banking routing numbers. We are currently facing a **$4.5M extortion demand**.
> * **Regulatory Triggers:** We have triggered the SEC 4-day Form 8-K materiality disclosure window, and the GDPR 72-hour notification requirement. CISA and the FBI have been engaged.
> * **Root Cause:** Systemic architectural reliance on legacy Push-MFA and perimeter-based EDR, failing to protect the actual identity session tokens.

---

## II. EXECUTIVE SUMMARY: THE ILLUSION OF SECURITY

For three years, I have warned this committee that our security posture was optimized for compliance, not resilience. I take full responsibility for failing to secure the budget and operational mandate required to transition this company to a Zero-Trust architecture. We are now paying the price for that collective risk acceptance.

The Qilin Cartel bypassed our $2.5M Endpoint Detection and Response (EDR) investment without writing a single zero-day exploit. They utilized a Tycoon 2FA framework to steal an authenticated session cookie from a Senior Logistics Manager in Rotterdam. By stealing the cookie, they became the user.

Let me be perfectly clear regarding executive liability: as demonstrated by recent SEC enforcement actions against corporate officers (e.g., *SolarWinds*), ignorance of architectural vulnerabilities is no longer a legal defense. We must overhaul our identity perimeter immediately, or we will not survive the regulatory fines and class-action lawsuits that will inevitably follow this breach.

---

## III. ATTACK PATH FORENSICS & ARCHITECTURAL FAILURES

To guarantee this does not happen again, my DFIR and Threat Intelligence teams have reconstructed the exact attack chain.

### A. The Tycoon 2FA Interception (Visualized)
The adversary did not hack our systems; they hacked human psychology and flawed network trust.

```text
[Rotterdam Manager] ---> Clicks Phishing Link (HTML Smuggling LNK drop)
       |
       v
[Tycoon 2FA Proxy]  <--- Bypasses automated scanners via Cloudflare Turnstile CAPTCHA
       |                 Presents spoofed Microsoft Azure AD login page
       v
[Aegis Azure AD]    <--- User inputs credentials. User approves Push-MFA on phone.
       |
       v
[Azure AD issues JWT] -> Cookie sent back... BUT intercepted by Tycoon Proxy.
                         Attacker injects stolen cookie into their browser.
                         *Aegis Network Penetrated.*

Phase,Tactics & Techniques,Forensic Reality (How They Did It),Architectural Failure (Why We Missed It)
Initial Access,T1566.002 (Spearphishing),"Email bypassed our Secure Email Gateway (SEG). The payload used HTML Smuggling to drop an obfuscated .LNK file, evading Mark of the Web (MotW).",SEG URL rewriting failed. We relied on users to spot a newly registered domain (aegis-logistcs-portal.com) while under end-of-quarter stress.
Credential Access,T1539 (Steal Web Cookie),User approved the Push-MFA. Tycoon stole the JWT session token (valid for 90 days).,CRITICAL FLAW: We lacked Token Binding and Conditional Access. The IdP did not verify if the device was an Intune-managed corporate asset.
Execution & Privilege,T1059 (Command Shell),".LNK executed a PowerShell cradle, pulling a PyInstaller RAT.","AppLocker was in ""Audit Only"" mode to prevent ""business friction."" Local Admin rights were never fully revoked."
Defense Evasion,T1070 (Indicator Removal),Attacker used native commands to clear Event Log Security 4624 (Logon) to hide lateral pivoting.,"EDR was misconfigured to skip sandbox detonation for high-entropy files >30MB to ""save bandwidth."""
Exfiltration,T1567.002 (Exfiltration to Cloud),Qilin used rclone to siphon 4.2TB to the Mega.nz API over 14 hours.,"Data Loss Prevention (DLP) failed. We had no network baseline for outbound anomalies, and non-sanctioned cloud storage was open."
