import os
import pytest
from agents_tools.pdf_generation_agent import create_invoice_pdf_file
from models.Invoice import InvoiceContext


@pytest.fixture
def sample_invoice_context():
    return InvoiceContext(
        serial_number="20240001",
        invoice_number="INV-001",
        invoice_currency_code="CNY",
        total_amount=1234.56,
        tax_amount=234.56,
        buyer_name="测试购买方",
        buyer_tax_id="1234567890",
        seller_name="测试销售方",
        seller_tax_id="0987654321",
        product_name="测试商品",
        tax_category_code="1000000",
        notes="测试备注"
    )

def test_create_invoice_pdf_file(sample_invoice_context, request):
    pdf_path = create_invoice_pdf_file(sample_invoice_context)
    print(f"PDF文件路径: {pdf_path}")
    assert os.path.exists(pdf_path)
    # 检查文件大小大于0
    assert os.path.getsize(pdf_path) > 0
    # 可选：检查PDF内容包含关键字（需安装pypdf）
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        text = "".join(page.extract_text() or "" for page in reader.pages)
        assert "发票信息" in text
        assert "测试购买方" in text
        assert "测试销售方" in text
        assert "测试商品" in text
    except ImportError:
        pass  # 未安装pypdf则跳过内容检查
    # 只在测试通过时删除PDF，失败时保留
    def cleanup():
        if os.path.exists(pdf_path) and False:
            os.remove(pdf_path)
    request.addfinalizer(cleanup)