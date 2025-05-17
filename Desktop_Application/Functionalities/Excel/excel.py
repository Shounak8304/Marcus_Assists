import win32com.client as win32
import customtkinter as ctk
import os
import re
from threading import Lock

class ExcelAutomationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel Automation")
        self.root.geometry("400x300")

        # Position at bottom-right corner
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 400
        window_height = 300


        # Excel variables
        self.excel = None
        self.workbook = None
        self.sheet = None

        # Lock for thread-safe output
        self.print_lock = Lock()

        # GUI Layout
        self.output_text = ctk.CTkTextbox(self.root, width=380, height=300, state='disabled')
        self.output_text.pack(padx=10, pady=10)


        # Start Excel initialization
        self.initialize_excel()

    def print_to_gui(self, text):
        """Thread-safe method to print to the GUI textbox."""
        with self.print_lock:
            self.output_text.configure(state='normal')
            self.output_text.insert('end', text + '\n')
            self.output_text.see('end')
            self.output_text.configure(state='disabled')

    def initialize_excel(self):
        self.print_to_gui("Initializing Excel...")
        self.print_to_gui("Do you want to edit an existing file or create a new one? (existing/new): ")
        # Wait for main.py to send "existing" or "new" via handle_command

    def handle_initial_choice(self, user_choice):
        if user_choice == "existing":
            try:
                self.excel = win32.GetActiveObject("Excel.Application")
                workbooks = self.excel.Workbooks
                if workbooks.Count > 0:
                    self.print_to_gui("\nOpen Workbooks:")
                    for i in range(1, workbooks.Count + 1):
                        self.print_to_gui(f"{i}. {workbooks.Item(i).Name}")
                    self.print_to_gui("\nEnter the workbook number or name to select: ")
                    return "awaiting_workbook_choice"
                else:
                    self.print_to_gui("No open workbooks found. Please open a workbook first or create a new one.")
                    self.initialize_excel()
            except Exception:
                self.print_to_gui("No active Excel instance found. Please open a workbook first or choose to create a new one.")
                self.initialize_excel()
        elif user_choice == "new":
            self.print_to_gui("Creating a new workbook...")
            self.excel = win32.Dispatch("Excel.Application")
            self.excel.Visible = True
            self.workbook = self.excel.Workbooks.Add()
            self.sheet = self.workbook.ActiveSheet
            self.print_to_gui(f"Active Sheet: {self.sheet.Name}")
            self.print_to_gui("Ready for commands (e.g., add, save, exit)")
        else:
            self.print_to_gui("Invalid choice. Please enter 'existing' or 'new'.")
            self.initialize_excel()
        return None

    def handle_workbook_choice(self, choice):
        try:
            workbooks = self.excel.Workbooks
            if choice.isdigit():
                choice = int(choice)
                if 1 <= choice <= workbooks.Count:
                    self.workbook = workbooks.Item(choice)
                else:
                    self.print_to_gui("Invalid selection. Enter a valid number from the list.")
                    self.print_to_gui("\nEnter the workbook number or name to select: ")
                    return "awaiting_workbook_choice"
            else:
                self.workbook = workbooks.Item(choice)
            self.print_to_gui(f"Selected Workbook: {self.workbook.Name}")
            sheets = self.workbook.Sheets
            self.print_to_gui("\nAvailable Sheets:")
            for i in range(1, sheets.Count + 1):
                self.print_to_gui(f"{i}. {sheets.Item(i).Name}")
            self.print_to_gui("\nEnter the sheet number or name to select (press Enter for default first sheet): ")
            return "awaiting_sheet_choice"
        except Exception:
            self.print_to_gui("Invalid selection. Please enter a valid workbook number or name.")
            self.print_to_gui("\nEnter the workbook number or name to select: ")
            return "awaiting_workbook_choice"

    def handle_sheet_choice(self, sheet_choice):
        try:
            sheets = self.workbook.Sheets
            if not sheet_choice:
                self.sheet = sheets.Item(1)
            elif sheet_choice.isdigit():
                sheet_choice = int(sheet_choice)
                if 1 <= sheet_choice <= sheets.Count:
                    self.sheet = sheets.Item(sheet_choice)
                else:
                    self.print_to_gui("Invalid sheet number. Enter a valid number from the list.")
                    self.print_to_gui("\nEnter the sheet number or name to select (press Enter for default first sheet): ")
                    return "awaiting_sheet_choice"
            else:
                self.sheet = sheets.Item(sheet_choice)
            self.print_to_gui(f"Selected Sheet: {self.sheet.Name}")
            self.print_to_gui("Ready for commands (e.g., add, save, exit)")
            return None
        except Exception:
            self.print_to_gui("Invalid sheet selection. Please enter a valid sheet number or name.")
            self.print_to_gui("\nEnter the sheet number or name to select (press Enter for default first sheet): ")
            return "awaiting_sheet_choice"

    def cell_reference_to_row_col(self, cell_ref):
        match = re.match(r"([A-Z]+)(\d+)", cell_ref.upper())
        if match:
            col_letter, row = match.groups()
            col = sum((ord(char) - 64) * (26 ** i) for i, char in enumerate(reversed(col_letter)))
            return int(row), col
        else:
            raise ValueError("Invalid cell reference format. Use a format like 'A1'.")

    def apply_formatting(self, start_row, start_col, end_row, end_col, formatting_options):
        for row in range(start_row, end_row + 1):
            for col in range(start_col, end_col + 1):
                cell = self.sheet.Cells(row, col)
                if 'bold' in formatting_options:
                    cell.Font.Bold = True
                if 'italic' in formatting_options:
                    cell.Font.Italic = True
                if 'underline' in formatting_options:
                    cell.Font.Underline = True
                if 'double underline' in formatting_options:
                    cell.Font.Underline = 2

    def create_table(self, start_row, start_col, rows, cols, row_data_list):
        for r, row_data in enumerate(row_data_list):
            if r < rows:
                cell_values = row_data.split(',')
                for c, value in enumerate(cell_values, start=0):
                    if c < cols:
                        self.sheet.Cells(start_row + r, start_col + c).Value = value.strip()
        for r in range(start_row, start_row + rows):
            for c in range(start_col, start_col + cols):
                cell = self.sheet.Cells(r, c)
                borders = cell.Borders
                for border in range(7, 13):
                    borders(border).LineStyle = 1
                    borders(border).Weight = 2
        self.print_to_gui(f"Table created at starting cell ({start_row}, {start_col}).")

    def apply_borders(self, start_row, start_col, end_row, end_col, bold=False):
        for row in range(start_row, end_row + 1):
            for col in range(start_col, end_col + 1):
                cell = self.sheet.Cells(row, col)
                borders = cell.Borders
                for border in range(7, 13):
                    borders(border).LineStyle = 1
                    borders(border).Weight = 4 if bold else 2
        self.print_to_gui(f"Borders ({'Bold' if bold else 'Normal'}) applied to range ({start_row},{start_col}) to ({end_row},{end_col}).")

    def insert_row(self, row_index):
        self.sheet.Rows(row_index).Insert()
        self.print_to_gui(f"Row {row_index} has been created.")

    def insert_column(self, column_index):
        self.sheet.Columns(column_index).Insert()
        self.print_to_gui(f"Column {column_index} has been created.")

    def delete_row(self, row_index):
        self.sheet.Rows(row_index).Delete()
        self.print_to_gui(f"Deleted row {row_index}.")

    def delete_column(self, col_index):
        self.sheet.Columns(col_index).Delete()
        self.print_to_gui(f"Deleted column {col_index}.")

    def delete_content(self, range_ref):
        try:
            self.sheet.Range(range_ref).ClearContents()
            self.print_to_gui(f"Content in range {range_ref} has been deleted.")
        except Exception as e:
            self.print_to_gui(f"Error: Unable to delete content in range {range_ref}. Details: {e}")

    def copy_content(self, source_range):
        try:
            self.sheet.Range(source_range).Copy()
            self.print_to_gui(f"Content from {source_range} copied to clipboard.")
        except Exception as e:
            self.print_to_gui(f"Error: Unable to copy content from {source_range}. Details: {e}")

    def paste_content(self, destination_range):
        try:
            self.sheet.Range(destination_range).PasteSpecial()
            self.print_to_gui(f"Content pasted into {destination_range}.")
        except Exception as e:
            self.print_to_gui(f"Error: Unable to paste content into {destination_range}. Details: {e}")

    def create_new_sheet(self, sheet_name=None):
        try:
            new_sheet = self.workbook.Sheets.Add()
            if sheet_name:
                new_sheet.Name = sheet_name
            self.print_to_gui(f"New sheet created with name '{new_sheet.Name}'.")
        except Exception as e:
            self.print_to_gui(f"Error: Unable to create new sheet. Details: {e}")

    def rename_sheet(self, sheet_identifier, new_name):
        try:
            if isinstance(sheet_identifier, int):
                sheet_to_rename = self.workbook.Sheets(sheet_identifier)
            else:
                sheet_to_rename = self.workbook.Sheets(sheet_identifier)
            sheet_to_rename.Name = new_name
            self.print_to_gui(f"Sheet renamed to '{new_name}'.")
        except Exception as e:
            self.print_to_gui(f"Error: Unable to rename sheet. Details: {e}")

    def basic_operations(self, operation, cell1, cell2, result_cell):
        try:
            row1, col1 = self.cell_reference_to_row_col(cell1)
            row2, col2 = self.cell_reference_to_row_col(cell2)
            result_row, result_col = self.cell_reference_to_row_col(result_cell)
            value1 = self.sheet.Cells(row1, col1).Value
            value2 = self.sheet.Cells(row2, col2).Value

            if value1 is None or value2 is None:
                self.print_to_gui(f"Error: One or both of the cells ({cell1}, {cell2}) are empty.")
                return

            if operation == 'add':
                result = value1 + value2
            elif operation == 'subtract':
                result = value1 - value2
            elif operation == 'multiply':
                result = value1 * value2
            elif operation == 'divide':
                if value2 == 0:
                    self.print_to_gui("Error: Division by zero is not allowed.")
                    return
                result = value1 / value2
            else:
                self.print_to_gui("Error: Unsupported operation.")
                return

            self.sheet.Cells(result_row, result_col).Value = result
            self.print_to_gui(f"{operation.capitalize()} result ({result}) written to cell {result_cell}.")
        except ValueError:
            self.print_to_gui("Error: Invalid cell reference format. Please provide references like 'A1'.")
        except Exception as e:
            self.print_to_gui(f"Error: Unable to perform the operation. Details: {e}")

    def auto_sum(self, range_ref, result_cell):
        try:
            if ':' not in range_ref:
                self.print_to_gui("Error: Provide a valid range like 'A1:A10'.")
                return
            start_ref, end_ref = range_ref.split(':')
            start_row, start_col = self.cell_reference_to_row_col(start_ref)
            end_row, end_col = self.cell_reference_to_row_col(end_ref)
            result_row, result_col = self.cell_reference_to_row_col(result_cell)
            total = 0
            for row in range(start_row, end_row + 1):
                for col in range(start_col, end_col + 1):
                    value = self.sheet.Cells(row, col).Value
                    if value is not None:
                        total += value
            self.sheet.Cells(result_row, result_col).Value = total
            self.print_to_gui(f"Auto-sum total ({total}) written to cell {result_cell}.")
        except ValueError:
            self.print_to_gui("Error: Invalid cell reference format. Please provide references like 'A1:A10'.")
        except Exception as e:
            self.print_to_gui(f"Error: Unable to perform the auto-sum. Details: {e}")

    def save_workbook(self, file_name=None):
        try:
            if file_name:
                file_path = os.path.join(os.getcwd(), file_name + ".xlsx")
                self.workbook.SaveAs(file_path)
                self.print_to_gui(f"Workbook saved as: {file_path}")
            else:
                file_path = self.workbook.FullName if self.workbook.Path else None
                if not file_path:
                    self.print_to_gui("Enter file name to save as (without extension): ")
                    return "awaiting_save_filename"
                else:
                    self.workbook.Save()
                    self.print_to_gui(f"Workbook saved as: {file_path}")
        except Exception as e:
            self.print_to_gui(f"Error: Unable to save the workbook. Details: {e}")

    def handle_command(self, command):
        """Handle commands received from main.py."""
        command = command.strip().lower()
        state = getattr(self, '_state', None)  # Track state for multi-step commands

        if command == "close excel processing":
            self.print_to_gui("Exiting Excel processing.")
            self.root.quit()
            self.root.destroy()
            return

        # Handle multi-step states
        if state == "awaiting_workbook_choice":
            new_state = self.handle_workbook_choice(command)
            self._state = new_state
        elif state == "awaiting_sheet_choice":
            new_state = self.handle_sheet_choice(command)
            self._state = new_state
        elif state == "awaiting_save_filename":
            self.save_workbook(command)
            self._state = None
        elif state == "awaiting_operation_cell1":
            self._cell1 = command
            self.print_to_gui("Enter the second cell reference (e.g., B1): ")
            self._state = "awaiting_operation_cell2"
        elif state == "awaiting_operation_cell2":
            self._cell2 = command
            self.print_to_gui("Enter the cell reference to store the result (e.g., C1): ")
            self._state = "awaiting_operation_result"
        elif state == "awaiting_operation_result":
            self.basic_operations(self._operation, self._cell1, self._cell2, command)
            self._state = None
        elif state == "awaiting_auto_sum_range":
            self._range_ref = command
            self.print_to_gui("Enter the cell reference to store the sum (e.g., B1): ")
            self._state = "awaiting_auto_sum_result"
        elif state == "awaiting_auto_sum_result":
            self.auto_sum(self._range_ref, command)
            self._state = None
        elif state == "awaiting_format_range":
            self._range_ref = command
            self.print_to_gui("Enter the formatting options (comma-separated, e.g., bold, italic): ")
            self._state = "awaiting_format_options"
        elif state == "awaiting_format_options":
            formatting_options = [opt.strip() for opt in command.split(',')]
            if ':' in self._range_ref:
                start_ref, end_ref = self._range_ref.split(':')
                start_row, start_col = self.cell_reference_to_row_col(start_ref)
                end_row, end_col = self.cell_reference_to_row_col(end_ref)
            else:
                start_row, start_col = self.cell_reference_to_row_col(self._range_ref)
                end_row, end_col = start_row, start_col
            self.apply_formatting(start_row, start_col, end_row, end_col, formatting_options)
            self.print_to_gui(f"Formatting applied to range {self._range_ref}.")
            self._state = None
        elif state == "awaiting_table_cell":
            self._start_cell = command
            self.print_to_gui("Enter the number of rows for the table: ")
            self._state = "awaiting_table_rows"
        elif state == "awaiting_table_rows":
            self._rows = int(command)
            self.print_to_gui("Enter the number of columns for the table: ")
            self._state = "awaiting_table_cols"
        elif state == "awaiting_table_cols":
            self._cols = int(command)
            self.print_to_gui("Enter data for each row (comma-separated, one row per command, e.g., 1,2,3): ")
            self._table_data = []
            self._state = "awaiting_table_data"
        elif state == "awaiting_table_data":
            self._table_data.append(command)
            if len(self._table_data) < self._rows:
                self.print_to_gui(f"Enter data for row {len(self._table_data) + 1} (comma-separated): ")
            else:
                start_row, start_col = self.cell_reference_to_row_col(self._start_cell)
                self.create_table(start_row, start_col, self._rows, self._cols, self._table_data)
                self._state = None
        elif state == "awaiting_borders_range":
            self._range_ref = command
            self.print_to_gui("Do you want the borders to be 'bold' or 'normal'? ")
            self._state = "awaiting_borders_style"
        elif state == "awaiting_borders_style":
            bold = command == "bold"
            if command not in ["bold", "normal"]:
                self.print_to_gui("Invalid input. Please type 'bold' or 'normal'.")
                self.print_to_gui("Do you want the borders to be 'bold' or 'normal'? ")
            else:
                if ':' in self._range_ref:
                    start_ref, end_ref = self._range_ref.split(':')
                    start_row, start_col = self.cell_reference_to_row_col(start_ref)
                    end_row, end_col = self.cell_reference_to_row_col(end_ref)
                else:
                    start_row, start_col = self.cell_reference_to_row_col(self._range_ref)
                    end_row, end_col = start_row, start_col
                self.apply_borders(start_row, start_col, end_row, end_col, bold)
                self._state = None
        elif state == "awaiting_rename_sheet":
            self._sheet_identifier = command if command.isdigit() else int(command)
            self.print_to_gui(f"Enter the new name for the sheet '{command}': ")
            self._state = "awaiting_rename_sheet_name"
        elif state == "awaiting_rename_sheet_name":
            self.rename_sheet(self._sheet_identifier, command)
            self._state = None
        else:
            # Initial command handling
            if not self.workbook:
                new_state = self.handle_initial_choice(command)
                self._state = new_state
            elif command in ['add', 'subtract', 'multiply', 'divide']:
                self._operation = command
                self.print_to_gui("Enter the first cell reference (e.g., A1): ")
                self._state = "awaiting_operation_cell1"
            elif command == "auto sum":
                self.print_to_gui("Enter the range to sum (e.g., A1:A10): ")
                self._state = "awaiting_auto_sum_range"
            elif command == "fill rows" or command == "fill columns":
                self.print_to_gui("Not implemented yet. Use 'fill cell' or 'create table' instead.")
            elif command == "fill cell":
                self.print_to_gui("Enter the cell reference (e.g., A1): ")
                self._state = "awaiting_fill_cell_ref"
            elif state == "awaiting_fill_cell_ref":
                self._cell_ref = command
                self.print_to_gui(f"Enter the value for cell {command}: ")
                self._state = "awaiting_fill_cell_value"
            elif state == "awaiting_fill_cell_value":
                row, col = self.cell_reference_to_row_col(self._cell_ref)
                self.sheet.Cells(row, col).Value = command
                self.print_to_gui(f"Cell {self._cell_ref} updated with value: {command}")
                self._state = None
            elif command == "format":
                self.print_to_gui("Enter the range to format (e.g., A1:C3 or A1): ")
                self._state = "awaiting_format_range"
            elif command == "create table":
                self.print_to_gui("Enter the starting cell reference for the table (e.g., A1): ")
                self._state = "awaiting_table_cell"
            elif command == "apply borders":
                self.print_to_gui("Enter the range to apply borders (e.g., A1:D4): ")
                self._state = "awaiting_borders_range"
            elif command == "insert row":
                self.print_to_gui("Enter the row index where you want to insert a new row: ")
                self._state = "awaiting_insert_row"
            elif state == "awaiting_insert_row":
                self.insert_row(int(command))
                self._state = None
            elif command == "insert column":
                self.print_to_gui("Enter the column index (e.g., A, B, C): ")
                self._state = "awaiting_insert_column"
            elif state == "awaiting_insert_column":
                col_number = self.cell_reference_to_row_col(command + "1")[1]
                self.insert_column(col_number)
                self._state = None
            elif command == "delete row":
                self.print_to_gui("Enter the row number to delete (e.g., 2): ")
                self._state = "awaiting_delete_row"
            elif state == "awaiting_delete_row":
                self.delete_row(int(command))
                self._state = None
            elif command == "delete column":
                self.print_to_gui("Enter the column letter to delete (e.g., A, B, C): ")
                self._state = "awaiting_delete_column"
            elif state == "awaiting_delete_column":
                self.delete_column(command)
                self._state = None
            elif command == "delete":
                self.print_to_gui("Enter the range to delete (e.g., A1:C5): ")
                self._state = "awaiting_delete_range"
            elif state == "awaiting_delete_range":
                self.delete_content(command)
                self._state = None
            elif command == "copy":
                self.print_to_gui("Enter the source range (e.g., A1:C5): ")
                self._state = "awaiting_copy_range"
            elif state == "awaiting_copy_range":
                self.copy_content(command)
                self._state = None
            elif command == "paste":
                self.print_to_gui("Enter the destination range (e.g., E1:G5): ")
                self._state = "awaiting_paste_range"
            elif state == "awaiting_paste_range":
                self.paste_content(command)
                self._state = None
            elif command == "create sheet":
                self.print_to_gui("Enter the name for the new sheet (or leave blank for default): ")
                self._state = "awaiting_create_sheet_name"
            elif state == "awaiting_create_sheet_name":
                self.create_new_sheet(command if command else None)
                self._state = None
            elif command == "rename sheet":
                self.print_to_gui("Enter the sheet number (e.g., '2') or name (e.g., 'Sheet1') to rename: ")
                self._state = "awaiting_rename_sheet"
            elif command == "save":
                new_state = self.save_workbook()
                self._state = new_state
            elif command == "help":
                self.print_to_gui(
                    "Available Excel Commands:\n"
                    "  add, subtract, multiply, divide - Basic operations\n"
                    "  auto sum - Sum a range\n"
                    "  fill cell - Fill a single cell\n"
                    "  format - Apply formatting (bold, italic, etc.)\n"
                    "  create table - Create a table\n"
                    "  apply borders - Add borders\n"
                    "  insert row/column - Insert rows or columns\n"
                    "  delete row/column - Delete rows or columns\n"
                    "  delete - Delete content in a range\n"
                    "  copy/paste - Copy and paste ranges\n"
                    "  create sheet - Add a new sheet\n"
                    "  rename sheet - Rename a sheet\n"
                    "  save - Save the workbook\n"
                    "  close excel processing - Exit Excel"
                )
            else:
                self.print_to_gui(f"Invalid command: {command}")

def open_excel(root):
    """Entry point for starting the Excel automation GUI."""
    ctk.set_appearance_mode("dark")
    app = ExcelAutomationApp(root)
    return app

if __name__ == "__main__":
    root = ctk.CTk()
    open_excel(root)
    root.mainloop()