"""
University Library Chatbot (Smart Rule-Based)
---------------------------------------------
A smart chatbot that answers library-related questions using:
- Case-insensitive matching (HELLO = hello = Hello)
- Punctuation-tolerant matching
- Fuzzy matching (handles typos like "helo" → "hello")
- Stricter matching for short keywords (avoids "book" → "ebook")
- Keyword scoring system
- Smart fallback responses

Built with:
- Python 3.10+
- Flask (Web Framework)
"""

from flask import Flask, render_template, request, jsonify
import re
from difflib import SequenceMatcher

app = Flask(__name__)

# ============================================================
# KNOWLEDGE BASE
# ============================================================
# Order matters: earlier entries win ties.
# ============================================================

KNOWLEDGE_BASE = [
    # ---------- HELP (must be first) ----------
    {
        "topic": "help",
        "keywords": [
            "help", "topics", "what can you do", "options",
            "menu", "commands", "assist", "support",
        ],
        "response": (
            "🤖 I can help you with:\n"
            "• 🕐 Opening hours\n"
            "• 📖 Borrowing & returning books\n"
            "• 🔄 Renewing books\n"
            "• 🔍 Searching for books\n"
            "• 💰 Fines & policies\n"
            "• 🏫 Study rooms\n"
            "• 📶 Wi-Fi & printing\n"
            "• 🪪 Membership\n"
            "• 📱 E-Books\n"
            "• 🎓 Tutoring\n"
            "• 📝 Research help\n"
            "• 📞 Contact info\n\n"
            "Just type your question!"
        ),
    },
    # ---------- GREETINGS ----------
    {
        "topic": "greeting",
        "keywords": [
            "hello", "hi", "hey", "greetings", "salam", "hola",
            "helo", "hllo", "hlo", "hii", "heyy", "heyyy",
            "heelo", "heello", "helloo",
            "good morning", "good evening", "good afternoon",
            "howdy", "yo", "sup", "whats up",
        ],
        "response": "👋 Hello! I'm your library assistant. How can I help you today?",
    },
    # ---------- THANKS ----------
    {
        "topic": "thanks",
        "keywords": [
            "thanks", "thank you", "appreciate", "shukran",
            "thx", "ty", "grateful", "thank u", "thanx",
        ],
        "response": "😊 You're welcome! Happy to help anytime.",
    },
    # ---------- GOODBYE ----------
    {
        "topic": "goodbye",
        "keywords": [
            "bye", "goodbye", "see you", "later", "farewell",
            "take care", "cya", "see ya", "peace",
        ],
        "response": "👋 Goodbye! Have a great day and happy reading!",
    },
    # ---------- OPENING HOURS ----------
    {
        "topic": "hours",
        "keywords": [
            "hour", "hours", "open", "opening", "close", "closing",
            "time", "timing", "timings", "schedule", "working",
            "operation",
        ],
        "response": (
            "📚 The library is open:\n"
            "• Sunday – Thursday: 8:00 AM – 8:00 PM\n"
            "• Saturday: 10:00 AM – 6:00 PM\n"
            "• Friday: Closed"
        ),
    },
    # ---------- RENEWAL ----------
    {
        "topic": "renewal",
        "keywords": [
            "renew", "renewal", "extend", "extension", "renewing",
            "renu", "renow", "extend book",
        ],
        "response": (
            "🔄 To renew a book:\n"
            "1. Log in to the library portal: library.university.edu\n"
            "2. Go to 'My Loans'.\n"
            "3. Click 'Renew' next to the book.\n"
            "4. You can renew up to 2 times (14 days each).\n"
            "⚠️ Renewal is not allowed if the book is reserved by another user."
        ),
    },
    # ---------- BORROWING ----------
    {
        "topic": "borrow",
        "keywords": [
            "borrow", "borrowing", "loan", "checkout", "check out",
            "take out", "issue", "borow", "borow book", "get a book",
        ],
        "response": (
            "📖 To borrow a book:\n"
            "1. Bring your university ID card.\n"
            "2. Go to the circulation desk.\n"
            "3. You can borrow up to 5 books for 14 days.\n"
            "4. Renew online via the library portal."
        ),
    },
    # ---------- RETURNING ----------
    {
        "topic": "return",
        "keywords": [
            "return", "returning", "give back", "bring back",
            "due", "drop off", "drop box", "retun", "retrn",
        ],
        "response": (
            "🔄 To return a book:\n"
            "• Use the drop box at the entrance.\n"
            "• Or hand it to the librarian at the circulation desk.\n"
            "• Late returns incur a fine of $1 per day."
        ),
    },
    # ---------- SEARCHING ----------
    {
        "topic": "search",
        "keywords": [
            "search", "find", "look for", "looking for",
            "catalog", "catalogue", "book on", "locate",
            "serch", "fnd",
        ],
        "response": (
            "🔍 To search for a book:\n"
            "1. Visit the library catalog: catalog.university.edu\n"
            "2. Search by title, author, or ISBN.\n"
            "3. Note the shelf location and call number.\n"
            "Need help? Ask a librarian!"
        ),
    },
    # ---------- FINES ----------
    {
        "topic": "fines",
        "keywords": [
            "fine", "fines", "penalty", "penalties", "late",
            "fee", "fees", "charge", "charges", "payment",
            "fne", "finee",
        ],
        "response": (
            "💰 Fines:\n"
            "• Late return: $1 per day per book.\n"
            "• Lost book: Full replacement cost + $10 processing fee.\n"
            "• Damaged book: $5 – $50 depending on damage."
        ),
    },
    # ---------- STUDY ROOMS ----------
    {
        "topic": "study_rooms",
        "keywords": [
            "study room", "study rooms", "studyrom", "studyroom",
            "booking", "book a room", "reserve", "reservation",
            "meeting room", "quiet room", "group room",
        ],
        "response": (
            "🏫 Study Rooms:\n"
            "• Available on the 2nd floor.\n"
            "• Book online at library.university.edu/rooms.\n"
            "• Maximum 4 hours per session."
        ),
    },
    # ---------- WI-FI ----------
    {
        "topic": "wifi",
        "keywords": [
            "wifi", "wi-fi", "internet", "network", "connection",
            "wireless", "wify", "wi fi",
        ],
        "response": (
            "📶 Free Wi-Fi is available throughout the library.\n"
            "Network: UniversityLibrary\n"
            "Password: Ask at the front desk."
        ),
    },
    # ---------- PRINTING ----------
    {
        "topic": "printing",
        "keywords": [
            "print", "printer", "printing", "copy", "copying",
            "scan", "scanning", "photocopy", "xerox",
            "prnt", "printr",
        ],
        "response": (
            "🖨️ Printing Services:\n"
            "• Located on the 1st floor.\n"
            "• Black & white: $0.10 per page.\n"
            "• Color: $0.50 per page.\n"
            "• Scanning is free."
        ),
    },
    # ---------- MEMBERSHIP ----------
    {
        "topic": "membership",
        "keywords": [
            "membership", "member", "join", "register",
            "registration", "card", "sign up", "subscribe",
            "membershp", "membrship",
        ],
        "response": (
            "🪪 Library Membership:\n"
            "• Free for all university students and staff.\n"
            "• Bring your ID to the front desk.\n"
            "• Your student card doubles as your library card."
        ),
    },
    # ---------- CONTACT ----------
    {
        "topic": "contact",
        "keywords": [
            "contact", "phone", "email", "reach", "call",
            "number", "address", "location",
            "contct", "emal", "phon",
        ],
        "response": (
            "📞 Contact Us:\n"
            "• Phone: +1 (555) 123-4567\n"
            "• Email: library@university.edu\n"
            "• Website: library.university.edu"
        ),
    },
    # ---------- E-BOOKS (بدون "online book") ----------
    {
        "topic": "ebooks",
        "keywords": [
            "ebook", "ebooks", "e-book", "e-books",
            "digital book", "pdf", "kindle",
        ],
        "response": (
            "📱 E-Books:\n"
            "• Access thousands of e-books at ebook.university.edu.\n"
            "• Login with your student ID.\n"
            "• Available 24/7."
        ),
    },
    # ---------- TUTORING (بدون "help") ----------
    {
        "topic": "tutoring",
        "keywords": [
            "tutor", "tutoring", "study group",
            "study help", "academic support",
            "tutr", "tutring",
        ],
        "response": (
            "🎓 Tutoring Services:\n"
            "• Free tutoring for all students.\n"
            "• Schedule at library.university.edu/tutoring.\n"
            "• Subjects: Math, Science, Writing, and more."
        ),
    },
    # ---------- RESEARCH HELP ----------
    {
        "topic": "research",
        "keywords": [
            "research", "citation", "cite", "apa", "mla",
            "chicago", "reference", "bibliography",
            "reserch", "citatoin",
        ],
        "response": (
            "📝 Research Help:\n"
            "• Citation guides available at the front desk.\n"
            "• APA, MLA, Chicago styles supported.\n"
            "• Ask a librarian for personalized help."
        ),
    },
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize_text(text: str) -> str:
    """
    Convert text to lowercase, remove punctuation, and strip extra spaces.
    """
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def fuzzy_ratio(a: str, b: str) -> float:
    """Return similarity ratio between two strings (0 to 1)."""
    return SequenceMatcher(None, a, b).ratio()


def keyword_matches(keyword: str, message: str, threshold: float = 0.75) -> bool:
    """
    Check if a keyword matches the message.
    - Exact substring match OR
    - Fuzzy match for individual words (handles typos)
    - Very short keywords (< 3 chars) are ignored
    - Short words (3-5 chars) require stricter matching (0.80)
    """
    # Exact substring match (fast path)
    if keyword in message:
        return True

    keyword_words = keyword.split()
    message_words = message.split()

    # Single-word keyword
    if len(keyword_words) == 1:
        # Skip fuzzy matching for extremely short keywords
        if len(keyword) < 3:
            return False

        # Short words (3-5 chars) require stricter matching
        local_threshold = threshold
        if len(keyword) <= 5:
            local_threshold = 0.80

        for word in message_words:
            if len(word) < 3:
                continue
            if fuzzy_ratio(keyword, word) >= local_threshold:
                return True
    else:
        # Multi-word keyword: check windows
        for i in range(len(message_words) - len(keyword_words) + 1):
            window = " ".join(message_words[i:i + len(keyword_words)])
            if fuzzy_ratio(keyword, window) >= threshold:
                return True

    return False


def get_response(user_message: str) -> str:
    """
    Match the user's message against the knowledge base.
    Returns the best matching response, or a fallback message.
    """
    message = normalize_text(user_message)

    if not message:
        return "Please type a message."

    best_match = None
    best_score = 0

    for entry in KNOWLEDGE_BASE:
        score = 0
        for keyword in entry["keywords"]:
            if keyword_matches(keyword, message):
                # Longer keywords = higher weight
                score += 1 + (len(keyword.split()) * 0.5)

        if score > best_score:
            best_score = score
            best_match = entry

    # Require at least one match
    if best_match and best_score > 0:
        return best_match["response"]

    # Smart fallback
    return (
        "🤔 I'm not sure I understand. Here are some topics I can help with:\n"
        "• 🕐 Opening hours\n"
        "• 📖 Borrowing & returning books\n"
        "• 🔄 Renewing books\n"
        "• 🔍 Searching for books\n"
        "• 💰 Fines & policies\n"
        "• 🏫 Study rooms\n"
        "• 📶 Wi-Fi & printing\n"
        "• 🪪 Membership\n"
        "• 📱 E-Books\n"
        "• 🎓 Tutoring\n"
        "• 📝 Research help\n"
        "• 📞 Contact info\n\n"
        "Try rephrasing your question, or type 'help' for a list of topics."
    )


# ============================================================
# FLASK ROUTES
# ============================================================

@app.route("/")
def index():
    """Render the chat interface."""
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    """Handle user messages and return a response."""
    data = request.get_json()
    user_message = data.get("message", "")
    return jsonify({"response": get_response(user_message)})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)