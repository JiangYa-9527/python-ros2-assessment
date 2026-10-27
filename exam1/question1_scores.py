"""第一题：输入 10 名同学的整数成绩，按从高到低输出。"""

import sys


def sort_scores(scores):
    """返回降序排列的新列表，不修改原列表。"""
    if len(scores) != 10:
        raise ValueError("必须输入 10 名同学的成绩")
    return sorted(scores, reverse=True)


def main():
    # 支持空格、英文逗号、中文逗号分隔，也可以每行输入一个成绩。
    scores = []
    try:
        while len(scores) < 10:
            line = input()
            numbers = line.replace(",", " ").replace("，", " ").split()
            scores.extend(int(number) for number in numbers)
        print(*sort_scores(scores))
    except EOFError:
        print("输入错误：必须输入 10 名同学的成绩", file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"输入错误：{error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
