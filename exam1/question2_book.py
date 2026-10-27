"""第二题：使用 Book 类保存、输入和输出书籍信息。"""


class Book:
    def __init__(self, title="", price=0.0, stock=0):
        # 双下划线成员由 Python 进行名称改写，供类内部使用。
        self.__title = title
        self.__price = float(price)
        self.__stock = int(stock)

    def input_data(self):
        """依次输入书名、价格和库存，每项占一行。"""
        self.__title = input()
        self.__price = float(input())
        self.__stock = int(input())

    def display_data(self):
        """按题目指定的格式输出书籍信息。"""
        print(f"书名：{self.__title}")
        print(f"价格：{self.__price:g}")
        print(f"库存：{self.__stock}")


def main():
    book = Book()
    book.input_data()
    book.display_data()


if __name__ == "__main__":
    main()
