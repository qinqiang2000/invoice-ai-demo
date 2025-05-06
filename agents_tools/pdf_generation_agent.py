from agents import Agent, RunContextWrapper, function_tool
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions
from models.Invoice import InvoiceContext
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import platform


def _register_chinese_font():
    """
    在macOS下注册系统自带的中文字体，优先使用PingFang或华文黑体。
    """
    font_candidates = [
        ("PingFang", "/System/Library/Fonts/PingFang.ttc"),
        ("STHeiti", "/System/Library/Fonts/STHeiti Medium.ttc"),
        ("Heiti SC", "/System/Library/Fonts/Heiti\ SC.ttc"),
        ("Hiragino Sans GB", "/System/Library/Fonts/Hiragino Sans GB.ttc"),
        ("Songti SC", "/System/Library/Fonts/Songti.ttc"),
    ]
    for font_name, font_path in font_candidates:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                return font_name
            except Exception:
                continue
    return None


def create_invoice_pdf_file(invoice: InvoiceContext) -> str:
    """
    根据发票上下文生成PDF文件。
    Args:
        invoice (InvoiceContext): 发票上下文
    Returns:
        str: 生成的PDF文件路径。
    """
    # 检查系统并注册中文字体
    font_name = None
    if platform.system() == "Darwin":
        font_name = _register_chinese_font()
    if not font_name:
        font_name = "Helvetica"  # fallback

    # 统一输出到 output 目录
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output")
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    file_name = f"invoice_{invoice.serial_number or 'unknown'}.pdf"
    file_path = os.path.join(output_dir, file_name)

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4
    y = height - 50
    c.setFont(font_name, 16)
    c.drawString(50, y, "发票信息")
    c.setFont(font_name, 12)
    y -= 40
    fields = [
        ("流水号", invoice.serial_number),
        ("发票编号", invoice.invoice_number),
        ("货币代码", invoice.invoice_currency_code),
        ("含税总金额", str(invoice.total_amount)),
        ("税额", str(invoice.tax_amount)),
        ("购买方名称", invoice.buyer_name),
        ("购买方税号", invoice.buyer_tax_id),
        ("销售方名称", invoice.seller_name),
        ("销售方税号", invoice.seller_tax_id),
        ("商品名称", invoice.product_name),
        ("税收分类编码", invoice.tax_category_code),
        ("备注", invoice.notes),
    ]
    for label, value in fields:
        c.drawString(50, y, f"{label}: {value if value is not None else ''}")
        y -= 25
        if y < 50:
            c.showPage()
            c.setFont(font_name, 12)
            y = height - 50
    c.save()
    
    return file_path


@function_tool
def generate_invoice_pdf(wrapper: RunContextWrapper[InvoiceContext]) -> str:
    """
    适配器：根据发票上下文生成PDF文件。
    Args: None
    Returns:
        str: 生成的PDF文件路径。
    """
    return create_invoice_pdf_file(wrapper.context)

PROMPT = (
    "你是一个发票PDF生成助手。"
    "请用generate_invoice_pdf工具根据发票上下文生成PDF文件。"
)

pdf_generation_agent = Agent[InvoiceContext](
    name="pdf生成助手",
    instructions=prompt_with_handoff_instructions(PROMPT),
    tools=[generate_invoice_pdf],
    model="gpt-4o-mini",
) 