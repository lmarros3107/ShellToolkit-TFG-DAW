from django.db import migrations


NMAP_KNOWLEDGE_ENTRIES = [
    {
        "name": "Nmap Basic Host Discovery",
        "description": "Understand discovery-first workflows with -sn and -Pn, when each is appropriate, and common ICMP probe behavior.",
        "scan_type": "host-discovery",
        "nse_categories": "discovery,safe",
        "extra_flags": "-sn,-Pn",
        "noise_level": "low",
        "lab_notes": (
            "- -sn performs host discovery without a port scan and is useful for quick inventory in scoped ranges.\n"
            "- -Pn skips discovery and treats hosts as up, useful when ICMP is filtered but increases scan time/noise.\n"
            "- Nmap discovery commonly uses ICMP echo/timestamp/address-mask and TCP/ARP probes depending on network context.\n"
            "- Prefer -sn first in labs, then targeted port scans only on confirmed hosts."
        ),
        "is_active": True,
    },
    {
        "name": "Nmap Port Scan Types",
        "description": "Compare TCP and UDP scan modes, stealth characteristics, and privilege requirements for common scan types.",
        "scan_type": "port-scans",
        "nse_categories": "discovery,safe",
        "extra_flags": "-sS,-sT,-sU,-sA,-sN,-sF,-sX",
        "noise_level": "medium",
        "lab_notes": (
            "- -sS (SYN/half-open) is efficient and typically requires elevated privileges.\n"
            "- -sT (TCP connect) uses full OS connect calls; useful without raw socket privileges.\n"
            "- -sU scans UDP services but is slower and can produce open|filtered ambiguity.\n"
            "- -sA helps map firewall rules (stateful filtering) rather than identify open services.\n"
            "- -sN/-sF/-sX may bypass weak stateless filters; reliability varies by target stack."
        ),
        "is_active": True,
    },
    {
        "name": "Nmap Service and Version Detection",
        "description": "Use -sV effectively, tune --version-intensity, and combine service detection with default NSE scripts.",
        "scan_type": "service-detection",
        "nse_categories": "default,discovery,safe",
        "extra_flags": "-sV,--version-intensity,-sC",
        "noise_level": "medium",
        "lab_notes": (
            "- -sV probes discovered ports to fingerprint service software and versions.\n"
            "- --version-intensity 0-9 controls probe aggressiveness: lower is faster, higher is more thorough.\n"
            "- -sC runs default scripts and is commonly paired with -sV for quick contextual enumeration.\n"
            "- Typical lab baseline: nmap -sV -sC --open <target>."
        ),
        "is_active": True,
    },
    {
        "name": "Nmap OS Detection",
        "description": "Perform OS fingerprinting with -O, understand --osscan-guess behavior, and read confidence limits correctly.",
        "scan_type": "os-detection",
        "nse_categories": "discovery,safe",
        "extra_flags": "-O,--osscan-guess",
        "noise_level": "medium",
        "lab_notes": (
            "- -O attempts OS fingerprinting using TCP/IP stack behavior.\n"
            "- Accuracy improves when at least one open and one closed TCP port are visible.\n"
            "- --osscan-guess provides best-effort guesses when confidence is low.\n"
            "- Treat OS output as probabilistic evidence, not absolute truth."
        ),
        "is_active": True,
    },
    {
        "name": "Nmap Output Formats",
        "description": "Capture results in reusable formats and tune verbosity for operator feedback in lab assessments.",
        "scan_type": "output-management",
        "nse_categories": "safe",
        "extra_flags": "-oN,-oX,-oG,-oA,-v,-vv,--open",
        "noise_level": "low",
        "lab_notes": (
            "- -oN writes normal human-readable output.\n"
            "- -oX writes XML suitable for parsing and automation.\n"
            "- -oG writes grepable output for quick shell filtering pipelines.\n"
            "- -oA saves all major formats with a shared basename.\n"
            "- -v/-vv increases runtime detail; --open prints only hosts with open ports."
        ),
        "is_active": True,
    },
    {
        "name": "Nmap Scripting Engine (NSE)",
        "description": "Run NSE scripts by category, pass script arguments, and use high-value discovery checks safely.",
        "scan_type": "nse",
        "nse_categories": "auth,brute,discovery,exploit,safe,vuln",
        "extra_flags": "--script,--script-args,http-title,smb-enum-shares,ftp-anon,ssh-brute",
        "noise_level": "high",
        "lab_notes": (
            "- --script selects scripts by name or category (auth, brute, discovery, exploit, safe, vuln).\n"
            "- --script-args passes parameters required by specific scripts.\n"
            "- Useful educational examples: http-title, smb-enum-shares, ftp-anon, ssh-brute.\n"
            "- Validate script scope and authorization before running intrusive categories."
        ),
        "is_active": True,
    },
    {
        "name": "Nmap Timing Templates",
        "description": "Choose timing templates (-T0..-T5) based on stability, noise budget, and IDS sensitivity in labs.",
        "scan_type": "timing",
        "nse_categories": "safe",
        "extra_flags": "-T0,-T1,-T2,-T3,-T4,-T5",
        "noise_level": "low",
        "lab_notes": (
            "- -T0 paranoid and -T1 sneaky are very slow and reduce burst patterns.\n"
            "- -T2 polite and -T3 normal are balanced defaults for many networks.\n"
            "- -T4 aggressive speeds up scans on stable links.\n"
            "- -T5 insane is fastest but can increase packet loss and false negatives.\n"
            "- Slower timing can help reduce detection probability but increases operation time."
        ),
        "is_active": True,
    },
    {
        "name": "Nmap Firewall and IDS Evasion",
        "description": "Review educational evasion-related flags and understand trade-offs, legality, and detection implications.",
        "scan_type": "evasion",
        "nse_categories": "safe",
        "extra_flags": "-f,--mtu,-D,--source-port,--data-length,-S,--scan-delay",
        "noise_level": "high",
        "lab_notes": (
            "- -f and --mtu fragment packets to test path/device handling.\n"
            "- -D adds decoys to obscure apparent scan origin.\n"
            "- --source-port and --data-length can alter simple filtering heuristics.\n"
            "- -S sets spoofed source IP in advanced scenarios.\n"
            "- --scan-delay spaces probes to reduce burst signatures.\n"
            "- Use strictly in authorized educational environments with explicit approval."
        ),
        "is_active": True,
    },
]


def add_nmap_knowledge(apps, schema_editor):
    NmapProfile = apps.get_model("recon", "NmapProfile")

    for payload in NMAP_KNOWLEDGE_ENTRIES:
        NmapProfile.objects.update_or_create(
            name=payload["name"],
            defaults=payload,
        )


def remove_nmap_knowledge(apps, schema_editor):
    NmapProfile = apps.get_model("recon", "NmapProfile")
    names = [item["name"] for item in NMAP_KNOWLEDGE_ENTRIES]
    NmapProfile.objects.filter(name__in=names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("recon", "0001_initial"),
        ("knowledge", "0002_sessionfavorite"),
    ]

    operations = [
        migrations.RunPython(add_nmap_knowledge, remove_nmap_knowledge),
    ]

