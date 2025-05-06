from agents import Agent, RunContextWrapper, function_tool
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions

from models.Invoice import InvoiceContext
from datetime import date, datetime


@function_tool
def complete_basic_info(wrapper: RunContextWrapper[InvoiceContext]) -> str:
    """
    补全发票的基础信息：如含税总金额、税额、购销方信息等。
    只补全缺失的字段，不覆盖已有信息。
    """
    # 获取真正的InvoiceContext对象
    ctx = wrapper.context if hasattr(wrapper, 'context') else wrapper
    
    DEFAULT_TAX_RATE = 0.13
    # 补全含税总金额和税额
    if (ctx.total_amount != 0.0 and ctx.tax_amount == 0.0):
        # 若有总金额无税额，按默认税率推算税额
        ctx.tax_amount = round(ctx.total_amount * DEFAULT_TAX_RATE / (1 + DEFAULT_TAX_RATE), 2)
    elif (ctx.tax_amount != 0.0 and ctx.total_amount == 0.0):
        # 若有税额无总金额，按默认税率推算总金额
        ctx.total_amount = round(ctx.tax_amount / DEFAULT_TAX_RATE * (1 + DEFAULT_TAX_RATE), 2)

    # 补全其他必填字段的默认值
    if not ctx.invoice_currency_code:
        ctx.invoice_currency_code = "CNY"
        
    # 补全购销方信息的默认值
    if not ctx.buyer_name:
        ctx.buyer_name = "默认购买方"
    if not ctx.buyer_tax_id:
        ctx.buyer_tax_id = "1234567890"
    if not ctx.seller_name:
        ctx.seller_name = "默认销售方"
    if not ctx.seller_tax_id:
        ctx.seller_tax_id = "9876543210"
        
    # 补全发票编号
    if not ctx.invoice_number:
        # 使用流水号作为发票编号的一部分
        serial_suffix = ctx.serial_number.split('-')[-1] if ctx.serial_number else '001'
        today = date.today().strftime('%Y%m%d')
        ctx.invoice_number = f"INV-{today}-{serial_suffix}"
        
    return "完成基础信息补全"

@function_tool
def complete_notes(wrapper: RunContextWrapper[InvoiceContext]) -> str:
    """
    补全发票的备注信息。
    只在备注字段为空时补全，且不覆盖已有备注。
    """
    ctx = wrapper.context if hasattr(wrapper, 'context') else wrapper
    if not ctx.notes:
        # 这里可以根据实际业务逻辑补全备注，示例为默认备注
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ctx.notes = f"本发票由系统自动补全基础信息：{current_time}"
    return "完成备注信息补全"


PROMPT = (
    "你是一个发票信息的补全助手。"
    "利用工具complete_basic_info补全发票的基础信息。"
    "如果没有明确要求补全的其他信息，则不需要调用其他工具补全。"
    "补全后，一定需要handoff给下一个agent。"
)


completion_agent = Agent[InvoiceContext](
    name="补全助手",
    instructions=prompt_with_handoff_instructions(PROMPT),
    tools=[complete_basic_info, complete_notes],
    model="gpt-4o-mini",
)