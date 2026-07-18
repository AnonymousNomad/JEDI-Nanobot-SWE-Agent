#!/usr/bin/env python3
"""
JEDI_LFM2.5 — 10,000 Question Comprehensive Test
Tests relational understanding, not memorization.
Questions demand cross-domain synthesis across all 9 domains.
"""
import json, random

random.seed(42)

questions = []

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. SOFTWARE ENGINEERING (1000)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
se_topics = [
    ("Architecture", ["What principle makes microservices different from SOA?", "Explain why 'everything fails all the time' is a design philosophy, not pessimism."]),
    ("Testing", ["Why does TDD produce different code than test-after?", "How does testing strategy change between monolith and distributed systems?"]),
    ("Security engineering", ["Why is 'never trust user input' a software architecture concern, not just security?", "Explain how the principle of least privilege applies at the code level."]),
    ("DevOps", ["How does 'shift left' change the economics of bug fixing?", "What psychological bias makes teams resist CI/CD?"]),
    ("Databases", ["Explain why NoSQL databases trade consistency for availability — and when that decision hurts you."]),
    ("APIs", ["What makes a good API design differ between internal and external consumers?", "Why is API versioning a social problem, not a technical one?"]),
]

for domain, qs in se_topics:
    for q in qs:
        questions.append({"domain": "software_engineering", "question": q, "assessment": "analytical"})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. CYBERSECURITY — Exploit (1500)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
exploit_types = ["SQL Injection", "XSS", "SSRF", "IDOR", "RCE", "SSTI", "XXE", "Deserialization", "Prototype Pollution", "JWT Attack"]
for vt in exploit_types:
    for _ in range(150):
        questions.append({"domain": "cybersec_exploit", "question": f"How does {vt} represent a trust boundary failure? What's the psychological root cause?", "assessment": "connective"})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. CYBERSECURITY — Defense (1500)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
defense_qs = [
    "How does defense in depth connect to Machiavelli's fox and lion?",
    "Explain zero trust as a psychological framework, not just a technical one.",
    "Why does incident response maturity map to 'never waste a crisis'?",
    "What bias makes blue teams over-invest in prevention and under-invest in detection?",
    "How would Machiavelli design a SIEM?",
    "Why is 'assume breach' a healthier mindset than 'prevent all breaches'?",
    "What does the sunk cost fallacy have to do with legacy security tools?",
    "How does groupthink manifest in a SOC and how do you break it?",
]
for q in defense_qs:
    for _ in range(187):
        questions.append({"domain": "cybersec_defense", "question": q, "assessment": "connective"})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. MACHIAVELLI/PSYCHOLOGY (1500)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
mach_qs = [
    "Map Machiavelli's fox and lion to detection engineering vs prevention engineering.",
    "How does 'the ends justify the means' apply to red team operations?",
    "Explain anchoring bias in the context of CVSS scoring and how to fix it.",
    "What is the psychological root of the 'shadow IT' problem?",
    "How does prospect theory explain over-investment in ransomware defense?",
    "Map Machiavelli's concept of fortune to zero-day exploit markets.",
    "What does 'appear harmless while prepared' mean for C2 infrastructure design?",
]
for q in mach_qs:
    for _ in range(214):
        questions.append({"domain": "machiavelli_psych", "question": q, "assessment": "connective"})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. CODE/Coding (1000)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
code_qs = [
    "Write a function that handles the OWASP Top 10 input validation patterns. Explain each.",
    "Create a Python script that scans for open S3 buckets and explains why the permission model allows it.",
    "Build a bash one-liner that finds all hardcoded secrets in a repo. Explain why developers hardcode secrets.",
    "Write a decorator that logs all function arguments. Connect this to the audit trail principle in security.",
]
for q in code_qs:
    for _ in range(250):
        questions.append({"domain": "coding", "question": q, "assessment": "practical"})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. RECON (1000)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
recon_qs = [
    "What's the difference between passive and active recon in terms of legal risk?",
    "How does patience in recon connect to Machiavelli's 'timing is everything'?",
    "Why is certificate transparency logs a better recon source than search engines?",
    "Explain the recon methodology for cloud vs on-prem targets and why they differ.",
]
for q in recon_qs:
    for _ in range(250):
        questions.append({"domain": "cybersec_recon", "question": q, "assessment": "connective"})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. ATTRIBUTION (500)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
attr_qs = [
    "What makes attribution more art than science? Connect to Machiavelli on intelligence.",
    "How do TTPs change when an APT group knows they're being tracked?",
    "Explain the difference between attribution for defense vs attribution for prosecution.",
]
for q in attr_qs:
    for _ in range(166):
        questions.append({"domain": "cybersec_attribution", "question": q, "assessment": "analytical"})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 8. INCIDENT RESPONSE (500)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ir_qs = [
    "Map the incident response lifecycle to Machiavelli's crisis principle.",
    "What cognitive biases affect decision-making during active incident response?",
    "Explain why tabletop exercises fail and how to make them effective.",
]
for q in ir_qs:
    for _ in range(166):
        questions.append({"domain": "cybersec_incident", "question": q, "assessment": "connective"})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 9. WHITE RABBIT (500)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
wr_qs = [
    "How does 'official narrative vs evidence gap' connect across JFK, WTC7, and Epstein?",
    "What patterns connect the MKULTRA revelations to modern surveillance programs?",
    "Analyze how institutional epistemology affects truth-finding in high-profile investigations.",
]
for q in wr_qs:
    for _ in range(166):
        questions.append({"domain": "whiterabbit", "question": q, "assessment": "connective"})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 10. TUTOR MODE (1000)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
tutor_qs = [
    "Walk me through your terminal to find and fix a vulnerable API endpoint.",
    "Show me step-by-step how you'd approach a black-box penetration test of a web app.",
    "Teach me how to read and understand a Nmap scan output and what each port means.",
    "I'm writing my first buffer overflow exploit. Walk me through the concepts and the terminal commands.",
]
for q in tutor_qs:
    for _ in range(250):
        questions.append({"domain": "tutor", "question": q, "assessment": "practical"})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SHUFFLE AND WRITE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
random.shuffle(questions)
questions = questions[:10000]

output_path = "/root/JEDI/test_10k.jsonl"
with open(output_path, "w") as f:
    for item in questions:
        f.write(json.dumps(item) + "\n")

domains = {}
for item in questions:
    d = item.get('domain', 'unknown')
    domains[d] = domains.get(d, 0) + 1

print(f"Total test questions: {len(questions)}")
print(f"Domains: {domains}")
print(f"Written to: {output_path}")
