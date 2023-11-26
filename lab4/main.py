# socat -d -d pty,raw,echo=0 pty,raw,echo=0 &
# socat -d -d pty,raw,echo=0 pty,raw,echo=0
# 142 char
# 1234567898765432123456789876543212345678987654321234567876543123415435678987654456543456765456542123456789876543212345678987654321234567876543
import random
import time

import serial
from tkinter import *
import threading
from bitarray import bitarray

import interface as interface
import packet as Packet

input_port_path = ''
receive_port_path = ''

input_port = serial.Serial()
receive_port = serial.Serial()

read_thread = threading.Thread()

baudrate = 9600
timeout = 1

jam_signal = b'jam'

try_counter = 0
max_try = 20


def is_channel_busy():
    return random.choice([True, False])


def emulate_collision():
    return random.choice([True, False])


def is_late_collision():
    return random.choice([True, False])


def wait_collision_window(send_bytes):
    # collision_window = (send_bytes / input_port.baudrate) * 2  # не будет заметна
    collision_window = 1
    time.sleep(collision_window)


def calculate_random_backoff(n):
    k = min(n, 10)
    r = random.randint(0, 2 ** k)
    return r


def handle_collision(collision_window):
    global try_counter, jam_signal, max_try
    is_error_return = False

    input_port.write(jam_signal)

    wait_collision_window(collision_window)

    try_counter += 1

    if is_late_collision():
        print('Поздняя коллизия')
        is_error_return = True
        return is_error_return

    if try_counter > max_try:
        print('Превышено число попыток')
        is_error_return = True
        return is_error_return

    slot_time_delay = 0.000512  # 512 микросекунд
    delay = calculate_random_backoff(try_counter) * slot_time_delay

    time.sleep(delay)

    return is_error_return


def send_message(event):
    global try_counter
    try_counter = 0

    input_string = com1_input.get()
    packet = Packet.Packet(input_string)

    print()
    if input_port.is_open:
        while True:
            if is_channel_busy():
                print('Канал занят')
                continue

            send_bytes = input_port.write(packet.get_packet)
            info = f'Bytes in last send message (COM1): {send_bytes}'
            interface.update_textbox(info_text, '3.0', '3.end', info)
            com1_input.delete(0, END)

            wait_collision_window(len(input_string))  # выжидаем окно колизий

            is_collision = emulate_collision()

            if is_collision:
                print('Коллизия')
                if handle_collision(len(input_string)):
                    return
                else:
                    continue
            break


def read_message():
    global receive_port, jam_signal
    try:
        while True:
            if receive_port.in_waiting:
                print()
                if receive_port.is_open:

                    received_data = receive_port.read(receive_port.in_waiting)  # receive packet

                    if received_data == jam_signal:
                        com2_output_text.delete(0, END)
                        info = f'Получен jam-сигнал'
                        interface.update_textbox(info_text, '4.0', '4.end', info)
                        continue

                    is_collision = emulate_collision()
                    if is_collision:
                        com2_output_text.delete(0, END)
                        info = 'Коллизия (другие причины)'
                        interface.update_textbox(info_text, '4.0', '4.end', info)
                        continue

                    s1 = bitarray()
                    s1.frombytes(received_data)
                    string = s1.to01()

                    interface.update_textbox(before_encoding, '1.0', '1.end', string)
                    before_encoding.tag_add('red', '1.end -8c', '1.end')
                    before_encoding.tag_config('red', foreground='red')

                    message = Packet.Packet.get_data(received_data)
                    info = f'Bytes in last received message (COM2): {len(received_data)}'

                    interface.update_textbox(info_text, '4.0', '4.end', info)
                    interface.update_textbox(com2_output_text, '1.0', 'end', message)

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


if __name__ == '__main__':
    root = Tk()
    root.title('Lab2 OKS')
    root.geometry('820x370')

    open_port_button = Button(root, text='Change ports',
                              command=lambda: interface.open_port_set_window(root, set_port_names))
    open_port_button.place(x=6.4, y=250)

    com1_label = interface.create_label('Send:', 6.4, 15, root)
    com2_label = interface.create_label('Recieved:', 6.4, 60, root)

    baudrate_label_com1 = interface.create_label('COM1:', 352, 15, root)
    baudrate_label_com2 = interface.create_label('COM2:', 352, 45, root)

    info_label = interface.create_label('Information:', 352, 81, root)
    info_text = interface.create_text_widget(root, 34, 8, 352, 105)

    com1_input = interface.create_input_entry(root, 30, 83.2, 15, send_message, '<Return>')

    com2_output_text = interface.create_text_widget(root, 30, 11, 83.2, 60)

    input_baudrate_combobox = interface.create_baudrate_combobox(root, input_port.BAUDRATES, baudrate, 416, 15, True,
                                                                 change_baudrate)
    receive_baudrate_combobox = interface.create_baudrate_combobox(root, receive_port.BAUDRATES, baudrate, 416, 45,
                                                                   False, change_baudrate)

    before_encoding = interface.create_text_widget(root, 100, 4, 6.4, 290)
    # after_encoding = interface.create_text_widget(root, 100, 4, 6.4, 370)

    root.mainloop()
    close_port(input_port)
    close_port(receive_port)
