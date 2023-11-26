import math
from bitarray import bitarray


def is_power_of_two(number):
    return number > 0 and (number & (number - 1)) == 0


def calculate_control_bit(data_bits, position):
    mask = 1 << int(math.log2(position))
    control_bit = 0

    for i in range(len(data_bits)):
        if i != position and i & mask:
            control_bit ^= data_bits[i]

    return control_bit


def insert_control_bits(data: bitarray):
    data.insert(0, 0)  # insert future parity bit

    for i in range(len(data)):  # insert future control bits
        if is_power_of_two(i):
            data.insert(i, 1)


def calculate_parity_bit_for_sender(data: bitarray):
    parity = 0
    for i in range(1, len(data)):
        parity ^= data[i]

    return parity


def calculate_parity_bit_for_receiver(data: bitarray):
    parity = 0
    for i in range(len(data)):
        parity ^= data[i]

    return parity


def hamming_encode(data: bitarray):
    insert_control_bits(data)

    for i in range(len(data)):
        if is_power_of_two(i):
            control_bit = calculate_control_bit(data, i)
            data[i] = control_bit

    data[0] = calculate_parity_bit_for_sender(data)


def calculate_syndrome_bit(data: bitarray, position):
    mask = 1 << int(math.log2(position))
    syndrome_bit = 0

    for i in range(len(data)):
        if i & mask:
            syndrome_bit ^= data[i]

    return syndrome_bit


def delete_control_bits(data: bitarray):
    indexes_to_remove = [2 ** i for i in range(len(data)) if 2 ** i < len(data)]

    for index in reversed(indexes_to_remove):
        data.pop(index)
    data.pop(0)


def binary_to_decimal(binary_list):
    decimal_number = 0
    for bit in binary_list:
        decimal_number = decimal_number * 2 + bit
    return decimal_number


def hamming_decode(data: bitarray):
    parity = calculate_parity_bit_for_receiver(data)  # считаем бит четности
    syndromes = list()

    for i in range(len(data)):
        if is_power_of_two(i):
            syndromes.insert(0, calculate_syndrome_bit(data, i))  # считаем биты синдрома

    if all(item == 0 for item in syndromes) and parity == 0:
        delete_control_bits(data)
        # print('нет ошибок')
        return 0

    if parity != 0 and any(item != 0 for item in syndromes):
        position = binary_to_decimal(syndromes)
        data[position] ^= 1
        delete_control_bits(data)
        # print('одиночная ошибка')
        return 1

    if parity == 0 and any(item != 0 for item in syndromes):
        # print('двойная ошибка')
        return 2
