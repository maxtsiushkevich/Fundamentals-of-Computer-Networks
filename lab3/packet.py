import random

from bitarray import bitarray
import hamming as hamming


class Packet:
    flag = (ord('z') + 20).to_bytes(8, 'big')  # Флаг

    def __init__(self, message):  # init of packet
        zero = 0

        dest_address = zero.to_bytes(4, 'big')  # Destination Address - 4 bytes
        source_address = zero.to_bytes(4, 'big')  # Source Address - 4 bytes
        length = len(message.encode('utf-8')).to_bytes(4, 'big')  # Length - 4 bytes

        data = bitarray()
        data.frombytes(message.encode('utf-8'))
        hamming.hamming_encode(data)
        pad = data.fill()

        fcs = pad.to_bytes(1, 'big')  # FCS - 1 byte
        print(f'FCS: {fcs} \n Pad: {pad}')
        byte_data = data.tobytes()

        self.__packet = self.flag + dest_address + source_address + length + byte_data + fcs

    @property
    def get_packet(self):
        return self.__packet

    @staticmethod
    def emulate_error(bit_data: bitarray):

        probability = random.random()
        index = random.randint(0, len(bit_data) - 1)

        if probability <= 0.5:
            bit_data[index] ^= 1
        elif probability <= 0.75:
            bit_data[index] ^= 1
            bit_data[index - 1] ^= 1

    @staticmethod  # parsing packet for message
    def get_data(byte_packet: bytes):
        bit_data = bitarray()
        bit_data.frombytes(byte_packet[20:-1])

        fcs_int = byte_packet[-1]

        for _ in range(fcs_int):
            bit_data.pop()

        Packet.emulate_error(bit_data)
        numbers_of_error = hamming.hamming_decode(bit_data)

        if numbers_of_error == 2:
            return 'Double error in receiving data'
        else:
            message = bit_data.tobytes().decode('utf-8')
            return message

    def get_stuffed_packet(self):
        packet = bitarray()
        packet.frombytes(self.__packet)

        bit_flag = bitarray()
        bit_flag.frombytes(self.flag)

        finding_equals = packet.search(bit_flag)  # starting position of all sequences matching the flag

        i = 1  # skip 0 because index 0 is flag of packet which no need bit-stuffing
        num_of_staffing_bits = 0
        while i < len(finding_equals):
            packet.insert(finding_equals[i] + (len(bit_flag) - 1), 1)
            i += 1
            num_of_staffing_bits += 1

        packet.fill()

        return packet.tobytes()

    @staticmethod
    def get_destuffed_packet(data: bytes):
        packet = bitarray()
        packet.frombytes(data)

        finding_bit_flag = bitarray()
        finding_flag = (ord('z') + 20).to_bytes(8, 'big')
        finding_bit_flag.frombytes(finding_flag)
        finding_bit_flag.insert(-1, 1)

        finding_equals = packet.search(finding_bit_flag)

        i = 0
        while i < len(finding_equals):
            packet.pop(finding_equals[i] + (
                    len(finding_bit_flag) - 2))  # -2 because findind bit flag have one more bit (stuff bit)
            i += 1

        length = packet[16 * 8:20 * 8]
        int_len = int(length.to01(), 2)
        destuffed_packet = packet[0:16 * 8] + length + packet[20 * 8:(20 + int_len) * 8] + packet[-8:]

        return destuffed_packet.tobytes()
