from flask import Flask, render_template, request, json
from cipher.caesar import CaesarCipher
from cipher.vigenere import VigenereCipher
from cipher.railfence import RailFenceCipher
from cipher.playfair import PlayFairCipher
from cipher.transposition import TranspositionCipher
app = Flask(__name__)

# --- Logic Caesar Cipher ---
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

# --- Logic Vigenere Cipher ---
def vigenere_encrypt_logic(plaintext, key):
    encrypted_text = []
    key_len = len(key)
    key_as_int = [ord(char.upper()) - ord('A') for char in key]

    j = 0
    for char in plaintext:
        if 'A' <= char.upper() <= 'Z':
            shift = key_as_int[j % key_len]

            if 'A' <= char <= 'Z':
                encrypted_char_code = (ord(char) - ord('A') + shift) % 26 + ord('A')
                encrypted_text.append(chr(encrypted_char_code))
            elif 'a' <= char <= 'z':
                encrypted_char_code = (ord(char) - ord('a') + shift) % 26 + ord('a')
                encrypted_text.append(chr(encrypted_char_code))
            j += 1
        else:
            encrypted_text.append(char)
    return "".join(encrypted_text)

def vigenere_decrypt_logic(ciphertext, key):
    decrypted_text = []
    key_len = len(key)
    key_as_int = [ord(char.upper()) - ord('A') for char in key]

    j = 0
    for char in ciphertext:
        if 'A' <= char.upper() <= 'Z':
            shift = key_as_int[j % key_len]

            if 'A' <= char <= 'Z':
                decrypted_char_code = (ord(char) - ord('A') - shift + 26) % 26 + ord('A')
                decrypted_text.append(chr(decrypted_char_code))
            elif 'a' <= char <= 'z':
                decrypted_char_code = (ord(char) - ord('a') - shift + 26) % 26 + ord('a')
                decrypted_text.append(chr(decrypted_char_code))
            j += 1
        else:
            decrypted_text.append(char)
    return "".join(decrypted_text)

# --- Logic Rail Fence Cipher ---
def railfence_encrypt_logic(text, key):
    text = text.replace(" ", "")
    if not text:
        return ""
    if key <= 1:
        return text

    rail = [['\n' for _ in range(len(text))] for _ in range(key)]
    dir_down = False
    row, col = 0, 0

    for char in text:
        if (row == 0) or (row == key - 1):
            dir_down = not dir_down

        rail[row][col] = char
        col += 1

        if dir_down:
            row += 1
        else:
            row -= 1

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

    rail = [['\n' for _ in range(len(ciphertext))] for _ in range(key)]
    dir_down = False
    row, col = 0, 0

    for i in range(len(ciphertext)):
        if (row == 0) or (row == key - 1):
            dir_down = not dir_down
        
        rail[row][col] = '*'
        col += 1

        if dir_down:
            row += 1
        else:
            row -= 1

    index = 0
    for i in range(key):
        for j in range(len(ciphertext)):
            if rail[i][j] == '*':
                rail[i][j] = ciphertext[index]
                index += 1

    result = []
    dir_down = False
    row, col = 0, 0
    for i in range(len(ciphertext)):
        if (row == 0) or (row == key - 1):
            dir_down = not dir_down
        
        if rail[row][col] != '\n':
            result.append(rail[row][col])
        col += 1

        if dir_down:
            row += 1
        else:
            row -= 1
            
    return "".join(result)

# --- Logic Playfair Cipher ---
def playfair_prepare_key(key):
    key = "".join(filter(str.isalpha, key)).upper().replace("J", "I")
    
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    key_square = []
    
    for char in key:
        if char not in key_square:
            key_square.append(char)
            
    for char in alphabet:
        if char not in key_square:
            key_square.append(char)
            
    matrix = []
    for i in range(5):
        matrix.append(key_square[i*5:(i+1)*5])
    return matrix

def playfair_find_char(matrix, char):
    for r, row in enumerate(matrix):
        for c, val in enumerate(row):
            if val == char:
                return r, c
    return -1, -1

def playfair_prepare_plaintext(text):
    text = "".join(filter(str.isalpha, text)).upper().replace("J", "I")
    prepared_text = []
    i = 0
    while i < len(text):
        prepared_text.append(text[i])
        if i + 1 < len(text):
            if text[i] == text[i+1]:
                prepared_text.append('X')
            prepared_text.append(text[i+1])
            i += 2
        else:
            i += 1
    
    if len(prepared_text) % 2 != 0:
        prepared_text.append('X')
    return "".join(prepared_text)

def playfair_encrypt_logic(plaintext, key):
    matrix = playfair_prepare_key(key)
    prepared_text = playfair_prepare_plaintext(plaintext)
    encrypted_text = []

    for i in range(0, len(prepared_text), 2):
        char1 = prepared_text[i]
        char2 = prepared_text[i+1]

        r1, c1 = playfair_find_char(matrix, char1)
        r2, c2 = playfair_find_char(matrix, char2)

        if r1 == r2:
            encrypted_text.append(matrix[r1][(c1 + 1) % 5])
            encrypted_text.append(matrix[r2][(c2 + 1) % 5])
        elif c1 == c2:
            encrypted_text.append(matrix[(r1 + 1) % 5][c1])
            encrypted_text.append(matrix[(r2 + 1) % 5][c2])
        else:
            encrypted_text.append(matrix[r1][c2])
            encrypted_text.append(matrix[r2][c1])
            
    return "".join(encrypted_text)

def playfair_decrypt_logic(ciphertext, key):
    matrix = playfair_prepare_key(key)
    ciphertext = "".join(filter(str.isalpha, ciphertext)).upper().replace("J", "I")

    decrypted_text = []

    for i in range(0, len(ciphertext), 2):
        char1 = ciphertext[i]
        char2 = ciphertext[i+1]

        r1, c1 = playfair_find_char(matrix, char1)
        r2, c2 = playfair_find_char(matrix, char2)

        if r1 == r2:
            decrypted_text.append(matrix[r1][(c1 - 1 + 5) % 5])
            decrypted_text.append(matrix[r2][(c2 - 1 + 5) % 5])
        elif c1 == c2:
            decrypted_text.append(matrix[(r1 - 1 + 5) % 5][c1])
            decrypted_text.append(matrix[(r2 - 1 + 5) % 5][c2])
        else:
            decrypted_text.append(matrix[r1][c2])
            decrypted_text.append(matrix[r2][c1])
            
    return "".join(decrypted_text)

# --- Logic Transposition Cipher (Columnar Transposition) ---
def transposition_encrypt_logic(plaintext, key):
    # Loại bỏ khoảng trắng và chuyển về chữ hoa (tùy chọn, để đơn giản)
    plaintext = "".join(filter(str.isalpha, plaintext)).upper()
    key = "".join(filter(str.isalpha, key)).upper()

    if not plaintext or not key:
        return ""

    num_cols = len(key)
    num_rows = (len(plaintext) + num_cols - 1) // num_cols # Làm tròn lên

    # Tạo ma trận và điền văn bản gốc vào
    matrix = [[' ' for _ in range(num_cols)] for _ in range(num_rows)]
    k = 0
    for r in range(num_rows):
        for c in range(num_cols):
            if k < len(plaintext):
                matrix[r][c] = plaintext[k]
                k += 1

    # Sắp xếp các cột dựa trên thứ tự chữ cái của khóa
    # key_order sẽ là một danh sách các tuple (ký tự khóa, chỉ số gốc) được sắp xếp
    key_order = sorted([(key[i], i) for i in range(num_cols)])

    encrypted_text = []
    # Đọc các ký tự theo thứ tự cột đã sắp xếp
    for _, original_col_index in key_order:
        for r in range(num_rows):
            encrypted_text.append(matrix[r][original_col_index])
    
    return "".join(encrypted_text).strip() # Loại bỏ khoảng trắng thừa ở cuối

def transposition_decrypt_logic(ciphertext, key):
    # Loại bỏ khoảng trắng và chuyển về chữ hoa (tùy chọn)
    ciphertext = "".join(filter(str.isalpha, ciphertext)).upper()
    key = "".join(filter(str.isalpha, key)).upper()

    if not ciphertext or not key:
        return ""

    num_cols = len(key)
    num_rows = (len(ciphertext) + num_cols - 1) // num_cols

    # Tính toán số lượng ký tự trong mỗi cột
    # Một số cột có thể ngắn hơn nếu văn bản không điền đầy đủ ma trận
    chars_per_col = [num_rows] * num_cols
    remaining_chars = len(ciphertext) % num_cols
    if remaining_chars != 0:
        for i in range(num_cols - remaining_chars):
            chars_per_col[num_cols - 1 - i] -= 1

    # Tạo ma trận trống
    matrix = [[' ' for _ in range(num_cols)] for _ in range(num_rows)]

    # Sắp xếp các cột dựa trên thứ tự chữ cái của khóa (tương tự mã hóa)
    key_order = sorted([(key[i], i) for i in range(num_cols)])
    
    # Điền văn bản mã hóa vào ma trận theo thứ tự cột đã sắp xếp
    current_char_index = 0
    for _, original_col_index in key_order:
        for r in range(num_rows):
            # Chỉ điền vào các vị trí hợp lệ
            if r < chars_per_col[original_col_index]:
                matrix[r][original_col_index] = ciphertext[current_char_index]
                current_char_index += 1

    # Đọc ma trận theo thứ tự hàng bình thường để lấy lại văn bản gốc
    decrypted_text = []
    for r in range(num_rows):
        for c in range(num_cols):
            if matrix[r][c] != ' ': # Bỏ qua các ô trống hoặc ký tự đệm
                decrypted_text.append(matrix[r][c])
    
    return "".join(decrypted_text)


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
    return render_template('railfence.html')

@app.route("/railfence_encrypt", methods=['POST'])
def railfence_encrypt():
    text = request.form['inputPlainTextRailFence']
    key = int(request.form['inputKeyRailFencePlain'])
    encrypted_text = railfence_encrypt_logic(text, key)
    return f"text: {text}<br/>key: {key}<br/>encrypted text: {encrypted_text}"

@app.route("/railfence_decrypt", methods=['POST'])
def railfence_decrypt():
    text = request.form['inputCipherTextRailFence']
    key = int(request.form['inputKeyRailFenceCipher'])
    decrypted_text = railfence_decrypt_logic(text, key)
    return f"text: {text}<br/>key: {key}<br/>decrypted text: {decrypted_text}"

# router routes for playfair cypher
@app.route("/playfair")
def playfair():
    return render_template('playfair.html')

@app.route("/playfair_encrypt", methods=['POST'])
def playfair_encrypt():
    text = request.form['inputPlainTextPlayfair']
    key = request.form['inputKeyPlayfairPlain']
    encrypted_text = playfair_encrypt_logic(text, key)
    return f"text: {text}<br/>key: {key}<br/>encrypted text: {encrypted_text}"

@app.route("/playfair_decrypt", methods=['POST'])
def playfair_decrypt():
    text = request.form['inputCipherTextPlayfair']
    key = request.form['inputKeyPlayfairCipher']
    decrypted_text = playfair_decrypt_logic(text, key)
    return f"text: {text}<br/>key: {key}<br/>decrypted text: {decrypted_text}"

# router routes for transposition cypher
@app.route("/transposition")
def transposition():
    return render_template('transposition.html') # Thêm route để hiển thị trang transposition.html

@app.route("/transposition_encrypt", methods=['POST'])
def transposition_encrypt():
    text = request.form['inputPlainTextTransposition']
    key = request.form['inputKeyTranspositionPlain'] # Khóa là chuỗi
    encrypted_text = transposition_encrypt_logic(text, key)
    return f"text: {text}<br/>key: {key}<br/>encrypted text: {encrypted_text}"

@app.route("/transposition_decrypt", methods=['POST'])
def transposition_decrypt():
    text = request.form['inputCipherTextTransposition']
    key = request.form['inputKeyTranspositionCipher'] # Khóa là chuỗi
    decrypted_text = transposition_decrypt_logic(text, key)
    return f"text: {text}<br/>key: {key}<br/>decrypted text: {decrypted_text}"

# main function
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)