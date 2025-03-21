from langchain_core.tools import tool
from typing import List, Dict, Any
from datetime import datetime
import re
import uuid
from datetime import datetime, timedelta

#######################    Functions
def generate_ticket(category: str, urgency_level: str = "normal", email_content: str = "") -> Dict[str, Any]:
    """
    Generate a support ticket with metadata based on category and urgency.
    
    :param category: The category of the ticket (e.g., "Complaint", "Support", "Account Access")
    :type category: str
    :param urgency_level: The urgency level ("urgent" or "normal")
    :type urgency_level: str
    :param email_content: Optional email content for additional classification
    :type email_content: str
    :return: A dictionary containing ticket information
    :rtype: Dict[str, Any]
    """
    # Generate ticket number with date prefix and unique ID
    ticket_number = f"{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
    
    # Set response time and team based on urgency
    if urgency_level == "urgent":
        response_time = timedelta(hours=4)
        assigned_team = "senior customer relations team"
    else:
        response_time = timedelta(hours=24)
        assigned_team = "customer service team"
    
    # Calculate estimated response datetime
    current_time = datetime.now()
    estimated_response = current_time + response_time
    
    # Subcategory detection (refine based on email content if provided)
    subcategory = "General"
    if email_content:
        if re.search(r"damaged|broken|defective", email_content.lower()):
            subcategory = "Product Quality"
        elif re.search(r"refund|return|money back", email_content.lower()):
            subcategory = "Refund Request"
        elif re.search(r"delivery|shipping|late|delay", email_content.lower()):
            subcategory = "Shipping Issue"
        elif re.search(r"wrong|incorrect|not ordered", email_content.lower()):
            subcategory = "Order Error"
        elif re.search(r"login|password|account", email_content.lower()):
            subcategory = "Account Access"
        elif re.search(r"error|crash|bug", email_content.lower()):
            subcategory = "Technical Error"
        elif re.search(r"install|download|setup", email_content.lower()):
            subcategory = "Installation"
        elif re.search(r"payment|invoice|billing|charge", email_content.lower()):
            subcategory = "Billing"
    
    # Create ticket object
    ticket = {
        "ticket_number": ticket_number,
        "category": category,
        "subcategory": subcategory,
        "urgency": urgency_level,
        "status": "open",
        "created_at": current_time.isoformat(),
        "estimated_response": estimated_response.isoformat(),
        "assigned_to": assigned_team,
        "response_time_hours": response_time.total_seconds() / 3600
    }
    
    return ticket

def classify_urgency(email_content: str) -> str:
    """
    Classify the urgency level of an email based on its content.
    
    :param email_content: The body of the email
    :type email_content: str
    :return: Urgency level ("urgent" or "normal")
    :rtype: str
    """
    urgent_keywords = [
        "urgent", "emergency", "immediately", "asap", "critical",
        "production down", "blocked", "can't work", "deadline", 
        "urgent request", "furious", "extremely disappointed",
        "legal action", "attorney", "lawyer", "sue", "lawsuit",
        "refund immediately", "cancellation", "damaged", "safety issue"
    ]
    
    # Check for urgent keywords
    if any(keyword in email_content.lower() for keyword in urgent_keywords):
        return "urgent"
    
    # Check for phrases that might indicate urgency
    urgent_phrases = [
        "need this resolved today",
        "waiting for days",
        "unacceptable service",
        "speak to a manager",
        "deadline is today",
        "extremely frustrated",
        "this is urgent",
        "fix it now",
        "can't wait any longer",
        "immediate attention required",
        "time is running out",
        "escalate this immediately",
        "completely unacceptable",
        "resolve this ASAP",
        "no more delays",
        "critical issue"
        ]
    
    if any(phrase in email_content.lower() for phrase in urgent_phrases):
        return "urgent"
        
    return "normal"

def format_response_with_ticket(response: str, ticket: Dict[str, Any]) -> str:
    """
    Format a response to include ticket information.
    
    :param response: The base response text
    :type response: str
    :param ticket: The ticket dictionary
    :type ticket: Dict[str, Any]
    :return: The formatted response with ticket information
    :rtype: str
    """
    # Add ticket-specific information to response
    response_time_hours = int(ticket["response_time_hours"])
    
    if ticket["urgency"] == "urgent":
        urgency_text = (
            f"\nWe understand your concern requires immediate attention and have marked it as URGENT. "
            f"Your case has been escalated to our {ticket['assigned_to']} and someone will contact you within {response_time_hours} hours. "
        )
    else:
        urgency_text = ""
    
    # Format the closing with ticket information
    closing = (
        f"{urgency_text}\n"
        f"Your reference ticket number is #{ticket['ticket_number']}. Please mention this number in any future communications about this matter. "
        f"A member of our {ticket['assigned_to']} will be in touch within {response_time_hours} hours. "
    )
    
    if ticket["urgency"] == "urgent":
        closing += "For immediate assistance, please call our priority line at 555-776-2323."
    else:
        closing += "If you need immediate assistance, please call our support line at 555-776-2323."
    
    # Add closing to response
    return response + closing

#######################    Tools for Email Classification and Response Generationtools
@tool
def classify_email_content() -> List[str]:
    """
    Returns the valid categories for email classification.
    The ReAct agent can use these categories to classify incoming emails.
    
    :return: List of valid email categories
    :rtype: List[str]
    """
    return ["complaint", "inquiry", "feedback", "support_request", "other"]


@tool 
def handle_complaint(email_content: str) -> Dict[str, Any]:
    """
    Returns a template response for complaint emails and generates a ticket.
    
    :param email_content: The body of the email
    :type email_content: str
    :return: A dictionary containing the response and ticket information
    :rtype: Dict[str, Any]
    :raises TypeError: If email_content is not a string
    """
    if not isinstance(email_content, str):
        raise TypeError("email_content must be a string")
    
    # Classify urgency
    urgency_level = classify_urgency(email_content)
    
    # Base template
    response = (
        "Thank you for reaching out to us. We sincerely apologize for the inconvenience you've experienced. "
        "At [!!Company Name!!], we take such matters seriously and are committed to resolving them promptly. "
    )
    
    # Detect issue type for personalization
    if "damaged" in email_content.lower() or "broken" in email_content.lower():
        response += (
            "We understand that you received a damaged product, which is unacceptable. "
            "We will process a replacement or refund immediately. "
            "Could you please provide any photos of the damage if available? "
        )
    elif "refund" in email_content.lower():
        response += (
            "We understand you're requesting a refund. "
            "We'll review your request right away and process it according to our policy. "
            "Please allow 3-5 business days for the refund to appear in your account once processed. "
        )
    elif "delivery" in email_content.lower() or "shipping" in email_content.lower():
        response += (
            "We understand there was an issue with your delivery. "
            "We'll look into the status of your order immediately and provide you with an update. "
        )
    else:
        response += (
            "Based on your message, we understand there was an issue with your experience. "
            "Please rest assured that we are investigating this matter. "
        )
    
    # Generate ticket
    ticket = generate_ticket("Complaint", urgency_level, email_content)
    
    # Format response with ticket information
    formatted_response = format_response_with_ticket(response, ticket)
    
    return {
        "response": formatted_response,
        "ticket": ticket,
        "urgency_level": urgency_level
    }

@tool 
def handle_inquiry(email_content: str) -> str:
    """
    Returns a template response for inquiry emails based on their content.
    
    This tool generates a standardized but partially personalized response 
    for customer inquiries that the agent can use directly or further refine.

    :param email_content: The body of the email
    :type email_content: str
    :return: A templated response for the inquiry
    :rtype: str
    :raises TypeError: If email_content is not a string
    """
    if not isinstance(email_content, str):
        raise TypeError("email_content must be a string")
    
    # Base template
    response = (
        "Thank you for your interest in our products and services at [!!Company Name!!]. "
        "We appreciate you taking the time to reach out to us. "
    )
    
    # Detect inquiry type for personalization
    if "price" in email_content.lower() or "cost" in email_content.lower():
        response += (
            "Regarding your pricing inquiry, we offer several options tailored to different needs. "
            "Our standard package starts at $X per month, while our premium solutions range from $Y to $Z "
            "depending on the features required. "
            "We'd be happy to provide a personalized quote based on your specific requirements. "
        )
    elif "compatibility" in email_content.lower() or "work with" in email_content.lower() or "compatible" in email_content.lower():
        response += (
            "Regarding your compatibility question, our products are designed to work with most standard systems. "
            "We support Windows, macOS, and Linux operating systems with our software solutions. "
            "For hardware compatibility, we recommend checking the detailed specifications on our website. "
        )
    elif "availability" in email_content.lower() or "in stock" in email_content.lower():
        response += (
            "Regarding product availability, we currently have most items in stock with typical shipping times of 2-3 business days. "
            "Some specialty items may require additional processing time. "
            "We can check the specific availability of any item you're interested in. "
        )
    else:
        response += (
            "We've received your inquiry and would like to provide you with the most accurate information. "
            "To better assist you, we may need additional details about your specific needs. "
        )
    
    # Common closing for all inquiry responses
    response += (
        "If you have any further questions or need additional information, please don't hesitate to let us know. "
        "Our team is available Monday through Friday, 9 AM to 6 PM ET to assist you. "
        "We look forward to helping you find the perfect solution for your needs."
    )
    
    return response

@tool 
def handle_support_request(email_content: str) -> dict:
    """
    Returns a template response for technical support requests and generates a ticket.
    
    :param email_content: The body of the email
    :type email_content: str
    :return: A dictionary containing the response and ticket information
    :rtype: Dict[str, Any]
    :raises TypeError: If email_content is not a string
    """
    if not isinstance(email_content, str):
        raise TypeError("email_content must be a string")
    
    # Classify urgency
    urgency_level = classify_urgency(email_content)
    
    # Base template
    response = (
        "Thank you for contacting [!!Company Name!!] Support. "
        "We're here to help you resolve any technical issues you're experiencing. "
    )
    
    # Detect support issue type for personalization
    if "login" in email_content.lower() or "password" in email_content.lower() or "account" in email_content.lower():
        response += (
            "Regarding your account access issue, we recommend the following steps:\n\n"
            "1. Try resetting your password through the 'Forgot Password' link on our login page\n"
            "2. Clear your browser cache and cookies\n"
            "3. Ensure you're using the correct email address associated with your account\n\n"
            "If you continue to experience issues after trying these steps, we can assist with a manual account recovery. "
        )
    elif "error" in email_content.lower() or "crash" in email_content.lower() or "bug" in email_content.lower():
        response += (
            "We understand you're experiencing an error with our software. "
            "To help us diagnose this issue more effectively, could you please provide the following information?\n\n"
            "1. The exact error message you're seeing (a screenshot would be helpful)\n"
            "2. The steps you were taking when the error occurred\n"
            "3. Your device type and operating system version\n"
            "4. The version of our software you're using\n\n"
            "This information will help our technical team identify and resolve the issue more quickly. "
        )
    elif "install" in email_content.lower() or "download" in email_content.lower() or "setup" in email_content.lower():
        response += (
            "Regarding your installation question, our software can be installed by following these general steps:\n\n"
            "1. Download the latest version from our website's download section\n"
            "2. Run the installer and follow the on-screen instructions\n"
            "3. Enter your license key when prompted (found in your purchase confirmation email)\n"
            "4. Complete the setup and restart your computer if prompted\n\n"
            "For more detailed instructions, please visit our installation guide at [Website]/support/installation. "
        )
    else:
        response += (
            "We've received your support request and would like to help you resolve your issue as quickly as possible. "
            "To better assist you, our technical support team may need additional information about the problem you're experiencing. "
        )
    
    # Generate ticket
    ticket = generate_ticket("Support", urgency_level, email_content)
    
    # Format response with ticket information
    formatted_response = format_response_with_ticket(response, ticket)
    
    return {
        "response": formatted_response,
        "ticket": ticket,
        "urgency_level": urgency_level
    }

@tool 
def handle_feedback(email_content: str) -> str:
    """
    Returns a template response for feedback emails based on their content.
    
    This tool generates a standardized but partially personalized response 
    for customer feedback that the agent can use directly or further refine.

    :param email_content: The body of the email
    :type email_content: str
    :return: A templated response for the feedback
    :rtype: str
    :raises TypeError: If email_content is not a string
    """
    if not isinstance(email_content, str):
        raise TypeError("email_content must be a string")
    
    # Base template
    response = (
        "Thank you for taking the time to share your feedback with [!!Company Name!!]. "
        "We genuinely appreciate hearing from our customers as it helps us improve our products and services. "
    )
    
    # Detect feedback type for personalization
    if any(word in email_content.lower() for word in ["great", "excellent", "love", "awesome", "thank", "appreciate"]):
        response += (
            "We're thrilled to hear about your positive experience with our products/services! "
            "It's wonderful customers like you who inspire us to continue delivering excellence. "
            "We've shared your kind words with our team, who were equally delighted to receive your feedback. "
        )
    elif any(word in email_content.lower() for word in ["improve", "suggestion", "could be better", "enhance"]):
        response += (
            "We value your suggestions for how we can improve our offerings. "
            "Your insights are incredibly helpful and will be carefully considered as we continue to enhance our products and services. "
            "We've forwarded your specific recommendations to our product development team for review. "
        )
    elif any(word in email_content.lower() for word in ["feature", "add", "include", "missing"]):
        response += (
            "Thank you for your feature suggestion. We're always looking for ways to make our products more useful and intuitive for our customers. "
            "Your idea has been logged in our feature request system and will be evaluated by our product team for potential inclusion in future updates. "
            "We appreciate you taking the time to help us improve. "
        )
    else:
        response += (
            "We've carefully noted your feedback and will take it into consideration as we continue to improve our offerings. "
            "Hearing directly from customers like you provides valuable insights that help shape our future direction. "
        )
    
    # Common closing for all feedback responses
    response += (
        "Your input is invaluable to us as we strive to deliver the best possible experience for our customers. "
        "If you have any additional thoughts or suggestions in the future, please don't hesitate to reach out again. "
        "We're committed to continuously improving and we thank you for being part of that journey."
    )
    
    return response

@tool 
def handle_other(email_content: str) -> str:
    """
    Returns a context-aware response for emails that don't fit into standard categories.
    
    This tool generates a personalized and professional response for emails that 
    don't clearly fall into complaint, inquiry, support request, or feedback categories.
    It attempts to identify the general topic and tailors the response accordingly.

    :param email_content: The body of the email
    :type email_content: str
    :return: A tailored response for the email
    :rtype: str
    :raises TypeError: If email_content is not a string
    """
    if not isinstance(email_content, str):
        raise TypeError("email_content must be a string")
    
    # Extract potential name for personalization
    import re
    name_match = re.search(r'[Ff]rom:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)|[Mm]y name is\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', email_content)
    greeting = "Thank you for reaching out to [!!Company Name!!]. "
    if name_match:
        name = name_match.group(1) or name_match.group(2)
        greeting = f"Hello {name},\n\nThank you for reaching out to [!!Company Name!!]. "
    
    # Dictionary of topic keywords and their corresponding responses
    topic_responses = {
        "partnership": {
            "keywords": ["partnership", "collaborate", "opportunity", "proposal", "joint venture", "alliance"],
            "response": (
                "We're always interested in exploring potential partnerships and collaboration opportunities. "
                "To help us evaluate your proposal more effectively, could you please provide:\n"
                "• The nature of the collaboration you're proposing\n"
                "• How you envision our organizations working together\n"
                "• Any specific goals or outcomes you have in mind\n"
                "• Timeline and resource considerations\n\n"
                "Our partnerships team will review your proposal and get back to you with next steps."
            )
        },
        "career": {
            "keywords": ["job", "career", "position", "employment", "hire", "hiring", "resume", "cv", "vacancy"],
            "response": (
                "Regarding your employment-related inquiry, we'd recommend visiting our careers page at [Website]/careers "
                "for information about current openings and our application process.\n\n"
                "All available positions are listed there, along with the required qualifications and application instructions. "
                "If you're interested in a specific department or role that isn't currently listed, "
                "you're welcome to submit your resume to [careers@company.com] for future consideration."
            )
        },
        "media": {
            "keywords": ["press", "media", "interview", "journalist", "publication", "news", "coverage"],
            "response": (
                "For press and media inquiries, our communications team would be happy to assist you. "
                "Please provide the following details so we can better help you:\n"
                "• The name of your publication or media outlet\n"
                "• The specific topic you're interested in covering\n"
                "• Any deadlines you're working with\n\n"
                "We'll connect you with the appropriate spokesperson or provide the information you need."
            )
        },
        "investor": {
            "keywords": ["investor", "investment", "shareholder", "stock", "financial", "dividend", "annual report"],
            "response": (
                "Thank you for your interest in [Company Name] from an investment perspective. "
                "Our investor relations team can provide you with the information you need. "
                "Please visit our investor relations portal at [Website]/investors for access to our "
                "financial reports, earnings calls, and upcoming events. "
                "For specific inquiries, please email [investor.relations@company.com]."
            )
        },
        "event": {
            "keywords": ["event", "conference", "webinar", "workshop", "speaking", "sponsor", "presentation"],
            "response": (
                "Thank you for your message regarding our events or speaking opportunities. "
                "Our events team would be happy to discuss this further with you. "
                "Could you please provide more details about the event, including dates, location, "
                "expected audience, and the specific nature of your request? "
                "This will help us determine the most appropriate response."
            )
        },
        "donation": {
            "keywords": ["donation", "charity", "fundraising", "nonprofit", "sponsor", "philanthropic"],
            "response": (
                "Thank you for considering [!!Company Name!!] for your charitable initiative. "
                "We have a structured process for reviewing donation and sponsorship requests. "
                "Please visit [!!Company Name!!].ai/community for information on our corporate social responsibility "
                "initiatives and the application process for charitable support. "
                "Alternatively, you can email your proposal to [!!Company Name!!].community@company.com."
            )
        },
        "service_update": {
            "keywords": ["service update", "municipal service", "city service", "web service", "api", "maintenance", 
                         "downtime", "outage", "upgrade", "system update", "service change", "improvements"],
            "response": (
                "We received your notification regarding service updates. "
                "We appreciate your feedback and will review the information provided. "
                "Our technical team will assess the impact of these changes on our services "
                "and communicate any necessary updates to our users."
                
            )
        },
        "invoice_billing": {
            "keywords": ["invoice", "billing", "payment", "charge", "subscription", "receipt", "statement", 
                         "account", "refund", "credit", "debit", "transaction", "price", "cost", "fee"],
            "response": (
                "Thank you for reaching out regarding your billing or invoice inquiry. "
                "Our billing department is available to assist you with any questions related to your account. "
                "To help us address your specific inquiry more efficiently, please provide:\n\n"
                "• Your account number or customer ID\n"
                "• The invoice number(s) in question, if applicable\n"
                "• The specific details of your billing concern\n\n"
                "For immediate access to your billing information, you can log into your account dashboard at [Website]/account "
                "where you can view past invoices, payment history, and manage your payment methods.\n\n"
                "If you're experiencing difficulty with a payment or believe there's an error on your invoice, "
                "please let us know and we'll investigate promptly."
            )
        }
    }
    
    # Check for topic matches
    for topic, data in topic_responses.items():
        if any(keyword in email_content.lower() for keyword in data["keywords"]):
            response = greeting + data["response"]
            break
    else:
        # Default response if no specific topic is identified
        response = greeting + (
            "We've received your message and would like to ensure it gets directed to the right department. "
            "Could you please provide a bit more information about the nature of your inquiry? "
            "This will help us route your message to the team best equipped to assist you.\n\n"
            "In the meantime, you might find answers to common questions in our FAQ section at [Website]/faq."
        )
    
    # Attempt to identify urgency
    urgent_words = ["urgent", "immediately", "asap", "emergency", "critical", "deadline", "time-sensitive"]
    if any(word in email_content.lower() for word in urgent_words):
        urgent_note = (
            "\n\nWe understand your matter may be time-sensitive. "
            "For immediate assistance, please call us directly at [Main_Phone_Number] during our business hours: "
            "Monday through Friday, 9 AM to 6 PM ET."
        )
        response += urgent_note
    
    # Common closing for all responses
    closing = (
        "\n\nA member of our team will review your message and follow up as soon as possible, typically within 1-2 business days. "
        "Thank you for your patience and for choosing [Company Name].\n\n"
        "Best regards,\n"
        "[Company Name] Customer Support Team"
    )
    
    return response + closing

