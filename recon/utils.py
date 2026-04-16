SCAN_FLAG_MAP = {
    "basic": ["-sV", "-sC"],
    "stealth": ["-sS"],
    "udp": ["-sU"],
    "vuln": ["-sV", "--script", "vuln"],
    "full": ["-sV", "-sC"],
}

SCAN_EXPLANATIONS = {
    "basic": "Service and default script discovery for baseline host mapping.",
    "stealth": "SYN scan style for lower-noise TCP reconnaissance.",
    "udp": "UDP-focused probing for non-TCP services.",
    "vuln": "Runs vulnerability script category checks.",
    "full": "Covers all TCP ports with service detection.",
}

NSE_NOISE_HINT = {
    "auth": "medium",
    "brute": "high",
    "default": "low",
    "discovery": "low",
    "safe": "low",
    "version": "medium",
    "vuln": "high",
}


def build_nmap_command(cleaned_data):
    target = cleaned_data["target"]
    scan_type = cleaned_data["scan_type"]
    port_mode = cleaned_data["port_mode"]
    custom_ports = cleaned_data.get("custom_ports", "")
    timing = cleaned_data["timing"]
    nse_categories = cleaned_data.get("nse_categories", [])
    extra_flags = cleaned_data.get("extra_flags", "")

    if isinstance(nse_categories, str):
        nse_categories = [nse_categories] if nse_categories else []

    command_parts = ["nmap"]
    explanations = []

    for flag in SCAN_FLAG_MAP.get(scan_type, []):
        command_parts.append(flag)

    explanations.append(SCAN_EXPLANATIONS.get(scan_type, "Custom scan profile."))

    if port_mode == "top100":
        command_parts.extend(["--top-ports", "100"])
        explanations.append("Scans top 100 most common ports.")
    elif port_mode == "top1000":
        command_parts.extend(["--top-ports", "1000"])
        explanations.append("Scans top 1000 most common ports.")
    elif port_mode == "all":
        command_parts.append("-p-")
        explanations.append("Scans all TCP ports.")
    elif port_mode == "custom":
        command_parts.extend(["-p", custom_ports])
        explanations.append("Scans custom port set.")

    command_parts.append(f"-T{timing}")
    explanations.append(f"Timing template set to T{timing}.")

    if nse_categories:
        categories = ",".join(nse_categories)
        command_parts.extend(["--script", categories])
        explanations.append(f"NSE categories enabled: {categories}.")

    if extra_flags:
        command_parts.extend(extra_flags.split())
        explanations.append("Additional validated flags applied.")

    command_parts.append(target)

    command = " ".join(command_parts)
    noise_level = _estimate_noise_level(scan_type, port_mode, nse_categories, timing)

    return {
        "command": command,
        "explanations": explanations,
        "noise_level": noise_level,
    }


def _estimate_noise_level(scan_type, port_mode, nse_categories, timing):
    score = 1

    if scan_type in {"vuln", "full", "udp"}:
        score += 1
    if port_mode in {"all", "custom"}:
        score += 1
    if int(timing) >= 4:
        score += 1

    for category in nse_categories:
        hint = NSE_NOISE_HINT.get(category, "low")
        if hint == "high":
            score += 1
        elif hint == "medium":
            score += 0

    if score <= 1:
        return "low"
    if score <= 3:
        return "medium"
    return "high"

