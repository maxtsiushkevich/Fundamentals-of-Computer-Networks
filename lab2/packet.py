class Packet:
    flag = (ord('z') + 20).to_bytes(8, 'big')  # Флаг

    def __init__(self, message):  # init of packet
        zero = 0

        dest_address = zero.to_bytes(4, 'big')  # Destination Address - 4 bytes
        source_address = zero.to_bytes(4, 'big')  # Source Address - 4 bytes
        length = len(message.encode('utf-8')).to_bytes(4, 'big')  # Length - 4 bytes
        data = message.encode('utf-8')
        fcs = zero.to_bytes(1, 'big')  # FCS - 1 byte
        self.__packet = self.flag + dest_address + source_address + length + data + fcs

    @property
    def get_packet(self):
        return self.__packet

    @staticmethod  # parsing packet for message
    def get_message(packet):
        length = int.from_bytes(packet[16:20], 'big')
        data = packet[20:20 + length]
        message = data.decode('utf-8')
        return message

    def get_stuffed_packet(self):
        stuffed_data = b''
        stuff_bit = b'\x01'

        i = 0
        while i < len(self.__packet):
            if i >= 8 and self.__packet[i:i + len(self.flag)] == self.flag:
                stuffed_data += self.flag[0:7]
                stuffed_data += stuff_bit
                stuffed_data += self.flag[7:8]
                i += len(self.flag) - 1
            else:
                stuffed_data += self.__packet[i:i + 1]
            i += 1

        return stuffed_data

    @staticmethod
    def get_destuffed_packet(data):
        destuffed_data = b""
        stuff_bit = b'\x01'
        flag = (ord('z') + 20).to_bytes(8, 'big')  # Флаг

        i = 0
        while i < len(data):
            if i + 7 < len(data) and data[i:i + 7] == flag[:7] and data[i + 7:i + 8] == stuff_bit and data[
                                                                                                      i + 8:i + 9] == flag[
                                                                                                                      7:8]:
                destuffed_data += flag[:7]
                i += 8
            else:
                destuffed_data += data[i:i + 1]
                i += 1

        return destuffed_data
