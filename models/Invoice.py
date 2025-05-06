from dataclasses import dataclass, field
from typing import Optional
from datetime import date

@dataclass
class InvoiceContext:
    """
    发票上下文信息
    """
    # 流水号
    serial_number: Optional[str] = None
    
    # 发票编号
    invoice_number: Optional[str] = None


    # 货币代码，默认人民币
    invoice_currency_code: str = "CNY"

    # 发票总金额（含税）
    total_amount: float = 0.0

    # 税额
    tax_amount: float = 0.0

    # 购买方名称
    buyer_name: Optional[str] = None

    # 购买方税号
    buyer_tax_id: Optional[str] = None

    # 销售方名称
    seller_name: Optional[str] = None

    # 销售方税号
    seller_tax_id: Optional[str] = None

    # 商品名称
    product_name: Optional[str] = None

    # 税收分类编码
    tax_category_code: Optional[str] = None

    # 备注
    notes: Optional[str] = None