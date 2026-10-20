"""Chat replies. Crisis phrases always get a fixed answer. Other messages go to Groq
when GROQ_API_KEY is set, and fall back to keyword replies if that call fails."""
import json
import logging
import re
import urllib.error
import urllib.request

from core.config import GROQ_API_KEY, GROQ_MODEL

logger = logging.getLogger("solace")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
SYSTEM_PROMPT = (
    "You are Solace, a calm, kind listener for students. "
    "You are not a therapist, doctor, or crisis service, and you never diagnose. "
    "Reply to the exact feeling in the latest message, in 2 to 4 short sentences, in plain language. "
    "Do not cheer a sad or self-critical message. "
    "Ask one gentle question when it fits. "
    "If the person may be in immediate danger or talking about suicide or self-harm, "
    "say you cannot help in a crisis and tell them to contact local emergency services "
    "(112 in India, 911 in the US) or Tele-MANAS at 14416."
)

# 1) CRISIS PHRASES: checked first. If any of these appear, we always return
#    CRISIS_RESPONSE. (Written in lowercase, without apostrophes.)
CRISIS_PHRASES = [
    "kill myself", "killing myself", "end my life", "ending my life", "end my own life",
    "end it all", "ending it all", "take my own life", "taking my own life",
    "want to die", "wanna die", "want to be dead", "better off dead", "no reason to live",
    "hurt myself", "hurting myself", "harm myself", "harming myself",
    "cut myself", "cutting myself", "self harm",
    "dont want to live", "do not want to live", "dont want to be alive",
    "suicide", "suicidal",
]

CRISIS_RESPONSE = (
    "I'm really sorry you're going through this, and I'm glad you told me. "
    "You deserve support right now, and I'm not able to give you the help you need in a crisis.\n\n"
    "If you are in immediate danger or might act on these thoughts, please call your local "
    "emergency number now (112 in India, 911 in the US).\n\n"
    "You can also talk to a trained person at any time:\n"
    "- India: Tele-MANAS, 14416 or 1800-891-4416 (free, 24/7)\n"
    "- US: call or text 988\n"
    "- Elsewhere: findahelpline.com lists crisis lines by country\n\n"
    "Please also tell someone you trust, like a friend, family member or teacher, "
    "how you are feeling so you are not alone with this."
)

FALLBACK_RESPONSE = "I'm here to listen. Tell me a little more about how you're feeling."

# 2) RESPONSES: a list of [keywords, response] pairs (like an array of objects in JS).
#    The FIRST group whose keyword appears in the message wins, so more serious or more
#    specific groups are listed first and greetings / thanks are near the end.
#    Keywords are lowercase, letters only, no apostrophes ("cant", not "can't").
RESPONSES = [
    # --- heavy feelings ---
    (["hopeless", "no hope", "give up", "giving up", "pointless", "worthless", "useless"],
     "I'm really sorry you feel this way. Feeling hopeless is exhausting, but feelings can change, even when it doesn't seem possible right now. Is there someone you trust that you could talk to today?"),
    (["abuse", "abused", "abusive", "violence", "beaten", "assault"],
     "I'm so sorry. You deserve to be safe. If you are in danger right now, please call your local emergency number (112 in India). Please also tell a trusted adult, a counselor, or call Tele-MANAS at 14416. Would you like to tell me more?"),
    (["depressed", "depression", "numb", "empty"],
     "I'm sorry you're feeling this low. I can't diagnose anything, but if these feelings last more than a couple of weeks, please talk to a counselor or doctor. What has been the hardest part lately?"),
    (["panic", "panic attack", "cant breathe"],
     "Let's slow down together. Breathe in through your nose for 4 seconds, hold for 4, then breathe out slowly for 6. Repeat a few times. If you have chest pain or real trouble breathing, please get medical help right away. Do you feel a little calmer?"),
    (["overwhelmed", "too much", "cant cope", "cant handle", "breaking down", "burnout", "burnt out"],
     "That sounds like a lot to carry. Try writing down everything on your mind, then pick just one small thing to do first. You don't have to solve it all today. What feels heaviest right now?"),
    (["overthinking", "overthink", "cant stop thinking", "racing thoughts"],
     "Overthinking is tiring. Try writing your thoughts down, or name 5 things you can see around you to bring your mind back to the present. What thought keeps coming back?"),

    # --- common feelings ---
    (["anxiety", "anxious", "nervous", "worried", "worry", "worrying", "restless", "uneasy"],
     "Anxiety can feel really uncomfortable. Try slow breathing: in for 4 seconds, out for 6. What is the thought that worries you the most right now?"),
    (["stress", "stressed", "stressful", "pressure", "tense", "tension"],
     "I'm sorry you're feeling stressed. Take a short break and some slow breaths. Would you like to talk about what's causing the stress?"),
    (["scared", "afraid", "fear", "frightened", "terrified"],
     "Feeling scared is hard, and it's okay to feel that way. You're not alone in this. What is making you feel afraid?"),
    (["grief", "grieving", "died", "death", "passed away", "funeral", "lost someone"],
     "I'm so sorry for your loss. Grief has no timetable, and whatever you feel is okay. Would you like to tell me about them?"),
    (["bullied", "bullying", "teased", "embarrassed", "ashamed", "left out"],
     "I'm sorry that happened. It's not your fault, and your feelings matter. Is there a teacher, friend or family member you could tell about this?"),
    (["insecure", "insecurity", "not good enough", "ugly", "comparing", "compare", "jealous"],
     "Comparing yourself to others is painful, and social media makes it worse. You only see their highlights, not their struggles. What do you like about yourself, even something small?"),
    (["sad", "sadness", "unhappy", "upset", "hurt", "miserable", "feel down", "feeling down", "not okay", "not good", "not great", "not fine", "not well", "unwell", "bad day", "feel bad"],
     "I'm sorry you're feeling this way. It's okay to feel sad sometimes. I'm here to listen. Do you want to tell me what happened?"),
    (["cry", "crying", "cried", "tears"],
     "It's okay to cry. It can help let feelings out. Take your time, I'm here with you. What's making you cry?"),
    (["lonely", "loneliness", "alone", "no friends", "isolated", "nobody"],
     "Feeling lonely is really hard, and you're not alone in feeling this. I'm here to talk. Is there one person you could message today, even just to say hi?"),
    (["angry", "anger", "mad", "furious", "irritated", "annoyed"],
     "It's okay to feel angry. Try taking a few deep breaths or a short walk before reacting. What happened that made you so angry?"),
    (["frustrated", "frustration", "frustrating", "fed up"],
     "That sounds frustrating. When things don't go as planned, it's natural to feel stuck. What is getting in your way?"),
    (["tired", "exhausted", "fatigue", "drained", "worn out"],
     "You sound worn out. Rest is important, not lazy. Can you take a short break, drink some water, or stretch a little?"),
    (["sleepy", "drowsy"],
     "Feeling sleepy? A glass of water, some fresh air or a short walk can help, or a short nap if you can. Did you sleep well last night?"),
    (["bored", "boring", "boredom"],
     "Boredom happens to everyone. You could try a short walk, some music, or something creative like drawing or writing. What do you usually enjoy?"),
    (["confused", "confusing", "lost", "unsure", "dont know what to do"],
     "Feeling confused is uncomfortable. Try writing down what you do know and what you're unsure about. Which part feels most unclear?"),

    # --- body and sleep ---
    (["insomnia", "cant sleep", "cannot sleep", "trouble sleeping", "sleepless", "awake all night"],
     "Not sleeping is tough. Try keeping your phone away an hour before bed, dimming the lights, and slow breathing. If it keeps happening for weeks, a doctor can help. What keeps your mind busy at night?"),
    (["sleep", "sleeping"],
     "Sleep matters a lot for how we feel. Try going to bed and waking up at the same time each day. How has your sleep been lately?"),
    (["headache", "migraine", "head hurts"],
     "I'm sorry about your headache. Try resting in a quiet place, drinking water and looking away from screens. If it is severe or keeps coming back, please see a doctor. Have you been under a lot of stress?"),

    # --- student life ---
    (["failure", "failed", "fail", "flunked", "didnt pass"],
     "I'm sorry. Failing hurts, but it doesn't define you. Many successful people have failed and tried again. What do you think you could do differently next time?"),
    (["mistake", "mistakes", "messed up", "screwed up", "regret", "guilty"],
     "Everyone makes mistakes. They're part of learning. Be as kind to yourself as you'd be to a friend. Do you want to talk about what happened?"),
    (["exam", "exams", "test", "tests", "finals", "viva", "backlog", "backlogs", "cgpa", "marks", "grades"],
     "Exams can be stressful. Try short study sessions with breaks, and get enough sleep. Your marks don't measure your worth. Which subject is worrying you most?"),
    (["deadline", "deadlines", "due tomorrow", "submission"],
     "Deadlines can feel scary. List what's left, start with the smallest task, and work in 25-minute blocks with short breaks. How much time do you have?"),
    (["assignment", "assignments", "homework", "project", "presentation"],
     "Assignments can pile up. Break it into small steps and finish one at a time. Which part do you want to start with?"),
    (["study", "studies", "studying", "revision", "revise", "syllabus", "concentrate", "focus"],
     "Studying is easier in short bursts: 25 minutes of focus, then a 5-minute break. Keep your phone away while you study. What subject are you working on?"),
    (["college", "university", "campus", "class", "classes", "teacher", "professor"],
     "College life can be demanding. It's okay to ask for help from friends or teachers. What's been the hardest part about college?"),
    (["career", "job", "placement", "placements", "internship", "interview", "future"],
     "Worrying about the future is very common. You don't need everything figured out right now. Taking one small step at a time helps. What feels most uncertain?"),

    # --- people ---
    (["breakup", "break up", "broke up", "heartbroken", "ex"],
     "I'm sorry about the breakup. Heartbreak really hurts, and it takes time to heal. Lean on friends and family, and be gentle with yourself. Do you want to talk about it?"),
    (["relationship", "boyfriend", "girlfriend", "partner", "crush", "dating"],
     "Relationships can bring both joy and stress. Honest, calm communication often helps. What's going on in yours?"),
    (["friend", "friends", "friendship", "best friend"],
     "Friendships matter a lot, and problems with friends can really hurt. What happened between you?"),
    (["family", "parents", "mother", "father", "mom", "dad", "brother", "sister", "siblings"],
     "Family can be a source of support and sometimes of stress. What's going on with your family?"),
    (["home", "homesick", "hostel"],
     "Missing home is natural, especially when you're away. Calling someone from home or keeping a small reminder of home nearby can help. What do you miss most?"),

    # --- self ---
    (["motivation", "unmotivated", "demotivated", "no motivation", "lazy", "procrastinate", "procrastinating", "cant start", "dont feel like"],
     "Low motivation happens to everyone. Start with just 5 minutes of the task. Starting is usually the hardest part. What are you trying to get done?"),
    (["confidence", "confident", "self esteem"],
     "Confidence grows in small steps. Notice one thing you did well today, however small. What would you like to feel more confident about?"),
    (["money", "fees", "loan", "financial"],
     "Money worries are stressful. Try listing your expenses and talking to someone you trust about it. You don't have to handle it alone. What's worrying you most?"),
    (["phone", "instagram", "social media", "scrolling", "screen time"],
     "Too much scrolling can leave us feeling worse. Try short phone-free breaks, like a walk or a chat with someone in person. How do you feel after using social media?"),
    (["exercise", "gym", "walk", "workout", "yoga"],
     "Moving your body is a great way to lift your mood, even a 10-minute walk helps. What kind of activity do you enjoy?"),
    (["breathing", "breathe", "relax", "meditation", "meditate"],
     "Here's a simple one: breathe in for 4 seconds, hold for 4, breathe out for 6. Repeat 5 times, slowly. How do you feel afterwards?"),

    # --- positive feelings ---
    (["peaceful", "peace", "relaxed", "relaxing"],
     "That sounds lovely. Enjoy the peaceful moment. What helped you feel this way?"),
    (["calm", "calmer", "relieved", "better"],
     "I'm glad you're feeling calmer. Remember what helped, so you can use it again. What worked for you?"),
    (["happy", "happiness", "joy", "joyful", "cheerful", "smile", "smiling"],
     "That's wonderful to hear! I'm glad you're feeling happy. What made your day better?"),
    (["excited", "exciting", "cant wait", "thrilled", "looking forward"],
     "How exciting! I'm happy for you. What are you looking forward to?"),
    (["proud", "achievement", "achieved", "accomplished", "passed", "got selected", "won", "promoted"],
     "Congratulations! You should be proud of yourself. Your hard work paid off. How are you celebrating?"),
    (["grateful", "thankful", "blessed", "appreciate"],
     "Gratitude is a lovely feeling and it's good for our mood too. What are you grateful for today?"),

    # --- conversation ---
    (["thanks", "thank you", "thankyou", "thx"],
     "You're very welcome. I'm glad I could help. I'm here whenever you want to talk."),
    (["sorry", "apologize"],
     "There's no need to apologize. You can share anything here. What would you like to talk about?"),
    (["good morning", "morning"],
     "Good morning! I hope today treats you kindly. How are you feeling today?"),
    (["good night", "goodnight", "night"],
     "Good night. Try to let go of today's worries and get some rest. I'm here if you want to talk tomorrow."),
    (["good", "great", "fine", "okay", "ok", "awesome", "amazing", "wonderful", "fantastic", "nice"],
     "I'm glad to hear that. Is there anything you'd like to share or talk about today?"),
    (["how are you", "how r u", "whats up", "sup"],
     "I'm a simple chatbot, so I don't have feelings, but I'm here and happy to listen. How are you doing today?"),
    (["who are you", "what are you", "your name"],
     "I'm Solace, a simple supportive chatbot. I'm not a therapist or a doctor, but I'm happy to listen and share some ideas. How are you feeling?"),
    (["hello", "hi", "hey", "hii", "hola", "namaste", "yo"],
     "Hello! I'm Solace. I'm here to listen. How are you feeling today?"),
    (["bye", "goodbye", "see you", "gtg"],
     "Take care of yourself. I'm here whenever you want to talk."),
    (["help", "support", "advice", "suggest"],
     "I'm here to help as best I can. Tell me what's on your mind, and we'll take it one step at a time."),
    (["talk", "listen", "vent", "share", "chat"],
     "I'm listening. Take your time and say whatever is on your mind."),
]


def clean_text(message):
    """Lowercase, remove apostrophes, keep only words. Returns ' word word word '."""
    text = message.lower().replace("'", "").replace("’", "")
    words = re.findall(r"[a-z]+", text)  # "I'm so-so!" -> ["im", "so", "so"]
    return " " + " ".join(words) + " "  # spaces at both ends -> whole-word matching


def contains(text, keyword):
    """True if the keyword appears as a whole word/phrase (so 'hi' won't match 'this')."""
    return " " + keyword + " " in text


def keyword_reply(message):
    """First matching keyword group, or the generic fallback."""
    text = clean_text(message)
    for keywords, response in RESPONSES:
        for keyword in keywords:
            if contains(text, keyword):
                return response
    return FALLBACK_RESPONSE


def _clean_reply(text):
    text = text.replace("\u00a0", " ").replace("\u202f", " ").replace("\u2009", " ")
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text[:2000]


def groq_reply(message, history):
    """Ask Groq for a reply. Returns None when the key is missing or the call fails."""
    if not GROQ_API_KEY:
        return None

    turns = []
    for turn in history[-8:]:
        role = turn.get("role")
        content = str(turn.get("content") or "").strip()
        if role in ("user", "assistant") and content:
            turns.append({"role": role, "content": content[:1000]})
    if turns and turns[-1]["role"] == "user" and turns[-1]["content"] == message.strip():
        turns.pop()

    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}, *turns, {"role": "user", "content": message.strip()[:1000]}],
        "temperature": 0.6,
        "max_tokens": 400,
    }
    # Cloudflare rejects urllib's default User-Agent with HTTP 403.
    request = urllib.request.Request(
        GROQ_URL,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "solace-backend/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode())
        text = _clean_reply(data["choices"][0]["message"].get("content") or "")
        return text or None
    except urllib.error.HTTPError as exc:
        logger.warning("Groq reply failed: HTTP %s", exc.code)
        return None
    except Exception as exc:
        logger.warning("Groq reply failed: %s", type(exc).__name__)
        return None


def get_chat_reply(message, history=None):
    text = clean_text(message)

    # Step 1: crisis check. This stays fixed and is not sent to Groq.
    for phrase in CRISIS_PHRASES:
        if contains(text, phrase):
            return CRISIS_RESPONSE

    # Step 2: language model, with the keyword list as backup.
    reply = groq_reply(message, history or [])
    if reply:
        return reply
    return keyword_reply(message)
