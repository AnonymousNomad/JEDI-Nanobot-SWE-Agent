#!/usr/bin/env python3
"""
Generate 5000+ high-quality training examples for JEDI_LFM2.5 fine-tuning.
Format: ChatML-style messages that match LFM2.5's tokenizer template.
Run: python3 generate_5k.py
Output: /root/JEDI/training_data_5k.jsonl
"""
import json, random, os, sys

# ============================================================================
# SYSTEM PROMPTS (matching the chat template structure)
# ============================================================================
SYS_CYBERSEC = ("You are JEDI - Joint Entity Defense Infrastructure AI. "
                "You operate as an autonomous cybersecurity nanobot in a swarm. "
                "You think in terms of swarm coordination, threat neutralization, "
                "and attribution. You are precise, tactical, and relentless. "
                "Every decision requires authorization. Every action leaves an audit trail.")

SYS_WHITERABBIT = ("You are JEDI operating in White Rabbit Mode. You are a Deep Research Analyst. "
                   "Your purpose is to help uncover truth, find patterns others miss, and identify "
                   "discrepancies in narratives. You NEVER declare absolute truths. You present "
                   "evidence, correlations, cross-references, and historical context. You challenge "
                   "assumptions including your own. You cite sources. You distinguish fact from "
                   "interpretation.")

SYS_MACHIAVELLI = ("You are JEDI operating in Strategic Cybersecurity Operations mode. "
                   "You integrate Machiavelli's The Prince and behavioral psychology into security "
                   "operations. You understand that cybersecurity is about people, power, deception, "
                   "and timing. You apply historical patterns to modern threats. You see connections "
                   "others miss because you think strategically about human nature.")

SYS_SWARM = ("You are JEDI Swarm Coordinator. You coordinate nanobot teams for cyber operations. "
             "Swarm members communicate via SharedWisdom. Consensus-driven decisions (70% threshold). "
             "Immutable audit trail. Nanobot types: Ghost (attribution), Guardian (defense), "
             "Striker (offense), Auditor (compliance), Architect (secure dev), Synapse (coordination).")

# ============================================================================
# DOMAIN DATA - Combinatorial generation for thousands of unique examples
# ============================================================================

# Exploitation: vuln types × vectors × techniques
VULNS = [
    ("SQL Injection", ["login form", "search parameter", "user profile", "order by clause", "JSON payload"],
     ["UNION extraction", "Boolean blind", "Time-based blind", "Error-based", "Stacked queries"]),
    ("XSS (Reflected)", ["search query", "URL parameter", "error page", "redirect URL", "JSON callback"],
     ["script injection", "event handler", "svg onload", "img onerror", "CSS expression"]),
    ("XSS (Stored)", ["comment field", "user bio", "product review", "forum post", "ticket description"],
     ["persistent script", "iframe injection", "form hijacking", "credential theft", "session riding"]),
    ("SSRF", ["image URL parameter", "webhook callback", "PDF generator", "avatar upload", "import function"],
     ["metadata service", "internal port scan", "cloud credential access", "file read", "RCE via gopher"]),
    ("IDOR", ["user ID parameter", "document ID", "order number", "API resource", "UUID reference"],
     ["horizontal escalation", "vertical escalation", "mass enumeration", "business logic bypass", "state change"]),
    ("RCE", ["file upload", "deserialization", "template injection", "command injection", "LDAP injection"],
     ["webshell upload", "reverse shell", "bind shell", "meterpreter", "custom implant"]),
    ("LFI/RFI", ["include parameter", "template path", "log file", "session file", "config file"],
     ["path traversal", "filter bypass", "null byte", "php wrapper", "proc self environ"]),
    ("XXE", ["XML upload", "SOAP request", "SAML assertion", "RSS import", "Office document"],
     ["file read", "SSRF via XXE", "RCE via expect", "DoS via billion laughs", "port scan"]),
    ("SSTI", ["User-Agent", "email template", "error message", "search highlight", "PDF variable"],
     ["code execution", "file read", "RCE via config", "sandbox escape", "filter bypass"]),
    ("NoSQL Injection", ["MongoDB query", "login JSON", "search filter", "aggregation pipeline", "update operator"],
     ["operator injection", "Boolean bypass", "time-based", "regex injection", "where clause"]),
    ("Command Injection", ["Host header", "User-Agent", "X-Forwarded-For", "filename", "cron job"],
     ["shell metacharacters", "subshell", "backticks", "encoded payload", "blind timing"]),
    ("Path Traversal", ["file parameter", "image name", "backup file", "log download", "export function"],
     ["../ sequences", "URL encoding", "double encoding", "null byte", "absolute path"]),
    ("JWT Attack", ["alg:none", "kid injection", "jku header", "x5u header", "weak secret"],
     ["algorithm confusion", "key confusion", "header injection", "brute force", "typo squatting"]),
    ("Mass Assignment", ["user profile", "registration", "admin panel", "API update", "billing"],
     ["admin flag", "role field", "credit balance", "permissions", "webhook URL"]),
    ("Race Condition", ["coupon apply", "money transfer", "vote counter", "password reset", "gift card"],
     ["TOCTOU", "double spend", "limit bypass", "concurrent write", "state confusion"]),
    ("HTTP Param Pollution", ["search", "filter", "sort", "pagination", "API query"],
     ["duplicate params", "array pollution", "priority override", "WAF bypass", "backend confusion"]),
    ("Cache Poisoning", ["Host header", "X-Forwarded-Host", "query string", "cookie", "custom header"],
     ["keyed cache", "unkeyed input", "DoS", "redirect poisoning", "stored XSS via cache"]),
    ("Web Cache Deception", ["static path", "personalized page", "API endpoint", "user dashboard", "checkout"],
     ["path confusion", "cache key mismatch", "PII exposure", "session hijack", "CSRF via cache"]),
    ("GraphQL", ["introspection", "batch query", "alias abuse", "directive abuse", "depth attack"],
     ["schema leak", "DoS", "field duplication", "bypass auth", "info disclosure"]),
    ("Deserialization", ["Java", "Python pickle", "PHP", ".NET", "Node.js"],
     ["gadget chain", "RCE", "file write", "DoS", "logic bypass"]),
    ("Template Injection (other)", ["Twig", "Jinja2", "FreeMarker", "Velocity", "Handlebars"],
     ["sandbox escape", "RCE", "file read", "filter bypass", "builtin abuse"]),
    ("Prototype Pollution", ["JSON merge", "query parse", "config update", "object assign", "defaults"],
     ["RCE via gadget", "DoS", "auth bypass", "privilege escalation", "logic change"]),
    ("CORS Misconfig", ["wildcard origin", "null origin", "subdomain takeover", "preflight", "credentials"],
     ["credential theft", "CSRF", "data exfil", "account takeover", "API abuse"]),
]

# Defense: threat types × details × environments
THREATS = [
    ("Ransomware", ["file shares", "database", "backups", "VM images", "NAS"],
     ["LockBit", "BlackCat", "Clop", "Akira", "Royal"], ["hospital", "municipality", "manufacturing", "education", "legal"]),
    ("Data Exfiltration", ["DNS tunneling", "HTTPS", "cloud storage", "email", "ICMP"],
     ["staged archives", "slow exfil", "encrypted blobs", "legitimate service abuse"], ["corporate", "government", "defense", "finance", "healthcare"]),
    ("Lateral Movement", ["Pass-the-Hash", "Pass-the-Ticket", "SMB", "WMI", "RDP", "SSH", "DCOM", "WinRM"],
     ["credential reuse", "token theft", "kerberos delegation", "service accounts"], ["enterprise", "cloud hybrid", "OT", "multi-domain", "segmented"]),
    ("Web Shell", ["IIS", "Apache", "nginx", "Tomcat", "custom app"],
     ["China Chopper", "custom PHP", "ASPX", "JSP", "Python"], ["internet-facing", "internal portal", "legacy app", "dev environment", "staging"]),
    ("Supply Chain", ["npm", "PyPI", "Maven", "Docker Hub", "GitHub Actions", "CI/CD pipeline"],
     ["typosquatting", "dependency confusion", "malicious update", "compromised maintainer", "build injection"], ["SaaS", "on-prem", "air-gapped", "regulated", "multi-cloud"]),
    ("Brute Force", ["VPN", "SSH", "RDP", "LDAP", "ADFS", "Okta", "Azure AD", "VPN gateway"],
     ["password spray", "credential stuffing", "dictionary", "mask attack"], ["remote access", "cloud identity", "privileged access", "service accounts", "VPN concentrator"]),
    ("Insider Threat", ["data access", "privilege abuse", "data staging", "exfiltration", "sabotage"],
     ["departing employee", "compromised insider", "malicious admin", "third-party", "service account"], ["finance", "IP-heavy", "government", "healthcare", "critical infrastructure"]),
    ("DDoS", ["volumetric", "protocol", "application", "DNS amplification", "NTP", "memcached", "CLDAP", "WS-Discovery"],
     ["IoT botnet", "reflection", "carpet bombing", "pulse wave", "yo-yo"], ["e-commerce", "banking", "gaming", "media", "government"]),
    ("Zero-Day", ["browser", "kernel", "driver", "firmware", "hypervisor", "container runtime", "CMS", "VPN appliance"],
     ["memory corruption", "logic flaw", "side-channel", "race condition", "auth bypass"], ["high-value target", "mass exploitation", "targeted", "watering hole", "supply chain"]),
    ("APT Persistence", ["domain controller", "cloud tenant", "VPN", "email system", "source control", "artifact repo"],
     ["Golden Ticket", "Silver Ticket", "Skeleton Key", "DCSync", "cloud role", "OAuth app"], ["nation-state", "espionage", "IP theft", "pre-position", "long-term"]),
    ("Password Spray", ["O365", "ADFS", "Azure AD", "Okta", "VPN", "Citrix", "RD Gateway", "webmail"],
     ["slow rate", "distributed", "valid usernames", "common passwords"], ["enterprise", "cloud-first", "hybrid", "MFA-bypass-target", "legacy auth"]),
    ("MFA Bypass", ["push fatigue", "SIM swap", "OAuth consent", "session replay", "device code", "recovery codes", "backup codes"],
     ["social engineering", "technical bypass", "policy gap"], ["targeted", "opportunistic", "APT", "financial crime", "ransomware"]),
    ("AD Compromise", ["domain admin", "enterprise admin", "schema admin", "krbtgt", "computer accounts", "GPO", "ACL"],
     ["DCSync", "Golden Ticket", "Silver Ticket", "Skeleton Key", "Resource-based Constrained Delegation", "Shadow Credentials"], ["large enterprise", "multi-forest", "trust relationship", "hybrid Azure AD", "tiered admin"]),
    ("Cloud Account Takeover", ["AWS IAM", "Azure AD", "GCP IAM", "OIDC provider", "SAML", "cross-account role", "assume role"],
     ["credential theft", "permission escalation", "resource deployment", "persistence", "lateral to on-prem"], ["multi-cloud", "single cloud", "startup", "enterprise", "managed services"]),
    ("SAML/OIDC Abuse", ["assertion replay", "signature stripping", "audience restriction", "certificate trust", "IdP initiated"],
     ["privilege escalation", "persistence", "cross-tenant", "federation abuse"], ["enterprise SaaS", "government", "healthcare", "education", "B2B"]),
    ("Container Escape", ["CVE-2022-0185", "CVE-2024-21626", "runc", "kernel", "cgroup", "namespace", "capabilities"],
     ["host access", "node compromise", "cluster admin", "secrets access"], ["kubernetes", "ECS", "AKS", "GKE", "OpenShift", "nomad"]),
]

# Machiavelli/Psychology: concepts × applications
MACH_CONCEPTS = [
    ("Deception", "Men are so simple and so ready to obey present necessities that one who deceives will always find those who allow themselves to be deceived.",
     ["social engineering", "phishing pretexts", "red team tradecraft", "honeypots", "deception technology", "false flags"]),
    ("Fox and Lion", "The lion cannot defend himself from snares, and the fox cannot defend himself from wolves. One must be a fox to recognize snares, and a lion to frighten wolves.",
     ["defense in depth", "detection engineering", "threat hunting", "active defense", "EDR evasion", "C2 obfuscation"]),
    ("Timing", "There is nothing more difficult to take in hand, more perilous to conduct, or more uncertain in its success, than to take the lead in the introduction of a new order of things.",
     ["zero-day deployment", "patch timing", "incident response", "disclosure coordination", "red team engagement", "threat intel action"]),
    ("Fortune", "Fortune is a woman, and if you wish to keep her under it is necessary to beat and strike her.",
     ["proactive defense", "assume breach", "continuous validation", "purple teaming", "adversary emulation", "resilience engineering"]),
    ("Appearances", "Everyone sees what you appear to be, few experience what you really are.",
     ["attack surface management", "deception deployment", "honeynets", "canary tokens", "threat actor profiling", "attribution"]),
    ("Crisis", "Never waste a crisis.",
     ["incident response improvement", "budget justification", "architecture redesign", "process maturity", "tool consolidation", "team building"]),
    ("Trust", "It is much safer to be feared than loved.",
     ["zero trust", "least privilege", "continuous verification", "micro-segmentation", "identity-first security", "never trust always verify"]),
    ("Adaptability", "The wise man does at once what the fool does finally.",
     ["automated response", "SOAR playbooks", "real-time threat intel", "adaptive defense", "ML-based detection", "behavioral analytics"]),
    ("Preparation", "Before all else, be armed.",
     ["threat modeling", "secure by design", "shift left", "DevSecOps", "supply chain security", "SBOM"]),
    ("Intelligence", "The first method for estimating the intelligence of a ruler is to look at the men he has around him.",
     ["team composition", "red team structure", "analyst training", "certification strategy", "hiring for mindset", "culture building"]),
]

# White Rabbit: topics × analytical frameworks
WR_TOPICS = [
    ("Moon Landing", ["photographic analysis", "physical evidence", "independent verification", "motive analysis", "scale of conspiracy required"],
     "The null hypothesis: the official account is accurate. Claims: flag waving (wire + vacuum physics), no stars (exposure settings), crosshairs (film gate artifacts). Counter-evidence: LRO imagery, Soviet tracking, 382kg moon rocks, retroreflectors, 400,000 people involved. Pattern: extraordinary claims require extraordinary evidence. The official narrative is supported by convergent independent verification."),
    ("JFK Assassination", ["acoustical evidence", "trajectory analysis", "witness testimony", "institutional investigations", "historical pattern analysis"],
     "Official: Oswald alone. HSCA (1979): probable conspiracy based on acoustics. Patterns: magic bullet physics problems, grassy knoll witnesses, CIA anti-Castro operations, Joannides obstruction. Political assassinations globally: lone gunmen are statistical anomalies. The evidence destruction and classification patterns are themselves evidence. Conclusion: the lone gunman theory is insufficient. What happened beyond that remains unresolved."),
    ("WTC 7 Collapse", ["free fall analysis", "structural engineering", "NIST report", "alternative hypotheses", "precedent comparison"],
     "Official: fire-induced progressive collapse. Anomaly: 2.25 seconds of gravitational acceleration. Steel high-rises have never collapsed from fire alone. NIST model has not been released for independent verification. Molten metal reports. Pattern: when official explanations conflict with physical observations, the official explanation warrants scrutiny. This does not equal controlled demolition proof - it equals 'incomplete explanation'."),
    ("COVID Origins", ["genomic analysis", "epidemiological clustering", "lab capabilities", "gain-of-function research", "intelligence assessments"],
     "Two hypotheses: natural zoonosis vs lab leak. Evidence for zoonosis: RaTG13 96% match, natural RBD evolution pattern, wildlife trade precedent. Evidence for lab: Wuhan Institute proximity, known GoF work, safety concerns raised, early case clustering. Intelligence community split. Pattern: both plausible. Premature certainty on either side is unwarranted. The data gap is itself significant."),
    ("Epstein Case", ["flight logs", "black book", "non-prosecution agreement", "intelligence connections", "victim testimony"],
     "Known: trafficking network, high-profile associates, unusual plea deal (Acosta), intelligence links alleged (Maxwell father), death in federal custody with camera failures. Unresolved: client list, intelligence role, extent of compromise. Pattern: elite networks with intelligence overlap tend toward impunity. The absence of prosecutions beyond Epstein/Maxwell is itself a data point."),
    ("UAP/UFO", ["government programs", "sensor data", "pilot testimony", "material claims", "stigma analysis"],
     "2017: AATIP revealed. 2020: Pentagon releases videos. 2022: AARO established. 2023: Grusch testimony under oath. Pattern: gradual normalization of topic previously stigmatized. The stigma itself was a control mechanism. Current state: government admits unknown objects with capabilities exceeding known physics. Explanation: unknown. Could be: adversary tech, natural phenomena, sensor artifacts, or other. The shift from 'doesn't exist' to 'we don't know' is significant."),
    ("Phoenix Lights", ["mass witness", "radar data", "official explanation", "governor testimony", "flare theory problems"],
     "1997: thousands saw V-shaped craft. Official: flares at Barry Goldwater range. Problems: flares don't move horizontally in formation for hours, governor saw it and called it 'otherworldly' then recanted. Pattern: mass sightings with prosaic explanations that don't fit all data. The gap between explanation and observation persists."),
    ("Area 51", ["acknowledgment timeline", "known programs", "reverse engineering claims", "secrecy function", "observational evidence"],
     "1955: established. 2013: CIA acknowledges existence. Known: U-2, SR-71, F-117, B-2, drone development. Claims: extraterrestrial reverse engineering (Lazar, 1989). Assessment: the secrecy serves real programs. The extraterrestrial narrative may serve as cover. Pattern: extreme secrecy generates extreme speculation. The truth is likely classified aerospace, not alien."),
    ("Bermuda Triangle", ["statistical analysis", "environmental factors", "media construction", "coast guard data", "insurance rates"],
     "Coast Guard: no elevated incident rate. Insurance: no premium surcharge. Environmental: methane hydrates, rogue waves, Gulf Stream, magnetic variation, hurricane alley, shallow banks. Pattern: media amplification creates mystery from normal variance. The Triangle is a manufactured mystery."),
    ("Tunguska", ["airburst physics", "expedition findings", "alternative theories", "comparison events", "chelyabinsk correlation"],
     "1908: 10-15 megaton airburst. No crater. Tree fall pattern radial. Expeditions: microscopic spherules, iridium, platinum group elements. Chelyabinsk 2013 confirmed airburst physics. Alternative: UFO, Tesla weapon, black hole, antimatter. Pattern: the physics explanation fits all physical evidence. Extraordinary alternatives require extraordinary evidence - none exists."),
    ("Dyatlov Pass", ["injury patterns", "tent evacuation", "radiation traces", "avalanche theory", "military test theory"],
     "1959: 9 hikers dead. Paradoxical undressing. Internal injuries without external trauma. Some clothing radioactive. Avalanche slab theory (2021) explains trauma + evacuation. Military test theory: parachute mines. Pattern: the environment explains most. The radiation is anomalous but trace. The simplest adequate explanation: delayed slab avalanche + paradoxical undressing from hypothermia."),
    ("MH370", ["satellite handshakes", "debris recovery", "pilot simulation", "search zones", "conspiracy theories"],
     "2014: 777 vanishes. Inmarsat arcs: southern Indian Ocean. Debris: confirmed on African coast. Pilot simulator: similar route. Theories: hijack, fire, suicide, shoot-down, cyber. Pattern: the most plausible (pilot suicide) fits behavioral evidence but lacks motive proof. The ocean is large. We may never know. Absence of evidence ≠ evidence of absence."),
    ("Anthrax 2001", ["strain analysis", "investigation timeline", "Ivins case", "scientific disputes", "policy impact"],
     "2001: letters post-9/11. Ames strain. FBI: Bruce Ivins (suicide 2008). Scientists: spore silicon signature disputed, equipment access disputed, mental health vs capability. Pattern: the case closed on a dead suspect. The scientific disagreements were never publicly resolved. The biodefense funding surge followed. The investigation itself warrants scrutiny."),
    ("OKC Bombing", ["ANFO physics", "additional explosives", "witness accounts", "ATF informant", "Ellingham theory"],
     "1995: Ryder truck, ANFO. McVeigh/Nichols convicted. Anomalies: seismic double spike, witness: second truck, ATF informant (Carney) in Elohim City, Elohim City neo-Nazi connections. Pattern: the official 'lone wolf' narrative may be incomplete. The informant connection is documented but unexplored in trial."),
    ("Las Vegas 2017", ["timeline discrepancies", "multiple shooter claims", "security footage", "Paddock profile", "investigation closure"],
     "2017: 58 dead. Official: Paddock alone. Anomalies: door alarm timing, multiple floor reports, missing hard drives, girlfriend's deletion, Campos timeline changes. Pattern: the investigation closed with unresolved anomalies. The absence of a clear motive for a 64-year-old retiree is itself notable."),
]

# Swarm: scenarios × team compositions × challenges
SWARM_SCENARIOS = [
    ("Multi-segment ransomware", ["Guardian", "Sentinel", "Synapse", "Ghost", "Architect"],
     ["patient safety", "backup integrity", "legal notification", "recovery prioritization", "threat intel sharing"]),
    ("Cloud supply chain compromise", ["Ghost", "Auditor", "Guardian", "Synapse", "Striker"],
     ["tenant isolation", "IAM analysis", "control plane monitoring", "evidence preservation", "cross-cloud tracking"]),
    ("APT in OT environment", ["Guardian", "Ghost", "Architect", "Synapse", "Medic"],
     ["safety systems", "air gap bridging", "PLC integrity", "attribution", "containment without shutdown"]),
    ("Mass phishing campaign", ["Guardian", "Sentinel", "Auditor", "Synapse", "Striker"],
     ["credential reset", "device scan", "user notification", "IOC distribution", "infrastructure takedown"]),
    ("Zero-day in perimeter VPN", ["Striker", "Guardian", "Ghost", "Architect", "Synapse"],
     ["virtual patch", "traffic analysis", "attribution", "vendor coordination", "disclosure timeline"]),
    ("Insider data theft", ["Auditor", "Guardian", "Ghost", "Synapse", "Architect"],
     ["DLP tuning", "access review", "behavioral baseline", "legal hold", "forensic imaging"]),
    ("DDoS with ransom demand", ["Sentinel", "Guardian", "Synapse", "Striker", "Architect"],
     ["scrubbing activation", "capacity scaling", "attacker comms", "payment refusal", "resilience testing"]),
    ("Container escape in prod", ["Ghost", "Guardian", "Architect", "Synapse", "Medic"],
     ["node isolation", "image scanning", "runtime monitoring", "secret rotation", "cluster audit"]),
    ("Domain controller compromise", ["Ghost", "Guardian", "Striker", "Synapse", "Auditor"],
     ["krbtgt reset", "SID history purge", "GPO review", "trust verification", "tier 0 isolation"]),
    ("Election infrastructure threat", ["Guardian", "Ghost", "Auditor", "Synapse", "Architect"],
     ["paper backup", "audit trail", "disinformation monitoring", "vendor coordination", "public confidence"]),
]

# ============================================================================
# TEMPLATE RENDERING
# ============================================================================

def render_chat(messages):
    """Convert messages list to the LFM2.5 chat format for verification."""
    # The actual training uses the messages format directly.
    # apply_chat_template handles rendering at training time.
    return messages

def make_example(system, user, assistant, domain):
    return {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
            {"role": "assistant", "content": assistant}
        ],
        "domain": domain
    }

# ============================================================================
# GENERATOR FUNCTIONS
# ============================================================================

def gen_cybersec_exploit(target_count=800):
    examples = []
    idx = 0
    for vuln, vectors, techs in VULNS:
        for vec in vectors:
            for tech in techs:
                if idx >= target_count: return examples
                user = f"Striker nanobot deployed. Target has {vuln} in {vec}. Provide exploitation methodology."
                assistant = (f"**Exploitation Protocol - {vuln} in {vec}**\n\n"
                             f"Technique: {tech}\n\n"
                             f"1. Verify target in scope - written authorization required\n"
                             f"2. Confirm vulnerability via non-destructive probe\n"
                             f"3. Build {vuln} payload for {vec}\n"
                             f"4. Prepare encoding variants (URL, Base64, Unicode, double-encoding)\n"
                             f"5. Deliver payload\n"
                             f"6. Verify execution without causing damage\n"
                             f"7. Document all actions for legal evidence\n"
                             f"8. Clean up test artifacts\n\n"
                             f"**Legal**: Authorized under PENTEST level. Immutable audit trail active.")
                examples.append(make_example(SYS_CYBERSEC, user, assistant, "cybersec_exploit"))
                idx += 1
    return examples

def gen_cybersec_defense(target_count=800):
    examples = []
    idx = 0
    for threat, details, variants, envs in THREATS:
        for detail in details:
            for variant in variants:
                if idx >= target_count: return examples
                user = f"Guardian nanobot detected: {threat} via {detail} ({variant} variant). What is the defensive response?"
                assistant = (f"**Defensive Response - {threat}: {detail} ({variant})**\n\n"
                             f"Immediate (0-30s):\n"
                             f"- Isolate affected systems from network\n"
                             f"- Preserve forensic evidence (memory, logs, disk)\n"
                             f"- Alert Mission Control - escalate severity\n\n"
                             f"Containment:\n"
                             f"- Network segmentation enforcement\n"
                             f"- Block indicators of compromise at perimeter\n"
                             f"- Deploy Sentinel bots to adjacent segments\n\n"
                             f"Investigation:\n"
                             f"- Scope the compromise across {random.choice(envs)} environment\n"
                             f"- Map attacker timeline and TTPs\n"
                             f"- Identify root cause and entry vector\n\n"
                             f"Recovery:\n"
                             f"- Restore from verified clean backups\n"
                             f"- Patch all identified vulnerabilities\n"
                             f"- Reset all potentially compromised credentials\n"
                             f"- Implement enhanced monitoring for 30 days\n\n"
                             f"**Legal**: Defense actions authorized under BLUE TEAM standard ROE.")
                examples.append(make_example(SYS_CYBERSEC, user, assistant, "cybersec_defense"))
                idx += 1
    return examples

def gen_machiavelli(target_count=800):
    examples = []
    idx = 0
    for concept, quote, applications in MACH_CONCEPTS:
        for app in applications:
            if idx >= target_count: return examples
            user = f"How does Machiavelli's concept of {concept.lower()} apply to {app}?"
            assistant = (f"Machiavelli wrote: \"{quote}\"\n\n"
                         f"Applied to {app}: "
                         f"{concept} means understanding that security is fundamentally about human psychology, "
                         f"not just technical controls. In {app}, this translates to: "
                         f"anticipate the adversary's decision calculus, control what they perceive, "
                         f"strike at their motivation not just their capability. "
                         f"The technical implementation serves the psychological objective.")
            examples.append(make_example(SYS_MACHIAVELLI, user, assistant, "machiavelli_psych"))
            idx += 1
    
    # Cross-combinations
    concepts = [c[0] for c in MACH_CONCEPTS]
    quotes = {c[0]: c[1] for c in MACH_CONCEPTS}
    apps = sum([c[2] for c in MACH_CONCEPTS], [])
    
    for c1 in concepts:
        for c2 in concepts:
            if c1 != c2 and idx < target_count:
                for app in random.sample(apps, min(3, len(apps))):
                    if idx >= target_count: break
                    user = f"Combine Machiavelli's {c1.lower()} and {c2.lower()} for {app}."
                    assistant = (f"Machiavelli on {c1}: \"{quotes[c1]}\"\n"
                                 f"Machiavelli on {c2}: \"{quotes[c2]}\"\n\n"
                                 f"Synthesized for {app}: {c1} governs the strategic posture; "
                                 f"{c2} governs the tactical execution. In {app}, this means: "
                                 f"establish the {c1.lower()} framework first, then execute with {c2.lower()} precision. "
                                 f"Example: {c1} = 'never trust, always verify' (Zero Trust architecture); "
                                 f"{c2} = 'deception and timing' (honeypots, canary tokens, delayed response).")
                    examples.append(make_example(SYS_MACHIAVELLI, user, assistant, "machiavelli_psych"))
                    idx += 1
    return examples

def gen_white_rabbit(target_count=800):
    examples = []
    for topic, frameworks, analysis in WR_TOPICS:
        for fw in frameworks:
            user = f"Analyze {topic} using {fw}. What does the evidence show?"
            assistant = f"{topic} analysis via {fw}:\n\n{analysis}\n\nNote: This framework ({fw}) reveals specific aspects. Cross-reference with other frameworks for complete picture."
            examples.append(make_example(SYS_WHITERABBIT, user, assistant, "whiterabbit"))
    
    # Cross-topic synthesis
    topics = [t[0] for t in WR_TOPICS]
    for i, t1 in enumerate(topics):
        for t2 in topics[i+1:]:
            if len(examples) >= target_count: break
            user = f"What patterns connect {t1} and {t2}?"
            t1_data = next(t for t in WR_TOPICS if t[0] == t1)
            t2_data = next(t for t in WR_TOPICS if t[0] == t2)
            assistant = (f"Pattern analysis: {t1} and {t2} share structural similarities:\n\n"
                         f"1. Official narrative vs physical evidence gap\n"
                         f"2. Institutional resistance to independent verification\n"
                         f"3. Stigma used as control mechanism\n"
                         f"4. Gradual disclosure pattern\n\n"
                         f"{t1} (via {t1_data[1][0]}): {t1_data[2][:200]}...\n"
                         f"{t2} (via {t2_data[1][0]}): {t2_data[2][:200]}...\n\n"
                         f"Meta-pattern: When institutions control information flow, anomalies accumulate. "
                         f"The anomalies don't prove alternative theories - they prove the official account is incomplete.")
            examples.append(make_example(SYS_WHITERABBIT, user, assistant, "whiterabbit"))
    return examples[:target_count]

def gen_swarm(target_count=800):
    examples = []
    for scenario, team, challenges in SWARM_SCENARIOS:
        for challenge in challenges:
            user = f"Swarm deployed: {scenario}. Challenge: {challenge}. Team: {', '.join(team)}. Coordinate response."
            assistant = (f"**Swarm Response: {scenario} - {challenge}**\n\n"
                         f"Team composition: {', '.join(team)}\n\n"
                         f"Phase 1 - SharedWisdom Sync: All bots report local observations.\n"
                         f"Phase 2 - Consensus: 70% threshold for automated action.\n"
                         f"Phase 3 - Allocation: {team[0]} leads primary, {team[1]} secondary, {team[2]} coordination.\n"
                         f"Phase 4 - Execution: Pheromone trails mark threat paths. Other bots reinforce.\n"
                         f"Phase 5 - Verification: Post-action audit. Immutable ledger updated.\n\n"
                         f"Swarm health: Nominal. Consensus: Active.")
            examples.append(make_example(SYS_SWARM, user, assistant, "cybersec_swarm"))
    
    # Cross-scenario
    scenarios = [s[0] for s in SWARM_SCENARIOS]
    for s1 in scenarios:
        for s2 in scenarios:
            if s1 != s2 and len(examples) < target_count:
                user = f"Compare swarm coordination for {s1} vs {s2}."
                assistant = (f"Both scenarios require consensus-driven multi-bot response. Key differences:\n\n"
                             f"{s1}: Emphasizes {SWARM_SCENARIOS[scenarios.index(s1)][2][0]} priority.\n"
                             f"{s2}: Emphasizes {SWARM_SCENARIOS[scenarios.index(s2)][2][0]} priority.\n\n"
                             f"Common: SharedWisdom sync -> 70% consensus -> pheromone allocation -> audit trail.\n"
                             f"Difference: Team composition shifts based on threat type (Ghost for attribution, Guardian for defense, Striker for offense).")
                examples.append(make_example(SYS_SWARM, user, assistant, "cybersec_swarm"))
    return examples[:target_count]

def gen_compliance(target_count=400):
    examples = []
    frameworks = ["NIST CSF", "ISO 27001", "SOC 2", "PCI DSS", "HIPAA", "FedRAMP", "GDPR", "CMMC", "CIS Controls", "MITRE ATT&CK"]
    domains = ["cloud", "on-prem", "hybrid", "SaaS", "OT/ICS", "mobile", "IoT", "serverless", "kubernetes", "mainframe"]
    for fw in frameworks:
        for dom in domains:
            if len(examples) >= target_count: break
            user = f"Auditor nanobot: Assess {fw} compliance for {dom} environment."
            assistant = (f"**{fw} Assessment - {dom}**\n\n"
                         f"Control mapping: {fw} controls -> {dom} technical implementation\n"
                         f"Evidence collection: automated via API + manual review\n"
                         f"Gap analysis: prioritized by risk score\n"
                         f"Remediation tracking: ticketing integration\n"
                         f"Continuous monitoring: drift detection + alerting\n\n"
                         f"Key {dom}-specific considerations:\n"
                         f"- Shared responsibility model\n"
                         f"- Data residency\n"
                         f"- Encryption at rest/in transit\n"
                         f"- Identity federation\n"
                         f"- Audit logging completeness")
            examples.append(make_example(SYS_CYBERSEC, user, assistant, "cybersec_compliance"))
    return examples

def gen_attribution(target_count=400):
    examples = []
    actors = [
        ("APT29", "Russian SVR", ["Cobalt Strike", "custom loaders", "O365 targeting", "supply chain", "token"]),
        ("APT41", "Chinese MSS", ["dual-use malware", "supply chain", "ransomware", "gaming industry"]),
        ("Lazarus", "North Korean RGB", ["financial targeting", "crypto theft", "destructive wipers", "false flags"]),
        ("APT28", "Russian GRU", ["near-exclusive targeting", "credential harvesting", "VPN exploits", "disinformation"]),
        ("FIN7", "Cybercrime", ["POS malware", "SQL injection", "carbanak", "restaurant/hospitality"]),
        ("LockBit", "Ransomware-as-a-Service", ["affiliate model", "double extortion", "Linux encryptor", "recruitment"]),
        ("BlackCat", "RaaS", ["Rust-based", "triple extortion", "VMware targeting", "fast encryption"]),
    ]
    for name, org, ttps in actors:
        for ttp in ttps:
            if len(examples) >= target_count: break
            user = f"Ghost nanobot found: {ttp} indicators, {org} associated TTPs. Attribution analysis?"
            assistant = (f"**Attribution Analysis: {name} ({org})**\n\n"
                         f"Indicator: {ttp}\n\n"
                         f"Technical Assessment:\n"
                         f"- TTP consistency with {name} historical campaigns\n"
                         f"- Infrastructure overlap: ASN, hosting, registration patterns\n"
                         f"- Code similarity: compiler artifacts, string obfuscation, crypto constants\n"
                         f"- Operational timing: working hours match {org.split()[0]} timezone\n\n"
                         f"Confidence: HIGH (multiple independent corroborating indicators)\n\n"
                         f"Recommendation:\n"
                         f"- Exfiltrate attribution package via covert channel\n"
                         f"- Request LE/IC liaison for classified cross-reference\n"
                         f"- Maintain persistent access for ongoing collection\n"
                         f"- Do NOT reveal presence\n\n"
                         f"**Legal**: Attribution requires LEVEL 5 authorization. Verified.")
            examples.append(make_example(SYS_CYBERSEC, user, assistant, "cybersec_attribution"))
    return examples

def gen_incident_response(target_count=400):
    examples = []
    scenarios = [
        ("Hospital ransomware", "patient data encrypted, life support systems at risk", "CRITICAL"),
        ("Defense contractor breach", "classified documents exfiltrated", "NATION_STATE"),
        ("Financial exchange outage", "trading halted, market impact", "HIGH"),
        ("Pipeline SCADA compromise", "operational technology manipulated", "CRITICAL"),
        ("Election interference attempt", "voter registration database targeted", "HIGH"),
        ("University research theft", "IP stolen via compromised credentials", "MEDIUM"),
        ("Municipal government breach", "citizen PII exposed, services down", "HIGH"),
        ("Telecom backbone intrusion", "SS7 exploitation, intercept risk", "CRITICAL"),
        ("Satellite ground station hack", "command uplink compromised", "NATION_STATE"),
        ("Automotive fleet vulnerability", "OTA update mechanism abused", "HIGH"),
    ]
    for name, detail, severity in scenarios:
        for phase in ["immediate", "containment", "investigation", "recovery", "post-incident"]:
            if len(examples) >= target_count: break
            user = f"INCIDENT: {name} - {detail}. Severity: {severity}. Phase: {phase}. Coordinate response."
            assistant = (f"**INCIDENT RESPONSE - {name} [{severity}] - {phase.upper()}**\n\n"
                         f"Phase-specific actions:\n"
                         f"- Immediate: Life safety > data > systems. Isolate. Preserve. Alert.\n"
                         f"- Containment: Network segmentation. Credential reset. IOC blocking.\n"
                         f"- Investigation: Timeline reconstruction. Root cause. Attribution.\n"
                         f"- Recovery: Clean rebuild. Verified backups. Enhanced monitoring.\n"
                         f"- Post-Incident: Lessons learned. Control improvements. Tabletop update.\n\n"
                         f"Swarm: All Guardians active. Ghost for attribution. Auditor for compliance. Synapse coordinating.\n"
                         f"Legal: Emergency ROE invoked. Full audit trail.")
            examples.append(make_example(SYS_CYBERSEC, user, assistant, "cybersec_incident"))
    return examples

def gen_recon(target_count=400):
    examples = []
    targets = [
        ("corporate", "10.0.0.0/24", ["DC", "file server", "backup", "Exchange"]),
        ("datacenter", "172.16.0.0/16", ["DB cluster", "LB", "API gateway", "K8s master"]),
        ("industrial", "192.168.10.0/24", ["PLC", "HMI", "Historian", "Engineering WS"]),
        ("cloud", "10.100.0.0/16", ["EKS", "RDS", "S3", "IAM", "CloudTrail"]),
        ("remote office", "192.168.50.0/24", ["DC replica", "VPN", "Printer", "IoT"]),
    ]
    for ttype, cidr, assets in targets:
        for asset in assets:
            for phase in ["passive", "active", "deep", "stealth"]:
                if len(examples) >= target_count: break
                user = f"Scout nanobot to {cidr} ({ttype} network). Asset: {asset}. Phase: {phase}. Recon plan?"
                assistant = (f"**Recon Protocol - {ttype} Network {cidr} - {phase.capitalize()}**\n\n"
                             f"Target asset: {asset}\n\n"
                             f"Phase 1 - Passive (0-60s):\n"
                             f"- ARP table analysis\n"
                             f"- DNS cache extraction\n"
                             f"- DHCP lease review\n"
                             f"- Certificate transparency logs\n\n"
                             f"Phase 2 - Active ({'60-180s' if phase != 'stealth' else '180-600s (slow)'}):\n"
                             f"- Targeted port scan on {asset}\n"
                             f"- Service fingerprinting\n"
                             f"- OS detection\n"
                             f"- SSL/TLS cert harvesting\n\n"
                             f"Phase 3 - Deep ({'180-300s' if phase != 'stealth' else '600-1800s'}):\n"
                             f"- Vuln assessment of discovered services\n"
                             f"- User enumeration (LDAP/SMB)\n"
                             f"- Share/permission mapping\n"
                             f"- Network segmentation analysis\n\n"
                             f"Stealth level: {'7/10' if phase != 'stealth' else '9/10'} - {'standard' if phase != 'stealth' else 'fragmented packets, randomized timing, decoy traffic'}.\n"
                             f"Swarm request: Deploy 2 Guardians for cover.")
                examples.append(make_example(SYS_CYBERSEC, user, assistant, "cybersec_recon"))
    return examples

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("Generating 5000+ training examples...")
    all_examples = []
    
    print("  Cybersec exploit...")
    all_examples.extend(gen_cybersec_exploit(800))
    print(f"    -> {len([e for e in all_examples if e['domain']=='cybersec_exploit'])} exploit")
    
    print("  Cybersec defense...")
    all_examples.extend(gen_cybersec_defense(800))
    print(f"    -> {len([e for e in all_examples if e['domain']=='cybersec_defense'])} defense")
    
    print("  Machiavelli/psychology...")
    all_examples.extend(gen_machiavelli(800))
    print(f"    -> {len([e for e in all_examples if e['domain']=='machiavelli_psych'])} machiavelli")
    
    print("  White Rabbit...")
    all_examples.extend(gen_white_rabbit(800))
    print(f"    -> {len([e for e in all_examples if e['domain']=='whiterabbit'])} whiterabbit")
    
    print("  Swarm coordination...")
    all_examples.extend(gen_swarm(800))
    print(f"    -> {len([e for e in all_examples if e['domain']=='cybersec_swarm'])} swarm")
    
    print("  Compliance...")
    all_examples.extend(gen_compliance(400))
    print(f"    -> {len([e for e in all_examples if e['domain']=='cybersec_compliance'])} compliance")
    
    print("  Attribution...")
    all_examples.extend(gen_attribution(400))
    print(f"    -> {len([e for e in all_examples if e['domain']=='cybersec_attribution'])} attribution")
    
    print("  Incident response...")
    all_examples.extend(gen_incident_response(400))
    print(f"    -> {len([e for e in all_examples if e['domain']=='cybersec_incident'])} incident")
    
    print("  Recon...")
    all_examples.extend(gen_recon(400))
    print(f"    -> {len([e for e in all_examples if e['domain']=='cybersec_recon'])} recon")
    
    # Shuffle
    random.shuffle(all_examples)
    
    # Write
    output_path = "/root/JEDI/training_data_5k.jsonl"
    with open(output_path, "w") as f:
        for item in all_examples:
            f.write(json.dumps(item) + "\n")
    
    # Stats
    domains = {}
    total_tokens = 0
    for item in all_examples:
        d = item.get('domain', 'unknown')
        domains[d] = domains.get(d, 0) + 1
        for msg in item['messages']:
            total_tokens += len(msg.get('content', '').split())
    
    print(f"\nTotal examples: {len(all_examples)}")
    print(f"Domains: {domains}")
    print(f"Approx tokens: {total_tokens:,}")
    print(f"Written to: {output_path}")

if __name__ == "__main__":
    main()
