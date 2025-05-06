from agents import Agent, RunContextWrapper, function_tool
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions
from models.Invoice import InvoiceContext

@function_tool
def validate_basic_fields(wrapper: RunContextWrapper[InvoiceContext]) -> list[str]:
    """
    校验发票的基础字段是否完整和有效。
    检查必填项：购买方名称、购买方税号、销售方名称、销售方税号、含税总金额、税额。
    校验金额、税额为正数。
    Args: None
    Returns:
        list[str]: 错误信息列表（如无错误则为空）。
    """
    ctx = wrapper.context if hasattr(wrapper, 'context') else wrapper
    errors = []
    if not ctx.buyer_name:
        errors.append("购买方名称缺失")
    if not ctx.buyer_tax_id:
        errors.append("购买方税号缺失")
    if not ctx.seller_name:
        errors.append("销售方名称缺失")
    if not ctx.seller_tax_id:
        errors.append("销售方税号缺失")
    if ctx.total_amount is None or ctx.total_amount <= 0:
        errors.append("含税总金额无效")
    if ctx.tax_amount is None or ctx.tax_amount < 0:
        errors.append("税额无效")
    if not ctx.notes:
        errors.append("备注缺失")
    return errors


PROMPT = (
    "你是一个发票信息的校验助手。"
    "请先用validate_basic_fields工具校验发票基础字段的完整性和有效性。"
    "如果校验通过，则handoff给下一个agent。"
    "如果校验不通过，则handoff给下一个completion_agent, 并告知缺失项。"
)

validation_agent = Agent[InvoiceContext](
    name="校验助手",
    instructions=prompt_with_handoff_instructions(PROMPT),
    tools=[validate_basic_fields],
    model="gpt-4o-mini",
) 