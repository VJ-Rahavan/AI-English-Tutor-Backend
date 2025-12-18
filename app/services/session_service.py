class SessionService:
    def __init__(self):
        self.session_score = 50
        self.session_summary = "User is starting the conversation."

    def update_score(self, evaluation: dict):
        score_change = 0
        if evaluation.get("isGrammaticallyCorrect"):
            score_change += 2
        else:
            score_change -= 1

        if evaluation.get("clarityScore", 0) >= 4:
            score_change += 1

        self.session_score = max(0, min(100, self.session_score + score_change))
        
        return {
            "score": self.session_score,
            "change": score_change,
            "comment": evaluation.get("shortFeedback")
        }

    def get_summary(self):
        return self.session_summary

    def update_summary(self, new_summary: str):
        self.session_summary = new_summary

# Global instance to maintain state across requests (in memory)
session_service = SessionService()
