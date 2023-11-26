# socat -d -d pty,raw,echo=0 pty,raw,echo=0 &
# socat -d -d pty,raw,echo=0 pty,raw,echo=0
# 142 chars

import serial
from tkinter import *
import threading
import interface as interface
import packet as Packet

input_port_path = ''
receive_port_path = ''

input_port = serial.Serial()
receive_port = serial.Serial()

read_thread = threading.Thread()

baudrate = 9600
timeout = 1


def send_message(event):
    if input_port.is_open:
        input_string = com1_input.get()

        packet = Packet.Packet(input_string)  # создаем пакет
        send_data = packet.get_stuffed_packet()  # стаффим пакет
        send_bytes = input_port.write(send_data)
        info = f'Bytes in last send message (COM1): {send_bytes}'
        interface.update_textbox(info_text, '3.0', '3.end', info)

        com1_input.delete(0, END)


def read_message():
    global receive_port
    try:
        while True:
            if receive_port.in_waiting:
                if receive_port.is_open:
                    received_data = receive_port.read(receive_port.in_waiting)  # receive packet
                    destuffing_data = Packet.Packet.get_destuffed_packet(received_data)
                    message = Packet.Packet.get_message(destuffing_data)
                    info = f'Bytes in last received message (COM2): {len(received_data)}'

                    interface.update_textbox(info_text, '4.0', '4.end', info)
                    interface.update_textbox(com2_output_text, '1.0', 'end', message)

                    print(f'Before: {interface.get_hex_string_space_every_4_chars(received_data)}')
                    print(f'After: {interface.get_hex_string_space_every_4_chars(destuffing_data)}')
                    print()
            else:
                if not receive_port.is_open:
                    return

    except Exception:
        return


def run_read_thread():
    global read_thread

    if read_thread and read_thread.is_alive():
        read_thread.join()

    read_thread = threading.Thread(target=read_message)
    read_thread.daemon = True
    read_thread.start()


def set_port_names(input_port_entry, receive_port_entry, port_entry_window):
    global input_port_path, receive_port_path, input_port, receive_port

    input_port_path = input_port_entry.get()
    receive_port_path = receive_port_entry.get()

    close_port(input_port)
    close_port(receive_port)

    try:
        input_port.port = input_port_path
        receive_port.port = receive_port_path

        input_port.open()
        receive_port.open()

        run_read_thread()

        interface.print_info_text(input_port, receive_port, info_text)
        port_entry_window.destroy()
    except serial.SerialException as e:
        print(f"Failed to open port: {str(e)}")


def close_port(port):
    if port.is_open:
        port.close()


def change_baudrate(selected_baudrate, is_input_port):
    global input_port, receive_port

    if is_input_port:
        input_port.baudrate = selected_baudrate
        print(f'Changed baudrate of {input_port.port} to {input_port.baudrate}')
    else:
        receive_port.baudrate = selected_baudrate
        print(f'Changed baudrate of {receive_port.port} to {receive_port.baudrate}')


root = Tk()
root.title('Lab2 OKS')
root.geometry('640x300')

run_read_thread()

open_port_button = Button(root, text='Change ports',
                          command=lambda: interface.open_port_entry_window(root, set_port_names))
open_port_button.place(relx=0.01, rely=0.85)

com1_label = interface.create_label('Send:', 0.01, 0.05, root)
com2_label = interface.create_label('Recieved:', 0.01, 0.2, root)

baudrate_label_com1 = interface.create_label('COM1:', 0.55, 0.05, root)
baudrate_label_com2 = interface.create_label('COM2:', 0.55, 0.15, root)

info_label = interface.create_label('Information:', 0.55, 0.27, root)

com1_input = interface.create_input_entry(root, 30, 0.13, 0.05, send_message, '<Return>')

com2_output_text = interface.create_text_widget(root, 30, 10, 0.13, 0.2)
info_text = interface.create_text_widget(root, 34, 7, 0.55, 0.35)

input_baudrate_combobox = interface.create_baudrate_combobox(root, input_port.BAUDRATES, baudrate, 0.65, 0.05, True,
                                                             change_baudrate)
receive_baudrate_combobox = interface.create_baudrate_combobox(root, receive_port.BAUDRATES, baudrate, 0.65, 0.15,
                                                               False, change_baudrate)

root.mainloop()

close_port(input_port)
close_port(receive_port)
