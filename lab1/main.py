# socat -d -d pty,raw,echo=0 pty,raw,echo=0 &
# socat -d -d pty,raw,echo=0 pty,raw,echo=0 &

import serial
from tkinter import *
from tkinter import ttk
import threading

baudrate_values = ['600', '1200', '2400', '4800', '9600', '19200', '38400', '57600', '115200']

input_port_path = ''
receive_port_path = ''

input_port = serial.Serial()
receive_port = serial.Serial()

read_thread = threading.Thread()

baudrate = 9600
timeout = 1


def update_textbox(textbox, line, line_end, data):
    textbox.config(state='normal')
    textbox.delete(line, line_end)
    textbox.insert(line_end, data)
    textbox.config(state='disabled')


def send_message(event):
    if input_port:
        input_string = com1_input.get()
        input_port.write(input_string.encode('utf-8'))

        info = f'Bytes in last send message (COM1): {len(input_string)}'
        update_textbox(info_text, '3.0', '3.end', info)

        print(f'Send message in {input_port.port}')
        com1_input.delete(0, END)


def read_message():
    try:
        while True:
            if receive_port.in_waiting:
                received_data = receive_port.read(receive_port.in_waiting)
                info = f'Bytes in last received message (COM2): {len(received_data)}'
                update_textbox(info_text, '4.0', '4.end', info)
                update_textbox(com2_output_text, '1.0', 'end', received_data.decode('utf-8'))
                print(f'Receive message from {receive_port.port}')
            else:
                if not receive_port.is_open:
                    return

    except Exception:
        return


def print_info_text():
    text = (f'COM1 Port: {input_port.port}\n'
            f'COM2 Port: {receive_port.port}\n'
            f'Bytes in last send message (COM1): {input_port.out_waiting}\n'
            f'Bytes in last received message (COM2): {receive_port.in_waiting}\n')

    update_textbox(info_text, '1.0', 'end', text)


def rerun_read_thread():
    global read_thread

    if read_thread and read_thread.is_alive():
        read_thread.join()

    read_thread = threading.Thread(target=read_message)
    read_thread.daemon = True
    read_thread.start()


def open_port_entry_window():
    def create_port_entry(parent, label_text):
        label = Label(parent, text=label_text)
        label.pack(pady=10)
        entry = Entry(parent, width=30)
        entry.pack()
        return entry

    def set_port_names():
        global input_port_path, receive_port_path, input_port, receive_port

        input_port_path = input_port_entry.get()
        receive_port_path = receive_port_entry.get()

        close_port(input_port)
        close_port(receive_port)

        try:
            input_port = serial.Serial(input_port_path, baudrate=baudrate, timeout=timeout)
            print(f'Port {input_port.port} opened successfully')

            receive_port = serial.Serial(receive_port_path, baudrate=baudrate, timeout=timeout)
            print(f'Port {input_port.port} opened successfully')

        except Exception as e:
            print(f'Error opening ports: {e}')
            return

        rerun_read_thread()
        print_info_text()
        port_entry_window.destroy()

    port_entry_window = Toplevel(root)
    port_entry_window.title('Enter Port Names')
    port_entry_window.geometry('400x200')

    input_port_entry = create_port_entry(port_entry_window, 'Enter COM1 Port Name:')
    receive_port_entry = create_port_entry(port_entry_window, 'Enter COM2 Port Name:')

    ok_button = Button(port_entry_window, text='OK', command=set_port_names)
    ok_button.pack(pady=10)


def close_port(port):
    if port:
        print(f'Port {port.port} is close')
        port.close()


def create_label(text, relx, rely):
    label = Label(root, text=text)
    label.place(relx=relx, rely=rely)
    return label


def create_baudrate_combobox(parent, values, default_value, relx, rely, is_input_combobox):
    cbox = ttk.Combobox(parent, values=values, state='readonly')
    cbox.set(default_value)
    cbox.place(relx=relx, rely=rely)

    cbox.bind('<<ComboboxSelected>>',
              lambda event, combobox=cbox: change_baudrate(int(combobox.get()), is_input_combobox))
    return cbox


def change_baudrate(selected_baudrate, is_input_port):
    global input_port, receive_port, read_thread

    port = input_port if is_input_port else receive_port

    if not is_input_port:
        port.close()
        read_thread.join()
    else:
        port.close()

    port.baudrate = selected_baudrate

    try:
        port.open()
        print(f'Changed baudrate of {port.port} to {port.baudrate}')
    except Exception as e:
        print(f'Error opening port {port.port}: {e}')

    if not is_input_port:
        rerun_read_thread()


def create_text_widget(parent, width, height, relx, rely):
    text_widget = Text(parent, width=width, height=height, wrap=WORD, font=('Arial', 14), state='disabled')
    text_widget.place(relx=relx, rely=rely)
    return text_widget


def create_input_entry(parent, width, relx, rely, bind_function, action):
    input_entry = Entry(parent, width=width, font=('Arial', 14))
    input_entry.place(relx=relx, rely=rely)
    input_entry.bind(action, bind_function)
    return input_entry


root = Tk()
root.title('Lab1 OKS')
root.geometry('640x300')

open_port_button = Button(root, text='Change ports', command=open_port_entry_window)
open_port_button.place(relx=0.01, rely=0.8)

com1_label = create_label('Send:', 0.01, 0.05)
com2_label = create_label('Recieved:', 0.01, 0.2)

baudrate_label_com1 = create_label('COM1:', 0.55, 0.05)
baudrate_label_com2 = create_label('COM2:', 0.55, 0.15)

info_label = create_label('Information:', 0.55, 0.27)

com1_input = create_input_entry(root, 30, 0.13, 0.05, send_message, '<Return>')

com2_output_text = create_text_widget(root, 30, 10, 0.13, 0.2)
info_text = create_text_widget(root, 34, 7, 0.55, 0.35)

input_baudrate_combobox = create_baudrate_combobox(root, baudrate_values, baudrate, 0.65, 0.05, True)
receive_baudrate_combobox = create_baudrate_combobox(root, baudrate_values, baudrate, 0.65, 0.15, False)

root.mainloop()

close_port(input_port)
close_port(receive_port)
