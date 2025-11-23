# security_analysis.py

from dataclasses import dataclass
from typing import List
from architecture_model import Architecture, Component


@dataclass
class SecurityRisk:
    component: str
    risk_type: str
    severity: str     # "Low", "Medium", "High"
    description: str
    suggestion: str


def analyze_security(arch: Architecture) -> List[SecurityRisk]:
    risks: List[SecurityRisk] = []
    seen = set()  # to avoid duplicates

    for comp in arch.components.values():

        # Rule 1: Public-facing service/gateway -> DoS risk
        if comp.public and comp.ctype in {"gateway", "service", "web_client"}:
            key = (comp.name, "DoS")
            if key not in seen:
                seen.add(key)
                risks.append(SecurityRisk(
                    component=comp.name,
                    risk_type="Denial-of-Service",
                    severity="High",
                    description=(
                        f"{comp.name} is a public-facing {comp.ctype}. "
                        "It may be vulnerable to traffic floods (DoS/DDoS) if not protected."
                    ),
                    suggestion=(
                        "Implement rate limiting, request throttling, and possibly a Web Application Firewall (WAF). "
                        "Monitor traffic patterns and add alerting for abnormal spikes."
                    ),
                ))

        # Rule 2: Public database
        if comp.public and comp.ctype == "database":
            key = (comp.name, "Data Exposure")
            if key not in seen:
                seen.add(key)
                risks.append(SecurityRisk(
                    component=comp.name,
                    risk_type="Data Exposure",
                    severity="High",
                    description=(
                        f"{comp.name} is a database flagged as public. "
                        "Databases should never be directly exposed to the internet."
                    ),
                    suggestion=(
                        "Place the database in a private subnet and restrict access via application services only."
                    ),
                ))

        # Rule 3: External API dependency
        if comp.ctype == "external_api":
            key = (comp.name, "External API")
            if key not in seen:
                seen.add(key)
                risks.append(SecurityRisk(
                    component=comp.name,
                    risk_type="External Dependency Risk",
                    severity="Medium",
                    description=(
                        f"{comp.name} depends on an external API which may fail, be rate limited, or compromised."
                    ),
                    suggestion=(
                        "Implement timeouts, retries with backoff, and fallback strategies. "
                        "Cache responses where possible and handle failures gracefully."
                    ),
                ))

    return risks

