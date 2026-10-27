"""第三题：统计字符串中的英文字母、数字和其他字符。"""


def count_characters(text):
    """英文字母仅含 A-Z/a-z，数字仅含 0-9，其余均计入其他字符。"""
    letters = 0
    digits = 0
    others = 0

    for character in text:
        if "a" <= character <= "z" or "A" <= character <= "Z":
            letters += 1
        elif "0" <= character <= "9":
            digits += 1
        else:
            others += 1

    return letters, digits, others


def main():
    # input() 去除行尾换行符，但保留字符串中的空格。
    text = input()
    letters, digits, others = count_characters(text)
    print(f"英文字母个数：{letters}")
    print(f"数字个数：{digits}")
    print(f"其他字符个数：{others}")


if __name__ == "__main__":
    main()
