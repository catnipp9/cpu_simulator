import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QComboBox, QTableWidget, QTableWidgetItem, 
                             QTextEdit, QMessageBox, QGroupBox, QSpinBox,
                             QHeaderView, QScrollArea, QSplitter, QFrame)
from PyQt5.QtCore import Qt

from cpu import CPU
from models import Memory 
from validator import Validator

class CPUApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cpu = None
        self.instruction_addresses = []
        self.data_addresses = set()
        self.data_inputs = {}
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Simple CPU Simulator  |  Jamel P. Hadjirasul")
        self.setGeometry(100, 100, 1200, 850)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a2e;
            }
            QGroupBox {
                border: 2px solid #16213e;
                border-radius: 12px;
                margin-top: 15px;
                padding-top: 20px;
                background-color: #0f3460;
                color: #e94560;
                font-weight: bold;
                font-size: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
            }
            QLabel {
                color: #eaeaea;
                font-size: 14px;
            }
            QPushButton {
                background-color: #e94560;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #ff6b81;
            }
            QPushButton:disabled {
                background-color: #533345;
                color: #888888;
            }
            QTableWidget {
                background-color: #16213e;
                color: #eaeaea;
                alternate-background-color: #0f3460;
                font-size: 13px;
                border: none;
                border-radius: 8px;
                gridline-color: #1a1a2e;
            }
            QHeaderView::section {
                background-color: #e94560;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 8px;
                border: none;
            }
            QLineEdit, QSpinBox {
                background-color: #16213e;
                color: #eaeaea;
                border: 2px solid #0f3460;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
            QLineEdit:focus, QSpinBox:focus {
                border: 2px solid #e94560;
            }
            QComboBox {
                background-color: #16213e;
                color: #eaeaea;
                border: 2px solid #0f3460;
                border-radius: 6px;
                padding: 6px;
                font-size: 13px;
            }
            QComboBox:focus {
                border: 2px solid #e94560;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #16213e;
                color: #eaeaea;
                selection-background-color: #e94560;
            }
            QTextEdit {
                background-color: #16213e;
                color: #00ff00;
                font-size: 13px;
                font-family: 'Courier New', monospace;
                border: 2px solid #0f3460;
                border-radius: 8px;
                padding: 8px;
            }
            QScrollBar:vertical {
                background-color: #0f3460;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #e94560;
                border-radius: 6px;
            }
            QSplitter::handle {
                background-color: #1a1a2e;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        splitter = QSplitter(Qt.Horizontal)
        
        # Configuration & Control
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)
        
        # Control Panel
        control_group = QGroupBox("⚙️ Control Panel")
        control_layout = QVBoxLayout(control_group)
        
        # Program size 
        size_layout = QHBoxLayout()
        size_label = QLabel("Program Size:")
        size_label.setStyleSheet("font-weight: bold;")
        self.instruction_count = QSpinBox()
        self.instruction_count.setRange(1, 256)
        self.instruction_count.setValue(4)
        self.instruction_count.setToolTip("Number of instructions (1-256)")
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.instruction_count)
        size_layout.addStretch()
        
        self.setup_btn = QPushButton("⚡ Initialize Program")
        self.setup_btn.setToolTip("Create instruction table")
        self.setup_btn.clicked.connect(self.setup_instructions)
        
        control_layout.addLayout(size_layout)
        control_layout.addWidget(self.setup_btn)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #16213e;")
        control_layout.addWidget(line)
        
        # Execution buttons
        exec_label = QLabel("Execution Controls:")
        exec_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        control_layout.addWidget(exec_label)
        
        self.run_btn = QPushButton("▶️ Run Full Program")
        self.run_btn.setToolTip("Execute all instructions")
        self.run_btn.clicked.connect(self.run_program)
        
        self.step_btn = QPushButton("⏭️ Step Through")
        self.step_btn.setToolTip("Execute one instruction")
        self.step_btn.clicked.connect(self.step_program)
        
        self.reset_btn = QPushButton("🔄 Reset")
        self.reset_btn.setToolTip("Clear and restart")
        self.reset_btn.clicked.connect(self.reset_program)
        
        control_layout.addWidget(self.run_btn)
        control_layout.addWidget(self.step_btn)
        control_layout.addWidget(self.reset_btn)
        control_layout.addStretch()
        
        left_layout.addWidget(control_group)
        
        # Data Values Section
        self.data_group = QGroupBox("💾 Memory Data")
        self.data_layout = QVBoxLayout(self.data_group)
        left_layout.addWidget(self.data_group)
        self.data_group.hide()
        
        left_layout.addStretch()
        
        # Instructions & Output
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(15)
        
        # Instructions Table
        instr_group = QGroupBox("📝 Instruction Memory")
        instr_layout = QVBoxLayout(instr_group)
        
        self.instructions_table = QTableWidget()
        self.instructions_table.setColumnCount(3)
        self.instructions_table.setHorizontalHeaderLabels(["Address", "Instruction", "Operand"])
        self.instructions_table.setAlternatingRowColors(True)
        self.instructions_table.setToolTip("Define your program instructions")
        self.instructions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        instr_layout.addWidget(self.instructions_table)
        right_layout.addWidget(instr_group, 3)
        
        # Console Output
        output_group = QGroupBox("🖥️ Execution Console")
        output_layout = QVBoxLayout(output_group)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setToolTip("Program execution output")
        self.output_text.setPlaceholderText(">>> Waiting for program execution...\n")
        
        output_layout.addWidget(self.output_text)
        right_layout.addWidget(output_group, 2)
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(splitter)
        
        self.statusBar().showMessage("🟢 Ready to configure program")
        self.statusBar().setStyleSheet("background-color: #0f3460; color: #eaeaea; padding: 5px;")
        
        self.step_btn.setEnabled(False)
        self.run_btn.setEnabled(False)
        self.reset_btn.setEnabled(False)
    
    def clear_data_inputs(self):
        """Safely clear all data input widgets"""
        for i in reversed(range(self.data_layout.count())):
            item = self.data_layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
        
        self.data_inputs.clear()
    
    def setup_instructions(self):
        
        count = self.instruction_count.value()
        
        self.instruction_addresses = list(range(count))
        self.data_addresses.clear()
        self.clear_data_inputs()
        
        self.instructions_table.setRowCount(count)
        
        instruction_types = ["", "LOAD", "STORE", "ADD", "SUB", "HLT"]
        
        for row, address in enumerate(self.instruction_addresses):
            addr_item = QTableWidgetItem(str(address))
            addr_item.setFlags(addr_item.flags() & ~Qt.ItemIsEditable)
            addr_item.setTextAlignment(Qt.AlignCenter)
            self.instructions_table.setItem(row, 0, addr_item)
            
            instr_combo = QComboBox()
            instr_combo.addItems(instruction_types)
            instr_combo.currentTextChanged.connect(lambda text, r=row: self.on_instruction_change(r, text))
            self.instructions_table.setCellWidget(row, 1, instr_combo)
            
            operand_edit = QLineEdit()
            operand_edit.setPlaceholderText("Address")
            operand_edit.textChanged.connect(lambda text, r=row: self.on_operand_change(r, text))
            self.instructions_table.setCellWidget(row, 2, operand_edit)
            operand_edit.setEnabled(False)
        
        self.instructions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.step_btn.setEnabled(True)
        self.run_btn.setEnabled(True)
        self.reset_btn.setEnabled(True)
        self.statusBar().showMessage("🟢 Program configured - Ready to execute")
    
    def on_instruction_change(self, row, instruction):
        operand_edit = self.instructions_table.cellWidget(row, 2)
        if instruction in ["LOAD", "STORE", "ADD", "SUB"]:
            operand_edit.setEnabled(True)
            operand_edit.setPlaceholderText("Data Address")
        else:
            operand_edit.setEnabled(False)
            operand_edit.clear()
            self.update_data_inputs()
    
    def on_operand_change(self, row, operand):
        old_addresses = self.data_addresses.copy()
        self.data_addresses.clear()
        
        for r in range(self.instructions_table.rowCount()):
            instr_combo = self.instructions_table.cellWidget(r, 1)
            instruction = instr_combo.currentText()
            if instruction in ["LOAD", "STORE", "ADD", "SUB"]:
                operand_edit = self.instructions_table.cellWidget(r, 2)
                operand_text = operand_edit.text().strip()
                if operand_text:
                    try:
                        address = int(operand_text)
                        self.data_addresses.add(address)
                    except ValueError:
                        pass
        
        if self.data_addresses != old_addresses:
            self.update_data_inputs()
    
    def update_data_inputs(self):
        """Update data input fields based on current data addresses"""
        self.clear_data_inputs()
        
        if not self.data_addresses:
            self.data_group.hide()
            return
        
        self.data_group.show()
        addresses_str = ", ".join(map(str, sorted(self.data_addresses)))
        self.data_group.setTitle(f"💾 Memory Data [{addresses_str}]")
        
        sorted_addresses = sorted(self.data_addresses)
        for address in sorted_addresses:
            layout = QHBoxLayout()
            label = QLabel(f"[{address}]")
            label.setStyleSheet("font-weight: bold; min-width: 40px;")
            layout.addWidget(label)
            
            data_edit = QLineEdit()
            data_edit.setPlaceholderText("Value")
            data_edit.setText("0")
            data_edit.setProperty("address", address)
            self.data_inputs[address] = data_edit
            layout.addWidget(data_edit)
            
            container = QWidget()
            container.setLayout(layout)
            self.data_layout.addWidget(container)
    
    def get_program_data(self):
        
        instructions = {}
        data_addresses_used = set()
        
        for row in range(self.instructions_table.rowCount()):
            instr_combo = self.instructions_table.cellWidget(row, 1)
            instruction = instr_combo.currentText()
            address = int(self.instructions_table.item(row, 0).text())
            
            if instruction:
                if instruction in ["LOAD", "STORE", "ADD", "SUB"]:
                    operand_edit = self.instructions_table.cellWidget(row, 2)
                    operand = operand_edit.text().strip()
                    if not operand:
                        QMessageBox.warning(self, "Error", f"Missing operand for instruction at address {address}")
                        return None, None
                    
                    valid, operand_val = Validator.validate_address(operand)
                    if not valid:
                        QMessageBox.warning(self, "Error", f"Invalid operand at address {address}: {operand_val}")
                        return None, None
                    
                    instructions[address] = f"{instruction} {operand_val}"
                    data_addresses_used.add(operand_val)
                else:
                    instructions[address] = instruction
        
        valid, duplicates = Validator.check_duplicate_instructions(instructions)
        if not valid:
            QMessageBox.warning(self, "Error", f"Duplicate instructions at addresses: {duplicates}")
            return None, None
        
        data_values = {}
        for address in data_addresses_used:
            if address in self.data_inputs:
                data_edit = self.data_inputs[address]
                value = data_edit.text().strip()
                if value:
                    valid, value_val = Validator.validate_data_value(value)
                    if not valid:
                        QMessageBox.warning(self, "Error", f"Invalid data value at address {address}: {value_val}")
                        return None, None
                    data_values[address] = value_val
                else:
                    data_values[address] = 0
            else:
                data_values[address] = 0
        
        print(f"Instructions: {instructions}")
        print(f"Data values: {data_values}")
        
        return instructions, data_values
    
    def run_program(self):
        
        instructions, data_values = self.get_program_data()
        if instructions is None:
            return
        
        self.cpu = CPU()
        
        for address, instruction in instructions.items():
            self.cpu.memory.set_instruction(address, instruction)
        
        for address, value in data_values.items():
            self.cpu.memory.set_data(address, value)
        
        self.cpu.run_program()
        
        self.output_text.clear()
        self.output_text.append("=== PROGRAM EXECUTION ===\n")
        for line in self.cpu.execution_log:
            self.output_text.append(line)
        self.output_text.append("\n=== EXECUTION COMPLETE ===")
        self.statusBar().showMessage("✅ Program execution completed")
    
    def step_program(self):

        if self.cpu is None:
            instructions, data_values = self.get_program_data()
            if instructions is None:
                return
            
            self.cpu = CPU()
            
            for address, instruction in instructions.items():
                self.cpu.memory.set_instruction(address, instruction)
            
            for address, value in data_values.items():
                self.cpu.memory.set_data(address, value)
        
        if not self.cpu.halted:
            self.cpu.run_cycle()
            self.output_text.clear()
            self.output_text.append("=== STEP-BY-STEP EXECUTION ===\n")
            for line in self.cpu.execution_log:
                self.output_text.append(line)
            self.statusBar().showMessage("⏭️ Stepped through one instruction")
        else:
            self.statusBar().showMessage("🛑 Program halted")
    
    def reset_program(self):
        self.cpu = None
        self.output_text.clear()
        self.setup_instructions()
        self.statusBar().showMessage("🔄 Program reset - Ready to configure")