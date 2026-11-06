"""Chặn job tốn tiền: ước tính > ngưỡng (configs/pricing.yaml: guard.confirm_above_usd) thì cần --confirm."""
from .cost_logger import Pricing


class BudgetExceeded(RuntimeError):
    pass


def check(estimated_usd: float, confirmed: bool, what: str = "job", pricing: Pricing | None = None):
    limit = (pricing or Pricing()).confirm_above
    if estimated_usd > limit and not confirmed:
        raise BudgetExceeded(
            f"{what}: ước tính {estimated_usd:.2f} USD > ngưỡng {limit:.2f} USD. "
            f"Xem lại `make api-dry`, rồi chạy lại với CONFIRM=1 (hoặc --confirm) nếu đồng ý.")
    return True
