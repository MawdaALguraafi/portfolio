from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str


# =========================
# 🔹 Helpers
# =========================
def normalize_text(text: str) -> str:
    text = str(text or "").lower().strip()

    replacements = {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ة": "ه",
        "ى": "ي",
    }

    for src, target in replacements.items():
        text = text.replace(src, target)

    text = re.sub(r"[^\w\u0600-\u06FF\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def is_arabic(text: str) -> bool:
    return bool(re.search(r"[\u0600-\u06FF]", text))


# =========================
# 🔹 Greeting Detection (🔥 FIXED)
# =========================
def is_greeting_only(question: str, lang: str) -> bool:
    q = normalize_text(question)

    arabic_greetings = [
        "هاي", "هلا", "مرحبا", "اهلا",
        "السلام", "السلام عليكم", "صباح الخير", "مساء الخير"
    ]

    english_greetings = ["hi", "hello", "hey"]

    greetings = arabic_greetings if lang == "ar" else english_greetings

    for greet in greetings:
        g = normalize_text(greet)

        # 🔥 الحل هنا
        if q.startswith(g):
            if len(q.split()) <= 3:
                return True

    return False


# =========================
# 🔹 Custom Answers (🔥 أهم جزء)
# =========================
def get_custom_answer(question: str, lang: str):
    q = normalize_text(question)

    # ===== التواصل =====
    contact_terms_ar = [
        "التواصل", "طريقة التواصل", "طريقه التواصل",
        "كيف اتواصل", "ابي اتواصل", "ابغا اتواصل",
        "ايميل", "الايميل", "البريد"
    ]

    contact_terms_en = [
        "contact", "email", "how can i contact"
    ]

    if any(term in q for term in contact_terms_ar):
        return "يمكن التواصل عبر البريد الإلكتروني: MawdaALguraafi@gmail.com"

    if any(term in q for term in contact_terms_en):
        return "You can contact Mawda via email: MawdaALguraafi@gmail.com"

    # ===== التحية =====
    if is_greeting_only(question, lang):
        if lang == "ar":
            return "مرحبًا! اسأليني عن خبراتها، تعليمها، ومهاراتها."
        return "Hi! Ask me about Mawda’s experience, education, and skills."

    # ===== التعليم =====
    education_terms = [
        "تعليم", "التعليم", "دراسة", "دراسه",
        "بكالوريوس", "البكالوريوس",
        "education", "bachelor"
    ]

    if any(term in q for term in education_terms):
        if lang == "ar":
            return "مودة حاصلة على بكالوريوس في علوم الحاسب من جامعة طيبة بمعدل 4.88 مع مرتبة الشرف الأولى."
        return "Mawda holds a Bachelor’s degree in Computer Science from Taibah University with a GPA of 4.88 (First Class Honors)."

    return None


# =========================
# 🔹 API
# =========================
@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/api/chat")
async def chat(req: ChatRequest):
    question = req.question.strip()
    lang = "ar" if is_arabic(question) else "en"

    if not question:
        return {"answer": "اكتب سؤال." if lang == "ar" else "Write a question."}

    # 🔥 أهم سطر (يوقف الرد الطويل)
    custom = get_custom_answer(question, lang)
    if custom:
        return {"answer": custom}

    # 🔻 fallback بسيط (بدل الكلام الطويل)
    if lang == "ar":
        return {"answer": "هذه المعلومة غير مذكورة في البورتفوليو."}
    else:
        return {"answer": "This information is not mentioned in the portfolio."}
