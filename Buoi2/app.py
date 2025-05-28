from flask import Flask, render_template, request, json
from cipher.caesar import CaesarCipher
from cipher.vigenere import VigenereCipher
from cipher.railfence import RailFenceCipher
app = Flask(__name__)

# --- Logic Caesar Cipher (nhúng trực tiếp vào app.py) ---
def caesar_encrypt_logic(text, key):
    encrypted_text = []
    for char in text:
        if 'A' <= char <= 'Z':
            encrypted_text.append(chr(((ord(char) - ord('A') + key) % 26) + ord('A')))
        elif 'a' <= char <= 'z':
            encrypted_text.append(chr(((ord(char) - ord('a') + key) % 26) + ord('a')))
        else:
            encrypted_text.append(char)
    return "".join(encrypted_text)

def caesar_decrypt_logic(text, key):
    decrypted_text = []
    for char in text:
        if 'A' <= char <= 'Z':
            decrypted_text.append(chr(((ord(char) - ord('A') - key + 26) % 26) + ord('A')))
        elif 'a' <= char <= 'z':
            decrypted_text.append(chr(((ord(char) - ord('a') - key + 26) % 26) + ord('a')))
        else:
            decrypted_text.append(char)
    return "".join(decrypted_text)

# --- Logic Vigenere Cipher (nhúng trực tiếp vào app.py) ---
def vigenere_encrypt_logic(plaintext, key):
    encrypted_text = []
    key_len = len(key)
    key_as_int = [ord(char.upper()) - ord('A') for char in key] # Chuyển đổi khóa thành số, đảm bảo chữ hoa

    j = 0
    for char in plaintext:
        if 'A' <= char.upper() <= 'Z':
            shift = key_as_int[j % key_len]

            if 'A' <= char <= 'Z': # Chữ hoa
                encrypted_char_code = (ord(char) - ord('A') + shift) % 26 + ord('A')
                encrypted_text.append(chr(encrypted_char_code))
            elif 'a' <= char <= 'z': # Chữ thường
                encrypted_char_code = (ord(char) - ord('a') + shift) % 26 + ord('a')
                encrypted_text.append(chr(encrypted_char_code))
            j += 1
        else:
            encrypted_text.append(char)
    return "".join(encrypted_text)

def vigenere_decrypt_logic(ciphertext, key):
    decrypted_text = []
    key_len = len(key)
    key_as_int = [ord(char.upper()) - ord('A') for char in key] # Chuyển đổi khóa thành số, đảm bảo chữ hoa

    j = 0
    for char in ciphertext:
        if 'A' <= char.upper() <= 'Z':
            shift = key_as_int[j % key_len]

            if 'A' <= char <= 'Z': # Chữ hoa
                decrypted_char_code = (ord(char) - ord('A') - shift + 26) % 26 + ord('A')
                decrypted_text.append(chr(decrypted_char_code))
            elif 'a' <= char <= 'z': # Chữ thường
                decrypted_char_code = (ord(char) - ord('a') - shift + 26) % 26 + ord('a')
                decrypted_text.append(chr(decrypted_char_code))
            j += 1
        else:
            decrypted_text.append(char)
    return "".join(decrypted_text)

# --- Logic Rail Fence Cipher (nhúng trực tiếp vào app.py) ---
def railfence_encrypt_logic(text, key):
    # Loại bỏ khoảng trắng và chuyển về chữ hoa để đơn giản hóa việc mã hóa
    # Hoặc bạn có thể giữ nguyên và xử lý thêm logic
    text = text.replace(" ", "")
    if not text:
        return ""
    if key <= 1: # Key = 1 hoặc nhỏ hơn không mã hóa gì
        return text

    # Tạo ma trận để đặt các ký tự
    rail = [['\n' for _ in range(len(text))] for _ in range(key)]

    # Hướng di chuyển: xuống hoặc lên
    dir_down = False
    row, col = 0, 0

    for char in text:
        # Kiểm tra hướng di chuyển của "hàng rào"
        if (row == 0) or (row == key - 1):
            dir_down = not dir_down

        # Đặt ký tự vào "hàng rào"
        rail[row][col] = char
        col += 1

        # Tìm hàng tiếp theo
        if dir_down:
            row += 1
        else:
            row -= 1

    # Đọc ma trận theo thứ tự hàng để tạo văn bản mã hóa
    result = []
    for i in range(key):
        for j in range(len(text)):
            if rail[i][j] != '\n':
                result.append(rail[i][j])
    return "".join(result)

def railfence_decrypt_logic(ciphertext, key):
    if not ciphertext:
        return ""
    if key <= 1:
        return ciphertext

    # Tạo ma trận trống và đánh dấu vị trí của các ký tự
    rail = [['\n' for _ in range(len(ciphertext))] for _ in range(key)]

    # Hướng di chuyển và vị trí ban đầu
    dir_down = False
    row, col = 0, 0

    # Đánh dấu vị trí sẽ điền vào
    for i in range(len(ciphertext)):
        if (row == 0) or (row == key - 1):
            dir_down = not dir_down
        
        rail[row][col] = '*' # Đánh dấu vị trí
        col += 1

        if dir_down:
            row += 1
        else:
            row -= 1

    # Điền các ký tự của văn bản mã hóa vào các vị trí đã đánh dấu
    index = 0
    for i in range(key):
        for j in range(len(ciphertext)):
            if rail[i][j] == '*':
                rail[i][j] = ciphertext[index]
                index += 1

    # Đọc lại theo đường zigzag để lấy lại văn bản gốc
    result = []
    dir_down = False
    row, col = 0, 0
    for i in range(len(ciphertext)):
        if (row == 0) or (row == key - 1):
            dir_down = not dir_down
        
        if rail[row][col] != '\n': # Kiểm tra xem có ký tự tại vị trí này không
            result.append(rail[row][col])
        col += 1

        if dir_down:
            row += 1
        else:
            row -= 1
            
    return "".join(result)


# router routes for home page
@app.route("/")
def home():
    return render_template('index.html')

# router routes for caesar cypher
@app.route("/caesar")
def caesar():
    return render_template('caesar.html')

@app.route("/encrypt", methods=['POST'])
def caesar_encrypt():
    text = request.form['inputPlainText']
    key = int(request.form['inputKeyPlain'])
    encrypted_text = caesar_encrypt_logic(text, key)
    return f"text: {text}<br/>key: {key}<br/>encrypted text: {encrypted_text}"

@app.route("/decrypt", methods=['POST'])
def caesar_decrypt():
    text = request.form['inputCipherText']
    key = int(request.form['inputKeyCipher'])
    decrypted_text = caesar_decrypt_logic(text, key)
    return f"text: {text}<br/>key: {key}<br/>decrypted text: {decrypted_text}"

# router routes for vigenere cypher
@app.route("/vigenere")
def vigenere():
    return render_template('vigenere.html')

@app.route("/vigenere_encrypt", methods=['POST'])
def vigenere_encrypt():
    text = request.form['inputPlainTextVigenere']
    key = request.form['inputKeyVigenerePlain']
    encrypted_text = vigenere_encrypt_logic(text, key)
    return f"text: {text}<br/>key: {key}<br/>encrypted text: {encrypted_text}"

@app.route("/vigenere_decrypt", methods=['POST'])
def vigenere_decrypt():
    text = request.form['inputCipherTextVigenere']
    key = request.form['inputKeyVigenereCipher']
    decrypted_text = vigenere_decrypt_logic(text, key)
    return f"text: {text}<br/>key: {key}<br/>decrypted text: {decrypted_text}"

# router routes for railfence cypher
@app.route("/railfence")
def railfence():
    return render_template('railfence.html') # Thêm route để hiển thị trang railfence.html

@app.route("/railfence_encrypt", methods=['POST'])
def railfence_encrypt():
    text = request.form['inputPlainTextRailFence']
    key = int(request.form['inputKeyRailFencePlain']) # Khóa là số nguyên
    encrypted_text = railfence_encrypt_logic(text, key)
    return f"text: {text}<br/>key: {key}<br/>encrypted text: {encrypted_text}"

@app.route("/railfence_decrypt", methods=['POST'])
def railfence_decrypt():
    text = request.form['inputCipherTextRailFence']
    key = int(request.form['inputKeyRailFenceCipher']) # Khóa là số nguyên
    decrypted_text = railfence_decrypt_logic(text, key)
    return f"text: {text}<br/>key: {key}<br/>decrypted text: {decrypted_text}"

# main function
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)