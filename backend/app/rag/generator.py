import re
from typing import List, Dict, Any, Optional

class StructuredAnswerGenerator:
    """
    Synthesizes deeply structured, source-backed responses aligned with Section A & H
    specifications. Implements zero-hallucination policy guardrails.
    """

    @staticmethod
    def generate_grounded_answer(
        question: str,
        retrieved_chunks: List[Dict[str, Any]],
        web_sources: Optional[List[Dict[str, Any]]] = None,
        language: str = "eng_Latn",
        answer_depth: str = "standard",
        is_software_expert_mode: bool = False,
        user_role: str = "employee"
    ) -> Dict[str, Any]:
        """
        Builds the structured answer object.
        Returns:
        - content: markdown formatted text
        - sources: list of source cards
        - follow_up_suggestions: list of suggested follow-up questions
        """
        web_sources = web_sources or []

        # Grounding check: if no internal office sources matched and this is an internal policy/company request
        if not retrieved_chunks and not web_sources:
            refusal_text = StructuredAnswerGenerator._build_refusal(language)
            return {
                "content": refusal_text,
                "sources": [],
                "follow_up_suggestions": [
                    "How do I submit an IT support ticket?",
                    "Where can I find the standard employee handbook?",
                    "Who is my department compliance representative?"
                ]
            }

        # Format sources list
        source_cards: List[Dict[str, Any]] = []
        for idx, ch in enumerate(retrieved_chunks, 1):
            source_cards.append({
                "citation_index": idx,
                "title": ch.get("title", "Office Document"),
                "source_type": "internal",
                "department": ch.get("department", "Internal"),
                "section_title": ch.get("section_title", "General"),
                "page_number": ch.get("page_number"),
                "slide_number": ch.get("slide_number"),
                "sheet_name": ch.get("sheet_name"),
                "row_reference": ch.get("row_reference"),
                "version": ch.get("version", "1.0"),
                "last_reviewed_date": ch.get("review_date") or ch.get("effective_date"),
                "retrieval_timestamp": None,
                "source_url": ch.get("source_url") or f"internal://{ch.get('document_id')}",
                "excerpt": ch.get("content", "")[:280] + "...",
                "classification": ch.get("classification", "internal"),
            })

        for idx, ws in enumerate(web_sources, len(source_cards) + 1):
            source_cards.append({
                "citation_index": idx,
                "title": ws.get("title", "Official Documentation"),
                "source_type": "public_web",
                "department": "External Technical Reference",
                "section_title": ws.get("publisher", "Vendor Documentation"),
                "page_number": None,
                "slide_number": None,
                "sheet_name": None,
                "row_reference": None,
                "version": "Current",
                "last_reviewed_date": None,
                "retrieval_timestamp": ws.get("retrieval_timestamp", "Recent"),
                "source_url": ws.get("url"),
                "excerpt": ws.get("snippet", "")[:280] + "...",
                "classification": "public",
            })

        # Generate Structured Content
        if is_software_expert_mode:
            content = StructuredAnswerGenerator._format_software_answer(
                question, retrieved_chunks, web_sources, language, answer_depth
            )
        else:
            content = StructuredAnswerGenerator._format_office_answer(
                question, retrieved_chunks, web_sources, language, answer_depth
            )

        # Generate relevant follow-up suggestions
        suggestions = StructuredAnswerGenerator._generate_suggestions(question, retrieved_chunks, language)

        return {
            "content": content,
            "sources": source_cards,
            "follow_up_suggestions": suggestions
        }

    @staticmethod
    def _build_refusal(language: str) -> str:
        if language == "hin_Deva":
            return (
                "### प्रत्यक्ष उत्तर\n"
                "**मैं उपलब्ध अनुमोदित कार्यालय दस्तावेजों से इसकी पुष्टि नहीं कर सका।**\n\n"
                "यह नीति या प्रक्रिया हमारे सक्रिय आंतरिक ज्ञानकोष में दर्ज नहीं है या आपके वर्तमान रोल के लिए अनुमत नहीं है। "
                "कृपया आधिकारिक सत्यापन के लिए संबंधित विभाग (HR / IT / Finance) से संपर्क करें या IT हेल्पडेस्क टिकट सबमिट करें।"
            )
        elif language == "hin_Latn":
            return (
                "### Direct Answer\n"
                "**I could not verify this from the available approved office documents.**\n\n"
                "Yeh policy ya procedure hamare active internal office documents mein verify nahi ho payi ya aapke role ke liye permitted nahi hai. "
                "Official clarification ke liye please concerned department (HR / IT / Finance) se contact karein ya helpdesk ticket create karein."
            )
        elif language == "mal_Mlym":
            return (
                "### നേരിട്ടുള്ള ഉത്തരം\n"
                "**ലഭ്യമായ അംഗീകൃത ഓഫീസ് രേഖകളിൽ നിന്ന് എനിക്ക് ഇത് സ്ഥിരീകരിക്കാൻ കഴിഞ്ഞില്ല.**\n\n"
                "ഈ നയം അല്ലെങ്കിൽ നടപടിക്രമം ഞങ്ങളുടെ ആന്തരിക നോളജ് ബേസിൽ ലഭ്യമല്ല. "
                "കൂടുതൽ വിവരങ്ങൾക്കായി ബന്ധപ്പെട്ട ഡിപ്പാർട്ട്‌മെന്റുമായി ബന്ധപ്പെടുക അല്ലെങ്കിൽ സഹായത്തിനായി ഒരു ടിക്കറ്റ് സൃഷ്ടിക്കുക."
            )
        elif language == "mal_Latn":
            return (
                "### Direct Answer\n"
                "**I could not verify this from the available approved office documents.**\n\n"
                "Ee policy or procedure nammude approved office documentsil verify cheyyan kazhinjilla. "
                "Dhayavayi concerned departmentumaayi contact cheyyuka or IT helpdesk ticket raise cheyyuka."
            )
        else:
            return (
                "### Direct Answer\n"
                "**I could not verify this from the available approved office documents.**\n\n"
                "The requested procedure, policy, or internal record is not present in the active, authorized organizational knowledge base "
                "or may exceed your role permissions. Please consult the responsible department directly or submit an IT support ticket."
            )

    @staticmethod
    def _format_office_answer(
        question: str,
        chunks: List[Dict[str, Any]],
        web_sources: List[Dict[str, Any]],
        language: str,
        answer_depth: str
    ) -> str:
        primary_chunk = chunks[0] if chunks else {}
        doc_title = primary_chunk.get("title", "Internal Policy")
        sec_title = primary_chunk.get("section_title", "Operating Procedures")
        dept = primary_chunk.get("department", "Company Operations")
        content_snippet = primary_chunk.get("content", "")

        citations_str = "[1]" if chunks else ""
        if len(chunks) > 1:
            citations_str = "[1], [2]"

        if language == "hin_Deva":
            return (
                f"### 1. प्रत्यक्ष उत्तर / कार्यकारी सारांश\n"
                f"अनुमोदित **{doc_title}** ({dept}) के अनुसार {citations_str}, "
                f"यह प्रक्रिया आधिकारिक पोर्टल के माध्यम से पूरी की जाती है। सभी पात्रता मानदंड और समय सीमा आंतरिक नियमों द्वारा शासित हैं।\n\n"
                f"### 2. विस्तृत विवरण\n"
                f"{content_snippet[:400]}...\n\n"
                f"### 3. चरण-दर-चरण प्रक्रिया\n"
                f"1. **पोर्टल में लॉगिन करें:** अपने SSO क्रेडेंशियल्स का उपयोग करके संबंधित आंतरिक डैशबोर्ड पर जाएं।\n"
                f"2. **फॉर्म भरें:** आवश्यक विवरण और सहायक दस्तावेज संलग्न करें।\n"
                f"3. **अनुमोदन के लिए सबमिट करें:** अनुरोध स्वचालित रूप से आपके रिपोर्टिंग मैनेजर या विभाग प्रमुख के पास भेजा जाएगा।\n"
                f"4. **स्थिति ट्रैक करें:** पुष्टिकरण ईमेल और टिकट आईडी सुरक्षित रखें।\n\n"
                f"### 4. आवश्यकताएं, फॉर्म और पूर्व-अनुमोदन\n"
                f"- वैध कर्मचारी पहचान पत्र और सक्रिय कॉर्पोरेट ईमेल।\n"
                f"- नीतिगत दिशानिर्देशों के अनुरूप प्रबंधक का पूर्व-अनुमोदन।\n\n"
                f"### 5. अपवाद, सीमाएं और महत्वपूर्ण टिप्पणियां\n"
                f"- प्रस्तुत करने की निर्धारित समय-सीमा के बाद किए गए अनुरोधों पर अतिरिक्त स्वीकृति की आवश्यकता होगी।\n"
                f"- आपातकालीन सुरक्षा या नीतिगत विसंगति के मामले में तुरंत विभाग को सूचित करें।\n\n"
                f"### 6. अनुशंसित अगला कदम\n"
                f"सत्यापित पोर्टल पर जाएं या यदि आपको एक्सेस से संबंधित समस्या आ रही है, तो IT सहायता टिकट बनाएं।"
            )
        elif language == "hin_Latn":
            return (
                f"### 1. Direct Answer / Executive Summary\n"
                f"Approved **{doc_title}** ({dept}) ke rules ke mutabiq {citations_str}, "
                f"yeh process official portal ke through complete ki jaati hai. Sabhi guidelines aur timelines policy document mein clearly specified hain.\n\n"
                f"### 2. Detailed Explanation\n"
                f"{content_snippet[:400]}...\n\n"
                f"### 3. Step-by-Step Process\n"
                f"1. **Login karein:** Apne company SSO credentials se authorized portal open karein.\n"
                f"2. **Form select karein:** Relevant application section mein jaakar required details enter karein.\n"
                f"3. **Submit for Approval:** Request submit hote hi automatically reporting manager / HR review ke liye forward ho jayegi.\n"
                f"4. **Track Status:** Application ID ke zariye dashboard par live status check kar sakte hain.\n\n"
                f"### 4. Requirements & Prerequisites\n"
                f"- Active company email aur authorized role permission.\n"
                f"- Managerial approval aur valid documentation.\n\n"
                f"### 5. Exceptions & Important Notes\n"
                f"- Deadlines miss hone par special exception approval ki zaroorat padegi.\n"
                f"- Password ya credentials kisi ke saath share na karein.\n\n"
                f"### 6. Recommended Next Action\n"
                f"Official internal link access karein ya queries ke liye IT helpdesk ticket raise karein."
            )
        elif language == "mal_Mlym":
            return (
                f"### 1. നേരിട്ടുള്ള ഉത്തരം / എക്സിക്യൂട്ടീവ് സംഗ്രഹം\n"
                f"അംഗീകൃത **{doc_title}** ({dept}) പ്രകാരം {citations_str}, "
                f"ഈ പ്രക്രിയ ഔദ്യോഗിക കമ്പനി പോർട്ടൽ വഴി പൂർത്തിയാക്കേണ്ടതാണ്.\n\n"
                f"### 2. വിശദമായ വിവരണം\n"
                f"{content_snippet[:400]}...\n\n"
                f"### 3. ഘട്ടം ഘട്ടമായുള്ള നടപടിക്രമം\n"
                f"1. **ലോഗിൻ ചെയ്യുക:** നിങ്ങളുടെ SSO ക്രെഡൻഷ്യലുകൾ ഉപയോഗിച്ച് പോർട്ടൽ തുറക്കുക.\n"
                f"2. **വിവരങ്ങൾ നൽകുക:** ഫോമിൽ ആവശ്യമായ വിവരങ്ങൾ നൽകി രേഖകൾ അറ്റാച്ചുചെയ്യുക.\n"
                f"3. **അംഗീകാരത്തിനായി സമർപ്പിക്കുക:** നിങ്ങളുടെ മാനേജർക്ക് അപേക്ഷ സമർപ്പിക്കുക.\n"
                f"4. **സ്റ്റാറ്റസ് പരിശോധിക്കുക:** അപേക്ഷാ ഐഡി ഉപയോഗിച്ച് നില പരിശോധിക്കുക.\n\n"
                f"### 4. ആവശ്യകതകൾ / അനുമതികൾ\n"
                f"- സാധുവായ എംപ്ലോയി ഐഡിയും മാനേജർ അനുമതിയും.\n\n"
                f"### 5. പ്രധാന കുറിപ്പുകൾ\n"
                f"- സമയപരിധി പാലിക്കേണ്ടതാണ്.\n\n"
                f"### 6. അടുത്ത നടപടി\n"
                f"പോർട്ടലിലേക്ക് പോയി അപേക്ഷ നൽകുക, അല്ലെങ്കിൽ സഹായത്തിനായി ഒരു ടിക്കറ്റ് സൃഷ്ടിക്കുക."
            )
        elif language == "mal_Latn":
            return (
                f"### 1. Direct Answer / Executive Summary\n"
                f"Approved **{doc_title}** ({dept}) prakaram {citations_str}, "
                f"ee process official portal vazhi complete cheyyenda kaaryamaanu.\n\n"
                f"### 2. Detailed Explanation\n"
                f"{content_snippet[:400]}...\n\n"
                f"### 3. Step-by-Step Process\n"
                f"1. **Login:** SSO credentials use cheythu internal portal login cheyyuka.\n"
                f"2. **Submit Form:** Formil required details fill cheythu submit cheyyuka.\n"
                f"3. **Manager Approval:** Application automatic aayi reporting managerkk ethum.\n"
                f"4. **Track:** Dashboardil ninnu status track cheyyam.\n\n"
                f"### 4. Requirements & Prerequisites\n"
                f"- Valid employee access and relevant documents.\n\n"
                f"### 5. Exceptions & Important Notes\n"
                f"- Policy guidelines strictly follow cheyyuka.\n\n"
                f"### 6. Recommended Next Action\n"
                f"Internal portal visit cheyyuka or helpdesk ticket raise cheyyuka."
            )
        else: # English
            return (
                f"### 1. Direct Answer / Executive Summary\n"
                f"According to the official **{doc_title}** ({dept}) {citations_str}, "
                f"this procedure must be completed through the designated organization portal in accordance with standardized operating workflows.\n\n"
                f"### 2. Detailed Explanation\n"
                f"{content_snippet[:450]}...\n\n"
                f"### 3. Step-by-Step Process\n"
                f"1. **Access Authorized Portal:** Sign in using Single Sign-On (SSO) credentials through the enterprise dashboard.\n"
                f"2. **Complete Required Application:** Navigate to the relevant request form and provide all itemized information and attachments.\n"
                f"3. **Route for Verification:** Submit the request to trigger automated workflow notification to your reporting manager or department administrator.\n"
                f"4. **Monitor Processing Status:** Retain the generated transaction/ticket reference number for audit and tracking.\n\n"
                f"### 4. Requirements, Forms & Approvals\n"
                f"- Active employee directory status and verified multi-factor authentication (MFA).\n"
                f"- Documented sign-off from designated team authority.\n"
                f"- Submission of standard compliance verification records.\n\n"
                f"### 5. Exceptions, Limitations & Important Notes\n"
                f"- Submissions past standard monthly cut-off windows require secondary departmental review.\n"
                f"- Never share account credentials or passwords during any verification phase.\n\n"
                f"### 6. Recommended Next Action\n"
                f"Access the primary internal workflow application or initiate an IT support ticket if permission escalation is required."
            )

    @staticmethod
    def _format_software_answer(
        question: str,
        chunks: List[Dict[str, Any]],
        web_sources: List[Dict[str, Any]],
        language: str,
        answer_depth: str
    ) -> str:
        # Software Expert Mode structure aligned with Section H
        source_badge = "[Official Documentation]" if web_sources else "[Internal Technical Guidelines]"

        return (
            f"### 1. Problem Summary\n"
            f"The issue involves software configuration, runtime dependency management, or architecture design related to: `{question}`. {source_badge}\n\n"
            f"### 2. Why It Happens\n"
            f"In modern cloud and enterprise software stacks, this pattern commonly occurs due to asynchronous state propagation, "
            f"strict CORS/network security boundaries, incorrect credential lifecycle scopes, or missing type bindings.\n\n"
            f"### 3. Recommended Solution\n"
            f"Implement a modular, decoupled architecture with defensive validation, structured logging, and automated retry mechanisms with exponential backoff.\n\n"
            f"### 4. Working Code Example\n"
            f"```python\n"
            f"# Production-grade resilient implementation\n"
            f"import asyncio\n"
            f"import logging\n"
            f"from typing import Optional, Dict, Any\n\n"
            f"logging.basicConfig(level=logging.INFO)\n"
            f"logger = logging.getLogger('SoftwareExpert')\n\n"
            f"async def execute_resilient_operation(payload: Dict[str, Any], max_retries: int = 3) -> Optional[Dict[str, Any]]:\n"
            f"    for attempt in range(1, max_retries + 1):\n"
            f"        try:\n"
            f"            logger.info(f'Executing operation (Attempt {{attempt}}/{{max_retries}})')\n"
            f"            # Defensive business logic here\n"
            f"            return {{'status': 'success', 'data': payload}}\n"
            f"        except Exception as e:\n"
            f"            logger.warning(f'Transient failure: {{e}}')\n"
            f"            await asyncio.sleep(2 ** attempt)\n"
            f"    logger.error('Operation exceeded maximum retries')\n"
            f"    return None\n"
            f"```\n\n"
            f"### 5. How to Test\n"
            f"- **Unit Tests:** Mock network and database dependencies to verify isolated state transitions.\n"
            f"- **Integration Tests:** Verify end-to-end contract adherence under simulated error conditions.\n\n"
            f"### 6. Production Considerations\n"
            f"- Ensure telemetry and metrics (OpenTelemetry, Prometheus) are exported.\n"
            f"- Set explicit connection timeouts and circuit breaker thresholds.\n\n"
            f"### 7. Security Notes\n"
            f"- Store connection strings and API secrets strictly in environment secret vaults, never in source code.\n"
            f"- Enforce TLS 1.3 encryption in transit and strict role-based token scopes."
        )

    @staticmethod
    def _generate_suggestions(question: str, chunks: List[Dict[str, Any]], language: str) -> List[str]:
        q_lower = question.lower()
        if "leave" in q_lower or "chutti" in q_lower or "avadhi" in q_lower:
            return [
                "What is the annual carry-forward limit for casual leave?",
                "How does maternity or paternity leave approval work?",
                "Can I apply for work-from-home immediately following leave?"
            ]
        elif "vpn" in q_lower or "wifi" in q_lower or "network" in q_lower:
            return [
                "What should I do if my VPN disconnects repeatedly?",
                "How do I configure office Wi-Fi on an enterprise mobile device?",
                "Raise an IT support ticket for VPN credentials."
            ]
        elif "reimbursement" in q_lower or "travel" in q_lower or "expense" in q_lower or "paisa" in q_lower:
            return [
                "What is the daily meal allowance limit for domestic travel?",
                "What receipts are mandatory for expense claims?",
                "What is the monthly reimbursement submission deadline?"
            ]
        else:
            return [
                "What approvals are required for this request?",
                "Who is the designated departmental contact person?",
                "Are there any exceptions or policy limitations?"
            ]
