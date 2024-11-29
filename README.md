![微信图片_20241129160326](https://github.com/user-attachments/assets/150a42e6-db82-4a21-a80b-bc06db3e8319)

先安装版本（默认目录即可）：Ghostscript 10.04.0 for Windows (64 bit)
https://www.ghostscript.com/releases/gsdnld.html

首先，D盘根目录新建两个文件夹，一个txt文件。
“other“-常用打印文件，比如在打印过程中需要插入一些分隔页面以及平时常用的文件等；
“temuskupdf”-设计好的SKU ID命名的pdf文件存放目录（通常是数百个数量）；
“print_set.txt”-打印机名称，自行一行一个输入保存（因为有些打印机不想让它显示时这时候自己输入就很方便）；

输入SKU ID后回车自动匹配“temuskupdf”中的文件，如存在，回车后会跳转到输入“数量”，输入数量之后再次敲击回车开始打印。

程序依赖gswin64c.exe打印接口全程静默打印。
后续考虑添加打印记录本地保存，以方便后期核对出库数量，打印记录设置“重打”按钮，手动删除某条打印记录等因为偶尔打错的记录删除掉可以方便正确统计出库数量。
代码都是LLM一步一步调试生成，本人一句也不会写。有问题别问我~


