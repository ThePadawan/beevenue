from typing import Optional


class BeevenueContext(object):
    def __init__(self, is_sfw: bool, user_role: Optional[str]):
        self.is_sfw = is_sfw
        self.user_role = user_role
