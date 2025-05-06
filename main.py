import asyncio
from manager import InvoiceManager
from models.Invoice import InvoiceContext


# Entrypoint for the Invoice bot .
async def main() -> None:
    # 构造一个示例发票上下文
    context = InvoiceContext(
        serial_number="132-20240601-001",
        invoice_currency_code="CNY",
        total_amount=1130.0,
    )
    mgr = InvoiceManager()
    await mgr.run(context)


if __name__ == "__main__":
    asyncio.run(main())