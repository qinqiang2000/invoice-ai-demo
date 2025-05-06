from rich.console import Console

from printer import Printer


console = Console()
printer = Printer(console)

printer.update_item("step1", "正在抓取数据")
# ... 数据抓取完成
printer.mark_item_done("step1")

printer.update_item("step2", "正在分析数据")
# ... 分析完成
printer.mark_item_done("step2")

printer.end()