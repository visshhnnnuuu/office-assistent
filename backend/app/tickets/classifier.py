import re
from typing import Dict, Any, List

INTENT_RULES = [
    ("security_incident", r'\b(phishing|malware|ransomware|hacked|data leak|lost laptop|stolen device|suspicious login|unknown mfa)\b', "critical", True),
    ("password_reset", r'\b(reset password|forgot password|change password|password expired)\b', "medium", False),
    ("account_locked", r'\b(account locked|locked out|too many attempts|unlock account)\b', "high", False),
    ("mfa_issue", r'\b(mfa|2fa|authenticator|duo|okta verify|otp not received)\b', "high", False),
    ("vpn_issue", r'\b(vpn|cisco anyconnect|globalprotect|vpn disconnected|vpn tunnel)\b', "high", False),
    ("wifi_issue", r'\b(wifi|wi-fi|office network|connect to internet|wireless ssid)\b', "high", False),
    ("email_issue", r'\b(outlook|exchange|mail bounce|email not syncing|inbox full)\b', "high", False),
    ("printer_issue", r'\b(printer|printing|paper jam|toner|print queue)\b', "medium", False),
    ("hardware_issue", r'\b(laptop screen|battery swollen|keyboard broken|charger|docking station)\b', "medium", False),
    ("software_installation", r'\b(install|installing|software request|download vscode|license for)\b', "low", False),
    ("software_error", r'\b(app crash|segmentation fault|exception|fatal error|software failed)\b', "medium", False),
    ("access_request", r'\b(request access|grant permission|github repo access|aws role access)\b', "low", False),
    ("asset_request", r'\b(new laptop|external monitor|ergonomic mouse|headset request)\b', "low", False),
    ("ticket_status", r'\b(ticket status|ticket update|check my ticket|status of ticket)\b', "low", False),
    ("general_it_policy", r'\b(it policy|acceptable use|byod policy|password requirements)\b', "low", False),
]

class ITIntentClassifier:
    """
    Evaluates user messages against the 16 canonical IT intents and assigns
    standardized priority levels and triage protocols.
    """

    @staticmethod
    def classify(text: str) -> Dict[str, Any]:
        text_lower = text.lower()

        for intent, pattern, priority, is_security in INTENT_RULES:
            if re.search(pattern, text_lower):
                needs_ticket = intent not in {"general_it_policy", "ticket_status"}
                
                # Check for blocking impact to elevate priority
                if any(w in text_lower for w in ["cannot work", "blocked", "urgent", "production down", "work stopped"]):
                    if priority in {"medium", "low"}:
                        priority = "high"

                required_fields = [
                    "device_type",
                    "operating_system",
                    "error_message",
                    "can_continue_working"
                ]

                guidance = ITIntentClassifier._get_response_guidance(intent, is_security)

                return {
                    "intent": intent,
                    "confidence": 0.94,
                    "priority": priority,
                    "security_incident": is_security,
                    "needs_ticket": needs_ticket,
                    "required_fields": required_fields,
                    "safe_response_guidance": guidance
                }

        # Unknown intent
        return {
            "intent": "unknown",
            "confidence": 0.40,
            "priority": "low",
            "security_incident": False,
            "needs_ticket": False,
            "required_fields": ["device_type", "operating_system", "error_message"],
            "safe_response_guidance": "Provide standard Level-1 clarification or invite the user to describe the IT challenge in more detail."
        }

    @staticmethod
    def _get_response_guidance(intent: str, is_security: bool) -> str:
        if is_security:
            return (
                "URGENT SECURITY WARNING: Instruct the user NOT to click further links, NOT to share credentials or OTPs, "
                "and immediately offer to file an incident ticket directly to the Information Security Operations Center (ISOC)."
            )
        elif intent == "password_reset":
            return "Guide the user to the self-service password reset portal (SSPR). Emphasize that IT staff will never ask for their password."
        elif intent == "vpn_issue":
            return "Advise checking Wi-Fi connectivity, rebooting the VPN client, and verifying MFA push notifications. Never instruct modifying local firewall bypass rules."
        else:
            return "Provide safe Level-1 troubleshooting steps and ask if they would like to raise an IT ticket."
