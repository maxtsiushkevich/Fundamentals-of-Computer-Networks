from tkinter import *
from tkinter import ttk


def update_textbox(textbox, line, line_end, data):
    textbox.config(state='normal')
    textbox.delete(line, line_end)
    textbox.insert(line_end, data)
    textbox.config(state='disabled')


def print_info_text(input_port, receive_port, widget):
    text = (f'COM1 Port: {input_port.port}\n'
            f'COM2 Port: {receive_port.port}\n'
            f'Bytes in last send message (COM1): {input_port.out_waiting}\n'
            f'Bytes in last received message (COM2): {receive_port.in_waiting}\n')

    update_textbox(widget, '1.0', 'end', text)


def create_label(text, x, y, root):
    label = Label(root, text=text)
    label.place(x=x, y=y)
    return label


def create_baudrate_combobox(parent, values, default_value, x, y, is_input_combobox, change_baudrate):
    cbox = ttk.Combobox(parent, values=values, state='readonly')
    cbox.set(default_value)
    cbox.place(x=x, y=y)

    cbox.bind('<<ComboboxSelected>>',
              lambda event, combobox=cbox: change_baudrate(int(combobox.get()), is_input_combobox))
    return cbox


def create_text_widget(parent, width, height, x, y):
    text_widget = Text(parent, width=width, height=height, wrap=WORD, font=('Arial', 14), state='disabled')
    text_widget.place(x=x, y=y)
    return text_widget


def create_input_entry(parent, width, x, y, bind_function, action):
    input_entry = Entry(parent, width=width, font=('Arial', 14))
    input_entry.place(x=x, y=y)
    input_entry.bind(action, bind_function)
    return input_entry


def get_hex_string_space_every_4_chars(string):
    hex_string = ''.join(f'{byte:02X}' for byte in string)
    hex_string_with_spaces = ' '.join(hex_string[i:i + 4] for i in range(0, len(hex_string), 4))
    return hex_string_with_spaces


def create_port_label(window, label_text):
    label = Label(window, text=label_text)
    label.pack(pady=10)
    entry = Entry(window, width=30)
    entry.pack()
    return entry


def open_port_set_window(root, set_port_names):
    port_entry_window = Toplevel(root)
    port_entry_window.title('Enter Port Names')
    port_entry_window.geometry('400x200')

    input_port_entry = create_port_label(port_entry_window, 'Enter COM1 Port Name:')
    receive_port_entry = create_port_label(port_entry_window, 'Enter COM2 Port Name:')

    ok_button = Button(port_entry_window, text='OK', command=lambda: set_port_names(input_port_entry, receive_port_entry, port_entry_window))
    ok_button.pack(pady=10)
