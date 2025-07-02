# Local Printer Interface Guide

This document describes how to use the `local_printer_interface.py` module to programmatically query SKU information and print PDF files from your local Python applications.

## Overview

The interface provides two main functions:

1.  `get_sku_info(sku: str) -> dict | None`: Retrieves information about a PDF associated with an SKU, such as its file path and dimensions.
2.  `print_sku_locally(sku: str, quantity: int, printer_name: str, ...) -> bool`: Prints the PDF associated with an SKU to a specified printer using Ghostscript.

This interface is designed to work within the existing environment of the Printer Management System application, leveraging its configuration and logging mechanisms.

## Prerequisites

1.  **Python Environment**: Ensure you have a Python environment set up with the necessary dependencies. The interface relies on modules used by the main application. Key dependencies include:
    *   `PyMuPDF` (for `fitz`): Used to read PDF properties. Install via `pip install PyMuPDF`.
    *   `PySide6`: Used for `QDateTime` in logging and potentially by underlying config/logger modules. Install via `pip install PySide6`.
    *   `pywin32` (Windows only): Used in the example test script to list available printers. Install via `pip install pywin32`.

2.  **Ghostscript**: Ghostscript must be installed on the system where this interface will be used. The interface will attempt to find common installations (e.g., Ghostscript 10.04.0) or use the system's PATH. If Ghostscript is installed in a non-standard location, you may need to provide the path to `gswin64c.exe` (or `gswin32c.exe` / `gs`) directly to the `print_sku_locally` function.

3.  **Application Configuration**:
    *   `printer_config.json`: This file must exist in the same directory as `local_printer_interface.py` (or where the main application expects it). It needs to be correctly configured, especially the `temuskupdf_folder` (pointing to your SKU PDFs) and `other_folder` (pointing to where common files like separator PDFs are stored).
        Example `printer_config.json` structure:
        ```json
        {
            "temuskupdf_folder": "D:\\temuskupdf",
            "other_folder": "D:\\other_pdfs",
            "print_set_file": "print_set.txt"
            // ... other settings
        }
        ```
    *   `print_log.csv`: The print logger will write to this file. Ensure it's writable.

4.  **PDF Files**:
    *   SKU PDF files should be present in the directory specified by `temuskupdf_folder` in `printer_config.json`. The interface expects SKUs to map to PDF filenames (e.g., SKU "MYSKU" maps to "MYSKU.pdf").
    *   If using the separator page feature, the separator PDF (default: "分割72.pdf") must exist in the `other_folder`.

## Using the Interface

### 1. Importing the Module

```python
from local_printer_interface import get_sku_info, print_sku_locally
```

### 2. Getting SKU Information

The `get_sku_info` function retrieves details about the PDF associated with an SKU.

```python
sku_to_check = "YOUR_SKU_HERE"  # e.g., "TEST1001"
sku_details = get_sku_info(sku_to_check)

if sku_details:
    print(f"Details for SKU '{sku_to_check}':")
    print(f"  Full Path: {sku_details['full_path']}")
    print(f"  Filename: {sku_details['filename']}")
    print(f"  Width (cm): {sku_details['width_cm']}")
    print(f"  Height (cm): {sku_details['height_cm']}")
    print(f"  Is Landscape: {sku_details['is_landscape']}")
else:
    print(f"SKU '{sku_to_check}' not found or error retrieving info.")
```

**Return Value (`get_sku_info`)**:
A dictionary containing:
*   `'full_path'`: Absolute path to the PDF file.
*   `'filename'`: Name of the PDF file.
*   `'width_cm'`: Width of the PDF's first page in centimeters.
*   `'height_cm'`: Height of the PDF's first page in centimeters.
*   `'is_landscape'`: Boolean, `True` if the PDF page's width > height.
Or `None` if the SKU is not found or an error occurs.

### 3. Printing an SKU

The `print_sku_locally` function sends the SKU's PDF to a specified printer.

```python
sku_to_print = "YOUR_SKU_HERE"
copies = 1
# Ensure this printer name matches one recognized by your system / Ghostscript
target_printer = "Your_Printer_Name_Here" # e.g., "Microsoft Print to PDF" or "HP LaserJet"

# Optional: Path to Ghostscript executable if not found automatically
# gs_exe_path = r"C:\Program Files\gs\gs10.04.0\bin\gswin64c.exe"

success = print_sku_locally(
    sku=sku_to_print,
    quantity=copies,
    printer_name=target_printer,
    # gs_path=gs_exe_path,  # Uncomment if providing GS path explicitly
    # print_separator=True, # Default is True
    # separator_pdf_name="my_custom_separator.pdf" # Default is "分割72.pdf"
)

if success:
    print(f"Successfully submitted SKU '{sku_to_print}' for printing.")
else:
    print(f"Failed to print SKU '{sku_to_print}'. Check console output for errors.")

```

**Arguments for `print_sku_locally`**:

*   `sku` (str): The SKU to print (e.g., "MYSKU" or "MYSKU.pdf").
*   `quantity` (int): Number of copies to print.
*   `printer_name` (str): The exact name of the target printer as recognized by the system (and Ghostscript's `-sOutputFile=%printer%<name>` syntax).
*   `gs_path` (Optional[str], default=None): Explicit path to the Ghostscript executable. If `None`, the function tries to find it.
*   `temuskupdf_folder` (Optional[str], default=None): Explicit path to the SKU PDF folder. If `None`, uses value from `printer_config.json`.
*   `other_folder` (Optional[str], default=None): Explicit path to the folder for other files (like separators). If `None`, uses value from `printer_config.json`.
*   `print_separator` (bool, default=True): If `True`, attempts to print a separator page after the main document.
*   `separator_pdf_name` (str, default="分割72.pdf"): Filename of the separator PDF located in `other_folder`.

**Return Value (`print_sku_locally`)**:
*   `True` if the main print job was successfully submitted to Ghostscript and logged.
*   `False` if any error occurred (e.g., SKU not found, Ghostscript error, file not found). Check the console for error messages.

## Troubleshooting

*   **"Ghostscript executable not found"**:
    *   Ensure Ghostscript is installed and its `bin` directory is in your system's PATH.
    *   Or, provide the full path to `gswin64c.exe` (or equivalent) via the `gs_path` argument in `print_sku_locally`.
*   **"PDF file not found"**:
    *   Verify the SKU and that the corresponding PDF (e.g., `SKU.pdf`) exists in the `temuskupdf_folder` defined in `printer_config.json`.
    *   Ensure `temuskupdf_folder` in `printer_config.json` is correct.
*   **Print job doesn't appear / Printer error**:
    *   Double-check the `printer_name` argument. It must exactly match a printer installed on your system.
    *   Check Ghostscript command output in the console for specific errors from the printer or Ghostscript.
    *   The `-sDEVICE=mswinpr2` is Windows-specific. This interface is primarily intended for Windows.
*   **Separator page not printing**:
    *   Ensure `print_separator=True`.
    *   Verify the `separator_pdf_name` exists in the `other_folder` specified in `printer_config.json` (or passed as an argument).
    *   Check that `other_folder` is correctly configured.

## Example Script

The `local_printer_interface.py` file itself contains an `if __name__ == "__main__":` block with example usage. You can run this script directly (`python local_printer_interface.py`) to test its functionality. Remember to:
1.  Have Ghostscript installed.
2.  Modify `test_printer` variable in the script to a printer name available on your system (e.g., "Microsoft Print to PDF" for testing without physical printing, which will prompt to save a PDF).
3.  The script will create dummy `printer_config.json`, `test_pdfs/TESTSKU.pdf` and `test_other_pdfs/dummy_separator.pdf` if they don't exist, for basic testing. For real use, configure `printer_config.json` to point to your actual PDF directories.

This should provide a good starting point for integrating this local printing capability into your Python projects.
```
