import sys
from PIL import Image

def decode_image(encoded_image_path):
    """Trích xuất thông điệp đã được giấu trong ảnh."""
    try:
        img = Image.open(encoded_image_path)
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file ảnh tại '{encoded_image_path}'")
        return

    binary_message = ""
    for row in range(img.height):
        for col in range(img.width):
            pixel = img.getpixel((col, row))
            for color_channel in range(3):
                binary_message += format(pixel[color_channel], '08b')[-1]

    delimiter = '1111111111111110'
    delimiter_index = binary_message.find(delimiter)

    if delimiter_index == -1:
        print("Không tìm thấy thông điệp hoặc file bị lỗi.")
        return ""

    binary_message = binary_message[:delimiter_index]

    message = ""
    for i in range(0, len(binary_message), 8):
        byte = binary_message[i:i+8]
        if len(byte) == 8:
            message += chr(int(byte, 2))
            
    return message

def main():
    if len(sys.argv) != 2:
        print("Usage: python decrypt.py <encoded_image_path>")
        return

    encoded_image_path = sys.argv[1]
    decoded_message = decode_image(encoded_image_path)
    if decoded_message:
        print(f"Decoded message: {decoded_message}")

if __name__ == "__main__":
    main()