# from pymongo import MongoClient
# from datetime import datetime

# # ── MongoDB Atlas Connection ──
# # MongoDB Atlas par free account banao → cluster banao → connection string copy karo
# MONGO_URI = "mongodb://localhost:27017"

# client = MongoClient(MONGO_URI)
# db = client["python_chatbot"]          # database name
# users_collection = db["users"]         # users table
# chats_collection = db["chat_history"]  # chat history table


# # ── User Functions ──
# def create_user(username: str, email: str, hashed_password: str) -> bool:
#     """Register new user in MongoDB"""
#     # Check if user already exists
#     if users_collection.find_one({"email": email}):
#         return False   # already exists

#     users_collection.insert_one({
#         "username": username,
#         "email": email,
#         "password": hashed_password,
#         "created_at": datetime.now(),
#         "is_active": True
#     })
#     return True


# def get_user_by_email(email: str):
#     """Find user by email"""
#     return users_collection.find_one({"email": email})


# def get_user_by_username(username: str):
#     """Find user by username"""
#     return users_collection.find_one({"username": username})


# # ── Chat History Functions ──
# def save_chat(username: str, role: str, message: str):
#     """Save one chat message to MongoDB"""
#     chats_collection.insert_one({
#         "username": username,
#         "role": role,
#         "message": message,
#         "timestamp": datetime.now()
#     })


# def get_chat_history(username: str) -> list:
#     """Load chat history for a user"""
#     chats = chats_collection.find(
#         {"username": username},
#         sort=[("timestamp", 1)]   # oldest first
#     )
#     return [{"role": c["role"], "content": c["message"]} for c in chats]


# def clear_chat_history(username: str):
#     """Delete all chats for a user"""
#     chats_collection.delete_many({"username": username})







#     # database.py mein yeh function add karo (neeche)

# def get_user_stats(username: str) -> dict:
#     """Get performance stats for dashboard"""

#     # Total user messages
#     total_questions = chats_collection.count_documents({
#         "username": username,
#         "role": "user"
#     })

#     # Total bot replies
#     total_replies = chats_collection.count_documents({
#         "username": username,
#         "role": "assistant"
#     })

#     # Unique days active
#     pipeline = [
#         {"$match": {"username": username}},
#         {"$group": {
#             "_id": {
#                 "$dateToString": {
#                     "format": "%Y-%m-%d",
#                     "date": "$timestamp"
#                 }
#             }
#         }},
#         {"$count": "days"}
#     ]
#     result = list(chats_collection.aggregate(pipeline))
#     days_active = result[0]["days"] if result else 0

#     # Last active time
#     last_msg = chats_collection.find_one(
#         {"username": username},
#         sort=[("timestamp", -1)]
#     )
#     if last_msg:
#         last_active = last_msg["timestamp"].strftime("%d %b, %I:%M %p")
#     else:
#         last_active = "Never"

#     return {
#         "total_questions": total_questions,
#         "total_replies": total_replies,
#         "days_active": days_active,
#         "last_active": last_active
#     }







# database.py

from pymongo import MongoClient
from datetime import datetime
import os

# ── MongoDB Connection ──
MONGO_URI = os.environ["MONGO_URI"]

client = MongoClient(MONGO_URI)
db = client["python_chatbot"]

users_collection  = db["users"]
chats_collection  = db["chat_history"]
stats_collection  = db["user_stats"]        # permanent stats — never cleared


# ════════════════════════════
#   USER FUNCTIONS
# ════════════════════════════

def create_user(username: str, email: str, hashed_password: str) -> bool:
    """Register new user — also creates a permanent stats record"""
    if users_collection.find_one({"email": email}):
        return False

    users_collection.insert_one({
        "username": username,
        "email": email,
        "password": hashed_password,
        "created_at": datetime.now(),
        "is_active": True
    })

    # Create stats record for this user on registration
    stats_collection.insert_one({
        "username": username,
        "total_questions": 0,
        "total_replies": 0,
        "active_dates": [],                  # list of unique date strings
        "daily_counts": [],                  # list of {date, count} for graph
        "first_active": datetime.now(),
        "last_active": datetime.now()
    })

    return True


def get_user_by_email(email: str):
    """Find user by email"""
    return users_collection.find_one({"email": email})


def get_user_by_username(username: str):
    """Find user by username"""
    return users_collection.find_one({"username": username})


# ════════════════════════════
#   CHAT HISTORY FUNCTIONS
# ════════════════════════════

def save_chat(username: str, role: str, message: str):
    """
    Save chat message to MongoDB.
    Also permanently update stats — stats survive chat clear.
    """
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")

    # Save message to chat_history
    chats_collection.insert_one({
        "username": username,
        "role": role,
        "message": message,
        "timestamp": now
    })

    # Update permanent stats
    if role == "user":
        # Check if today already has a count entry
        stats = stats_collection.find_one({"username": username})

        if stats:
            daily_counts = stats.get("daily_counts", [])
            # Find today's entry
            today_entry = next((d for d in daily_counts if d["date"] == today), None)

            if today_entry:
                # Increment today's count
                stats_collection.update_one(
                    {"username": username, "daily_counts.date": today},
                    {
                        "$inc": {
                            "total_questions": 1,
                            "daily_counts.$.count": 1
                        },
                        "$set": {"last_active": now},
                        "$addToSet": {"active_dates": today}
                    }
                )
            else:
                # Add new date entry for today
                stats_collection.update_one(
                    {"username": username},
                    {
                        "$inc": {"total_questions": 1},
                        "$set": {"last_active": now},
                        "$addToSet": {"active_dates": today},
                        "$push": {"daily_counts": {"date": today, "count": 1}}
                    }
                )

    elif role == "assistant":
        stats_collection.update_one(
            {"username": username},
            {
                "$inc": {"total_replies": 1},
                "$set": {"last_active": now}
            }
        )


def get_chat_history(username: str) -> list:
    """Load full chat history for a user"""
    chats = chats_collection.find(
        {"username": username},
        sort=[("timestamp", 1)]
    )
    return [{"role": c["role"], "content": c["message"]} for c in chats]


def clear_chat_history(username: str):
    """
    Delete chat messages only.
    Stats collection is NOT touched — counts stay permanent.
    """
    chats_collection.delete_many({"username": username})


# ════════════════════════════
#   STATS FUNCTIONS
# ════════════════════════════

def get_user_stats(username: str) -> dict:
    """
    Get permanent stats for dashboard.
    Counts never reset even after chat is cleared.
    """
    stats = stats_collection.find_one({"username": username})

    if not stats:
        # Safety fallback for old users who registered before stats collection existed
        stats_collection.insert_one({
            "username": username,
            "total_questions": 0,
            "total_replies": 0,
            "active_dates": [],
            "daily_counts": [],
            "first_active": datetime.now(),
            "last_active": datetime.now()
        })
        return {
            "total_questions": 0,
            "total_replies": 0,
            "days_active": 0,
            "last_active": "Never",
            "member_since": "N/A",
            "daily_counts": []
        }

    # Days active = unique dates used
    days_active = len(stats.get("active_dates", []))

    # Last active formatted
    last_active = stats.get("last_active")
    last_active_str = last_active.strftime("%d %b %Y, %I:%M %p") if last_active else "Never"

    # Member since
    first_active = stats.get("first_active")
    member_since = first_active.strftime("%d %b %Y") if first_active else "N/A"

    # Daily counts for graph — sorted by date
    daily_counts = sorted(
        stats.get("daily_counts", []),
        key=lambda x: x["date"]
    )

    return {
        "total_questions": stats.get("total_questions", 0),
        "total_replies":   stats.get("total_replies", 0),
        "days_active":     days_active,
        "last_active":     last_active_str,
        "member_since":    member_since,
        "daily_counts":    daily_counts           # used for graph in dashboard
    }






def save_quiz_result(username: str, topic: str, score: int, total: int, percent: int):
    """
    Save quiz result permanently.
    Never deleted even if chat is cleared.
    """
    now   = datetime.now()
    today = now.strftime("%Y-%m-%d")

    # Save individual quiz attempt
    db["quiz_results"].insert_one({
        "username":   username,
        "topic":      topic,
        "score":      score,
        "total":      total,
        "percent":    percent,
        "date":       today,
        "timestamp":  now
    })

    # Update quiz summary in stats collection
    stats_collection.update_one(
        {"username": username},
        {
            "$inc": {
                "total_quizzes":     1,
                "total_quiz_score":  score,
                "total_quiz_questions": total
            },
            "$push": {
                "quiz_history": {
                    "topic":     topic,
                    "score":     score,
                    "total":     total,
                    "percent":   percent,
                    "date":      today,
                    "timestamp": now
                }
            }
        }
    )


def get_quiz_stats(username: str) -> dict:
    """
    Get all quiz performance data for dashboard graphs.
    """
    results = list(
        db["quiz_results"].find(
            {"username": username},
            sort=[("timestamp", 1)]
        )
    )

    if not results:
        return {
            "total_quizzes":    0,
            "average_score":    0,
            "best_score":       0,
            "worst_score":      0,
            "quiz_history":     [],
            "topic_scores":     [],
            "daily_quiz_data":  []
        }

    # Calculate overall stats
    percents         = [r["percent"] for r in results]
    average_score    = round(sum(percents) / len(percents), 1)
    best_score       = max(percents)
    worst_score      = min(percents)

    # Quiz history for line graph (attempt number vs score)
    quiz_history = [
        {
            "attempt":  i + 1,
            "topic":    r["topic"],
            "percent":  r["percent"],
            "score":    f"{r['score']}/{r['total']}",
            "date":     r["date"]
        }
        for i, r in enumerate(results)
    ]

    # Topic-wise average score for bar chart
    topic_map = {}
    for r in results:
        t = r["topic"]
        if t not in topic_map:
            topic_map[t] = []
        topic_map[t].append(r["percent"])

    topic_scores = [
        {
            "topic":   t,
            "average": round(sum(v) / len(v), 1),
            "attempts": len(v)
        }
        for t, v in topic_map.items()
    ]

    # Daily quiz count for activity graph
    daily_map = {}
    for r in results:
        d = r["date"]
        daily_map[d] = daily_map.get(d, 0) + 1

    daily_quiz_data = [
        {"date": d, "quizzes": c}
        for d, c in sorted(daily_map.items())
    ]

    return {
        "total_quizzes":   len(results),
        "average_score":   average_score,
        "best_score":      best_score,
        "worst_score":     worst_score,
        "quiz_history":    quiz_history,
        "topic_scores":    topic_scores,
        "daily_quiz_data": daily_quiz_data
    }