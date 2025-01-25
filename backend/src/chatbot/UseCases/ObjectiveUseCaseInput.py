from typing import Optional


class ObjectiveUseCaseInput:
    """目標設定に関するユースケースの入力"""
    # その場合は、promptのみを使用する
    def __init__(self, prompt: str, objective_id: Optional[str] = None):
        self.prompt = prompt
        self.objective_id = objective_id
