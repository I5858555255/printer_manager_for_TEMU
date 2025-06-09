制作该脚本的目的是方便TEMU标签打印，背景是几百个上千个SKU标签pdf文件在发货的时候需要打印，我们都知道TEMU平台后台有打印标签功能，
而我将合规标签与系统标签整合后无需在系统中打印，整合也使得粘贴标签时节省至少一倍的工作量，因为只用贴一张！
过程：
运营在temu后台打印发货清单（清单上有SKU id）
仓库拿着发货清单打印标签。
分工提高工作效率

![微信图片_20241129160326](https://github.com/user-attachments/assets/150a42e6-db82-4a21-a80b-bc06db3e8319)

## 安装与设置 (Installation and Setup)

1.  **安装 Ghostscript:**
    *   请先安装 Ghostscript 10.04.0 (或兼容版本)。推荐使用64位版本。
    *   下载链接: [Ghostscript Downloads](https://www.ghostscript.com/releases/gsdnld.html)
    *   (Please install Ghostscript 10.04.0 (or a compatible version) first. The 64-bit version is recommended.)

2.  **文件夹和文件设置 (Folder and File Setup):**
    *   以下为程序默认使用的文件夹名称和文件，建议首次运行时按默认设置，程序会自动在需要时创建相关配置文件。
    *   (The following are the default folder names and files used by the program. It's recommended to use the defaults on the first run; the program will create necessary configuration files if they don't exist.)
        *   `D:\other` - **默认**常用打印文件存放目录。用于存放例如分隔页或日常打印的PDF文件。
        *   (`D:\other` - **Default** directory for commonly used print files, e.g., separator pages or frequently printed PDFs.)
        *   `D:\temuskupdf` - **默认**SKU PDF文件存放目录。存放以SKU ID命名的PDF标签文件。
        *   (`D:\temuskupdf` - **Default** directory for SKU PDF files. Stores PDF label files named with SKU IDs.)
        *   `print_set.txt` - **默认**打印机配置文件名。用于指定程序中可选的打印机列表，每行一个打印机名称。
        *   (`print_set.txt` - **Default** printer configuration filename. Used to specify the list of available printers in the program, one printer name per line.)
    *   **重要提示 (Important Note):**
        *   这些路径现在是可配置的。首次运行时如果 `printer_config.json` 文件不存在，程序会自动创建并填入这些默认路径。您可以编辑 `printer_config.json` 文件来修改这些路径。可配置的键名分别为 `temuskupdf_folder`、`other_folder` 和 `print_set_file`。
        *   (These paths are now configurable. If `printer_config.json` does not exist upon first run, it will be created with these default paths. You can edit `printer_config.json` to change these paths if needed. The configurable keys are `temuskupdf_folder`, `other_folder`, and `print_set_file`.)

## 使用说明 (Usage)

输入SKU ID后回车，程序会自动在配置的“SKU PDF文件存放目录”（默认为 `D:\temuskupdf`）中查找对应的PDF文件。
如果文件存在，光标会自动跳转到“数量”输入框，输入打印数量后再次敲击回车即可开始打印。
程序依赖 Ghostscript (`gswin64c.exe` 或 `gswin32c.exe`) 实现静默打印。

(After entering the SKU ID and pressing Enter, the program automatically searches for the corresponding PDF file in the configured "SKU PDF directory" (default is `D:\temuskupdf`). If the file exists, the cursor will jump to the "quantity" input field. Enter the quantity and press Enter again to start printing. The program relies on Ghostscript for silent printing.)

## 功能更新 (Feature Updates)

### 打印历史记录 (Print History)

*   程序现在会自动记录每次成功的打印任务。
    *   (The program now automatically records every successful print job.)
*   打印记录保存在程序目录下的 `print_log.csv` 文件中。该文件包含以下信息：时间戳 (Timestamp)、SKU/文件名 (SKU/Filename)、数量 (Quantity)、打印机 (Printer) 和状态 (Status)。
    *   (Print records are saved in `print_log.csv` in the program directory. This file includes: Timestamp, SKU/Filename, Quantity, Printer, and Status.)
*   主界面新增“打印历史”选项卡，提供以下功能：
    *   (A "Print History" tab has been added to the main interface, providing the following functions:)
    *   **查看所有打印记录**: 默认按时间倒序排列。
        *   (View all print records, sorted by time in descending order by default.)
    *   **刷新记录**: 重新加载并显示最新的打印历史。
        *   (Refresh Records: Reload and display the latest print history.)
    *   **重打**: 快速重新打印选定的历史记录。
        *   (Reprint: Quickly reprint a selected historical job.)
    *   **删除**: 删除选定的单条打印记录（操作前会有确认提示）。
        *   (Delete: Delete a selected single print record (with confirmation before action).)
    *   **清空所有记录**: 删除所有打印历史记录（操作前会有确认提示）。
        *   (Clear All Records: Delete all print history records (with confirmation before action).)

## 后续考虑 (Future Considerations)

后续可考虑的功能包括：更高级的打印队列管理、用户权限控制、远程管理界面、更灵活的错误处理和日志分级等。

(Future considerations could include: more advanced print queue management, user permissions, a remote management interface, more flexible error handling and log levels, etc.)

## 关于 (About)
代码都是LLM一步一步调试生成，本人一句也不会写。有问题别问我~
(The code was generated step-by-step with an LLM. I didn't write a single line myself. Don't ask me if you have problems~)
