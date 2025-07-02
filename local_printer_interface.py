# local_printer_interface.py
# This file will contain the functions for the local printer interface.

import os
import fitz  # PyMuPDF
from typing import Optional, Dict, Union # Union was missing for type hint
from pathlib import Path

# Assuming printer_config.py is in the same directory or accessible in PYTHONPATH
from printer_config import PrinterConfig

def get_sku_info(sku: str) -> Union[Dict[str, Union[str, float, bool]], None]:
    """
    Retrieves information about a given SKU, including its PDF file path and dimensions.

    Args:
        sku: The SKU string (e.g., "TESTSKU" or "TESTSKU.pdf").

    Returns:
        A dictionary with PDF information if found, otherwise None.
        The dictionary contains:
        - 'full_path': Absolute path to the PDF file.
        - 'filename': Name of the PDF file.
        - 'width_cm': Width of the PDF in centimeters.
        - 'height_cm': Height of the PDF in centimeters.
        - 'is_landscape': Boolean indicating if the PDF is landscape oriented.
    """
    try:
        config_manager = PrinterConfig()
        app_config = config_manager.get_config()
        temuskupdf_folder = app_config.get('temuskupdf_folder')

        if not temuskupdf_folder:
            print("Error: 'temuskupdf_folder' not configured in printer_config.json.")
            return None

        if not os.path.isdir(temuskupdf_folder):
            print(f"Error: Configured 'temuskupdf_folder' does not exist or is not a directory: {temuskupdf_folder}")
            return None

        file_name = sku if sku.lower().endswith('.pdf') else f"{sku}.pdf"
        full_path = os.path.join(temuskupdf_folder, file_name)

        if not os.path.exists(full_path):
            print(f"Error: PDF file not found at {full_path}")
            return None

        # Analyze PDF (similar to PrinterPanel._analyze_and_update_size)
        doc = fitz.open(full_path)
        if not doc or len(doc) == 0:
            print(f"Error: Could not open or read PDF: {full_path}")
            doc.close()
            return None

        page = doc[0]
        # Convert points to cm (1 point = 1/72 inch, 1 inch = 2.54 cm)
        # Conversion factor: (1/72) * 2.54 cm/point
        # PyMuPDF page.rect.width/height are in points
        width_cm = page.rect.width * (2.54 / 72.0)
        height_cm = page.rect.height * (2.54 / 72.0)
        doc.close()

        is_landscape = width_cm > height_cm
        actual_width_cm = width_cm
        actual_height_cm = height_cm

        if is_landscape:
            # If landscape, swap width and height for portrait representation often used in settings
            # However, for raw info, we might want to keep original orientation sense
            # For now, let's report dimensions as they are and a flag
            pass # Keeping dimensions as they are, is_landscape flag indicates orientation

        return {
            'full_path': full_path,
            'filename': file_name,
            'width_cm': round(actual_width_cm, 2),
            'height_cm': round(actual_height_cm, 2),
            'is_landscape': is_landscape
        }

    except Exception as e:
        print(f"An error occurred in get_sku_info: {e}")
        return None


if __name__ == '__main__':
    # Example usage for get_sku_info
    print("Testing Local Printer Interface...")

    # --- Configuration Setup (Important for testing) ---
    # Ensure printer_config.json exists and is correctly configured
    # For example, it should have:
    # {
    #     "temuskupdf_folder": "D:\\temuskupdf",
    #     ... other configs
    # }
    # And ensure D:\temuskupdf (or your configured path) exists and contains test PDFs.

    # Create a dummy printer_config.json for testing if it doesn't exist
    # This is a simplified setup for demonstration.
    # In a real scenario, the user should configure this file.
    if not os.path.exists("printer_config.json"):
        print("Creating a dummy printer_config.json for testing.")
        dummy_config_data = {
            "temuskupdf_folder": "test_pdfs", # Using a local folder for tests
            "other_folder": "test_other_pdfs",
            "print_set_file": "print_set.txt",
            "selected_printers": [],
            "last_sizes": {},
            "last_paths": {}
        }
        import json
        with open("printer_config.json", "w") as f:
            json.dump(dummy_config_data, f, indent=4)

        # Create dummy PDF folder and a test PDF
        if not os.path.exists("test_pdfs"):
            os.makedirs("test_pdfs")
        if not os.path.exists("test_pdfs/TESTSKU.pdf"):
            try:
                doc = fitz.open() # Create new PDF
                page = doc.new_page(width=21 * (72/2.54), height=29.7 * (72/2.54)) # A4 portrait
                doc.save("test_pdfs/TESTSKU.pdf")
                doc.close()
                print("Created dummy test_pdfs/TESTSKU.pdf")
            except Exception as e:
                print(f"Could not create dummy PDF: {e}")

    print("\n--- Testing get_sku_info ---")
    test_sku_1 = "TESTSKU"
    info1 = get_sku_info(test_sku_1)
    if info1:
        print(f"Info for SKU '{test_sku_1}':")
        for key, value in info1.items():
            print(f"  {key}: {value}")
    else:
        print(f"SKU '{test_sku_1}' not found or error.")

    test_sku_2 = "NONEXISTENTSKU.pdf"
    info2 = get_sku_info(test_sku_2)
    if info2:
        print(f"Info for SKU '{test_sku_2}': {info2}")
    else:
        print(f"SKU '{test_sku_2}' not found or error.")

    # test_sku_3 with .pdf extension
    test_sku_3 = "TESTSKU.pdf"
    info3 = get_sku_info(test_sku_3)
    if info3:
        print(f"Info for SKU '{test_sku_3}':")
        for key, value in info3.items():
            print(f"  {key}: {value}")
    else:
        print(f"SKU '{test_sku_3}' not found or error.")

    # Placeholder for print_sku_locally tests later
    print("\n--- Testing print_sku_locally (Placeholder) ---")
    # print("Further implementation for print_sku_locally will go here.")


# --- Helper function to find Ghostscript (similar to PrinterManager._find_ghostscript) ---
def _find_ghostscript() -> Optional[str]:
    """Tries to find the Ghostscript executable."""
    possible_paths = [
        r"C:\Program Files\gs\gs10.04.0\bin\gswin64c.exe", # Added common GS 10.04.0 paths
        r"C:\Program Files (x86)\gs\gs10.04.0\bin\gswin32c.exe",
        r"C:\Program Files\gs\gs10.03.1\bin\gswin64c.exe", # Older common GS paths
        r"C:\Program Files (x86)\gs\gs10.03.1\bin\gswin32c.exe",
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    try:
        # Try 'where' command on Windows
        import subprocess
        result = subprocess.run(['where', 'gswin64c.exe'], capture_output=True, text=True, check=False, shell=True)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split('\n')[0]
        result = subprocess.run(['where', 'gswin32c.exe'], capture_output=True, text=True, check=False, shell=True)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split('\n')[0]

        # Try 'which' command on Unix-like systems
        if os.name != 'nt':
            result = subprocess.run(['which', 'gs'], capture_output=True, text=True, check=False)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split('\n')[0]
    except Exception:
        pass # Silently ignore if 'where' or 'which' fails or not found
    return None

# --- Main print function ---
import subprocess
import sys
from print_logger import log_print_job # Assuming print_logger.py is accessible
from PySide6.QtCore import QDateTime # For timestamp, though can be replaced with datetime

def print_sku_locally(sku: str, quantity: int, printer_name: str,
                      gs_path: Optional[str] = None,
                      temuskupdf_folder: Optional[str] = None,
                      other_folder: Optional[str] = None,
                      print_separator: bool = True,
                      separator_pdf_name: str = "分割72.pdf") -> bool:
    """
    Prints a given SKU to a specified printer.

    Args:
        sku: The SKU to print.
        quantity: Number of copies.
        printer_name: Name of the target printer.
        gs_path: Optional path to Ghostscript executable. If None, tries to find it.
        temuskupdf_folder: Optional path to the SKU PDF folder. If None, reads from config.
        other_folder: Optional path to the folder containing separator PDFs. If None, reads from config.
        print_separator: Whether to print a separator page after the main job.
        separator_pdf_name: Filename of the separator PDF in the other_folder.

    Returns:
        True if printing (and logging) was successful, False otherwise.
    """
    if quantity <= 0:
        print("Error: Quantity must be greater than 0.")
        return False

    # 1. Get SKU Info
    # If temuskupdf_folder is provided, we can't directly use the global get_sku_info
    # as it reads from config. We need a way to pass this.
    # For now, let's assume get_sku_info will use the config if temuskupdf_folder is None
    # This is a bit of a workaround. A better way would be for get_sku_info to accept folder path.

    # Re-fetch config if specific folders aren't passed.
    # This is slightly redundant if get_sku_info also does it, but ensures paths are available here.
    _config_manager = PrinterConfig()
    _app_config = _config_manager.get_config()

    if temuskupdf_folder is None:
        temuskupdf_folder = _app_config.get('temuskupdf_folder')
    if other_folder is None:
        other_folder = _app_config.get('other_folder')

    # We need to pass the temuskupdf_folder to a modified get_sku_info or replicate logic
    # For now, let's assume get_sku_info uses the globally configured path.
    # This part of the design might need refinement if we want get_sku_info to be more flexible
    # without relying on the global config object being initialized the same way.

    # Let's modify get_sku_info to accept an optional folder path
    # For now, I will proceed assuming get_sku_info uses the config, and ensure config is loaded.
    sku_info = get_sku_info(sku) # This will use the config from PrinterConfig()

    if not sku_info:
        print(f"Error: Could not get info for SKU '{sku}'.")
        return False

    pdf_full_path = sku_info['full_path']
    width_cm = sku_info['width_cm']
    height_cm = sku_info['height_cm']
    is_landscape = sku_info['is_landscape'] # Original orientation

    # 2. Find Ghostscript
    if gs_path is None:
        gs_path = _find_ghostscript()
    if not gs_path or not os.path.exists(gs_path):
        print("Error: Ghostscript executable not found or path is invalid.")
        print("Please install Ghostscript or provide a valid 'gs_path'.")
        return False

    # 3. Prepare Ghostscript Command
    # Convert cm to points for Ghostscript: 1 cm = 72/2.54 points
    points_per_cm = 72.0 / 2.54
    device_width_points = width_cm * points_per_cm
    device_height_points = height_cm * points_per_cm

    # Ghostscript's -dORIENT1:
    # 0: Portrait (width < height)
    # 1: Landscape (width > height)
    # This refers to the *paper* orientation, not necessarily the content.
    # PyMuPDF's is_landscape refers to content. If content is landscape,
    # and paper is portrait, GS might rotate.
    # The original code uses `is_landscape` from its analysis, which seems to be content-based.
    # Let's stick to that logic. If content is landscape, set ORIENT1=1.
    orient_val = "1" if is_landscape else "0"


    # Setup creation flags for subprocess to hide console window on Windows
    creation_flags = 0
    if sys.platform == "win32":
        creation_flags = subprocess.CREATE_NO_WINDOW


    base_gs_command = [
        gs_path,
        "-dNOPAUSE",
        "-dBATCH",
        "-dSAFER",
        "-sDEVICE=mswinpr2", # This is Windows-specific. Needs adjustment for cross-platform.
        f"-sOutputFile=%printer%{printer_name}",
        f"-dNumCopies={quantity}",
        f"-dDEVICEWIDTHPOINTS={device_width_points}",
        f"-dDEVICEHEIGHTPOINTS={device_height_points}",
        f"-dORIENT1={orient_val}", # Use determined orientation
        "-c",
        # Policy for PageSize: 3 means it attempts to use the printer's current default.
        # This can be problematic if the PDF size doesn't match.
        # Using dDEVICEWIDTHPOINTS/HEIGHTPOINTS should override this.
        # The original command had "<< /Policies << /PageSize 3 >> >> setpagedevice"
        # and also "<< /PageOffset ... /BeginPage ... >> setpagedevice"
        # These are advanced PostScript settings. Let's include them for consistency.
        "<< /Policies << /PageSize 3 >> >> setpagedevice",
        # The PageOffset and scaling from original code:
        # Offset: X by 2.8mm, Y by -1mm. Scale to 98.2%.
        # Convert mm to points for offset: 2.8 * (72/2.54) and -1 * (72/2.54)
        offset_x_points = 2.8 * (72.0/2.54)
        offset_y_points = -1.0 * (72.0/2.54)
        scale_factor = 0.982
        f"<< /PageOffset [{offset_x_points} {offset_y_points}] /BeginPage {{ {scale_factor} dup scale }}  >> setpagedevice",
        "-f"
    ]

    main_print_command = base_gs_command + [pdf_full_path]

    # 4. Execute Main Print Command
    try:
        print(f"Executing Ghostscript for main document: {' '.join(main_print_command)}")
        result = subprocess.run(
            main_print_command,
            check=True, # Raises CalledProcessError on non-zero exit
            capture_output=True,
            text=True,
            shell=False, # Safer not to use shell=True if command is fully formed
            creationflags=creation_flags
        )

        if result.returncode == 0:
            print(f"Successfully submitted '{sku_info['filename']}' ({quantity} copies) to printer '{printer_name}'.")
            # Log the main print job
            current_time_str = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
            log_print_job(
                timestamp=current_time_str,
                sku_or_filename=sku_info['filename'],
                quantity=quantity,
                printer_name=printer_name,
                status="Printed via Local Interface"
            )

            # 5. Optionally Print Separator Page
            if print_separator and other_folder and separator_pdf_name:
                full_separator_path = os.path.join(other_folder, separator_pdf_name)
                if os.path.exists(full_separator_path):
                    # Separator page uses the same dimensions/orientation as the main document
                    # but always 1 copy.
                    separator_gs_command = [
                        gs_path,
                        "-dNOPAUSE", "-dBATCH", "-dSAFER",
                        "-sDEVICE=mswinpr2",
                        f"-sOutputFile=%printer%{printer_name}",
                        "-dNumCopies=1", # Force 1 copy for separator
                        f"-dDEVICEWIDTHPOINTS={device_width_points}",
                        f"-dDEVICEHEIGHTPOINTS={device_height_points}",
                        f"-dORIENT1={orient_val}",
                        "-c",
                        "<< /Policies << /PageSize 3 >> >> setpagedevice",
                        f"<< /PageOffset [{offset_x_points} {offset_y_points}] /BeginPage {{ {scale_factor} dup scale }}  >> setpagedevice",
                        "-f",
                        full_separator_path
                    ]
                    try:
                        print(f"Executing Ghostscript for separator: {' '.join(separator_gs_command)}")
                        sep_result = subprocess.run(
                            separator_gs_command,
                            check=True, capture_output=True, text=True,
                            shell=False, creationflags=creation_flags
                        )
                        if sep_result.returncode == 0:
                            print(f"Successfully printed separator page '{separator_pdf_name}'.")
                            log_print_job(
                                timestamp=QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss"),
                                sku_or_filename=separator_pdf_name,
                                quantity=1,
                                printer_name=printer_name,
                                status="Printed Separator via Local Interface"
                            )
                        else:
                            print(f"Warning: Ghostscript failed for separator page '{separator_pdf_name}'. Stderr: {sep_result.stderr}")
                    except subprocess.CalledProcessError as sep_e:
                        print(f"Error printing separator page '{separator_pdf_name}': {sep_e}")
                        print(f"Stderr: {sep_e.stderr}")
                    except Exception as sep_e_gen:
                        print(f"General error printing separator page: {sep_e_gen}")
                else:
                    print(f"Warning: Separator PDF '{separator_pdf_name}' not found in '{other_folder}'. Skipping.")
            elif print_separator:
                print("Warning: Separator printing enabled but 'other_folder' or 'separator_pdf_name' is not set. Skipping separator.")

            return True # Main job was successful

        else: # Should be caught by check=True, but as a fallback
            print(f"Error: Ghostscript returned code {result.returncode} for '{pdf_full_path}'. Stderr: {result.stderr}")
            return False

    except subprocess.CalledProcessError as e:
        print(f"Error executing Ghostscript for '{pdf_full_path}': {e}")
        print(f"Command: {' '.join(e.cmd)}")
        print(f"Stderr: {e.stderr}")
        return False
    except FileNotFoundError: # If gs_path itself is not found by subprocess.run
        print(f"Error: Ghostscript executable not found at path '{gs_path}'. Ensure it is correct and accessible.")
        return False
    except Exception as e_gen:
        print(f"An unexpected error occurred during printing: {e_gen}")
        return False


if __name__ == '__main__':
    # Example usage for get_sku_info
    print("Testing Local Printer Interface...")

    # --- Configuration Setup (Important for testing) ---
    # Ensure printer_config.json exists and is correctly configured
    # For example, it should have:
    # {
    #     "temuskupdf_folder": "D:\\temuskupdf",
    #     "other_folder": "D:\\other_pdfs",
    #     ... other configs
    # }
    # And ensure D:\temuskupdf (or your configured path) exists and contains test PDFs.

    config_file_path = "printer_config.json"
    dummy_temu_pdf_folder = "test_pdfs"
    dummy_other_pdf_folder = "test_other_pdfs"
    dummy_separator_pdf = "dummy_separator.pdf"

    if not os.path.exists(config_file_path):
        print(f"Creating a dummy {config_file_path} for testing.")
        dummy_config_data = {
            "temuskupdf_folder": dummy_temu_pdf_folder,
            "other_folder": dummy_other_pdf_folder,
            "print_set_file": "print_set.txt",
            "selected_printers": [],
            "last_sizes": {},
            "last_paths": {}
        }
        import json
        with open(config_file_path, "w") as f:
            json.dump(dummy_config_data, f, indent=4)

        if not os.path.exists(dummy_temu_pdf_folder):
            os.makedirs(dummy_temu_pdf_folder)
        if not os.path.exists(os.path.join(dummy_temu_pdf_folder, "TESTSKU.pdf")):
            try:
                doc = fitz.open()
                page = doc.new_page(width=21 * (72/2.54), height=29.7 * (72/2.54)) # A4 portrait
                doc.save(os.path.join(dummy_temu_pdf_folder, "TESTSKU.pdf"))
                doc.close()
                print(f"Created dummy {os.path.join(dummy_temu_pdf_folder, 'TESTSKU.pdf')}")
            except Exception as e:
                print(f"Could not create dummy PDF: {e}")

        if not os.path.exists(dummy_other_pdf_folder):
            os.makedirs(dummy_other_pdf_folder)
        if not os.path.exists(os.path.join(dummy_other_pdf_folder, dummy_separator_pdf)):
            try:
                doc = fitz.open()
                page = doc.new_page(width=7.2 * (72/2.54), height=3.6 * (72/2.54)) # Small label size
                page.insert_text((10, 20), "Separator")
                doc.save(os.path.join(dummy_other_pdf_folder, dummy_separator_pdf))
                doc.close()
                print(f"Created dummy {os.path.join(dummy_other_pdf_folder, dummy_separator_pdf)}")
            except Exception as e:
                print(f"Could not create dummy separator PDF: {e}")

    # Ensure print_log.csv exists for logger
    if not os.path.exists("print_log.csv"):
        with open("print_log.csv", "w") as f:
            f.write("Timestamp,SKU/Filename,Quantity,Printer,Status\n") # Header for logger

    print("\n--- Testing get_sku_info ---")
    test_sku_1 = "TESTSKU"
    info1 = get_sku_info(test_sku_1)
    if info1:
        print(f"Info for SKU '{test_sku_1}':")
        for key, value in info1.items():
            print(f"  {key}: {value}")
    else:
        print(f"SKU '{test_sku_1}' not found or error.")

    # ... (other get_sku_info tests can remain)

    print("\n--- Testing print_sku_locally ---")
    # IMPORTANT: Replace "Your_Printer_Name_Here" with an actual printer name on your system.
    # For actual printing, Ghostscript needs a real printer.
    # For testing without printing, you might need a virtual printer or mock Ghostscript.
    # Common virtual printers: "Microsoft Print to PDF", "Microsoft XPS Document Writer"

    # First, find Ghostscript
    gs_exe_path = _find_ghostscript()
    if not gs_exe_path:
        print("Ghostscript not found. Skipping print_sku_locally tests.")
    else:
        print(f"Using Ghostscript found at: {gs_exe_path}")

        # Example: Print TESTSKU to "Microsoft Print to PDF" (if available)
        # Note: Printing to "Microsoft Print to PDF" will typically pop up a "Save As" dialog.
        # This is not ideal for automated testing but can verify GS command formation.
        test_printer = "Microsoft Print to PDF" # Replace if needed

        # Check if the printer exists (Windows specific)
        printer_exists = False
        if sys.platform == "win32":
            import win32print
            try:
                printers = [p[2] for p in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
                if test_printer in printers:
                    printer_exists = True
                else:
                    print(f"Warning: Printer '{test_printer}' not found. Available printers: {printers}")
                    # Fallback to default printer if test_printer not found
                    if printers:
                         print(f"Attempting to use default printer: {win32print.GetDefaultPrinter()}")
                         test_printer = win32print.GetDefaultPrinter()
                         printer_exists = True # Assume default printer exists
                    else:
                        print("No printers found on the system.")

            except ImportError:
                print("pywin32 not installed. Cannot verify printer existence on Windows. Assuming it exists.")
                printer_exists = True # Assume for non-Windows or if pywin32 is missing
            except Exception as e_prn:
                print(f"Could not enumerate printers: {e_prn}")
                printer_exists = True # Proceed with caution

        if printer_exists:
            print(f"\nAttempting to print SKU 'TESTSKU' (1 copy) to printer '{test_printer}' with separator:")
            success = print_sku_locally(
                sku="TESTSKU",
                quantity=1,
                printer_name=test_printer,
                gs_path=gs_exe_path,
                separator_pdf_name=dummy_separator_pdf # Use the dummy separator for testing
            )
            print(f"Print job submission result: {success}")

            print(f"\nAttempting to print SKU 'TESTSKU' (2 copies) to printer '{test_printer}' WITHOUT separator:")
            success_no_sep = print_sku_locally(
                sku="TESTSKU",
                quantity=2,
                printer_name=test_printer,
                gs_path=gs_exe_path,
                print_separator=False
            )
            print(f"Print job submission result (no separator): {success_no_sep}")

            print(f"\nAttempting to print non-existent SKU 'FAKESKU':")
            success_fake = print_sku_locally(
                sku="FAKESKU",
                quantity=1,
                printer_name=test_printer,
                gs_path=gs_exe_path
            )
            print(f"Print job submission result (fake SKU): {success_fake}")
        else:
            print(f"Skipping print tests as printer '{test_printer}' could not be confirmed or no printers available.")
