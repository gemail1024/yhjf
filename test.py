
from app import ZWSPaths,SERVER_URL



"""使用真正的零宽字符生成哈希"""
    # 只使用完全不可见的零宽字符
zero_width_chars = [
    '\u200b',  # 零宽空格 ZERO WIDTH SPACE
    '\u200c',  # 零宽非连接符 ZERO WIDTH NON-JOINER
    '\u200d',  # 零宽连接符 ZERO WIDTH JOINER
    '\u2060',  # 词组连接符 WORD JOINER
    '\ufeff',  # 零宽非断空格 ZERO WIDTH NO-BREAK SPACE
]


def zws_to_decimal(zws):
    """将零宽字符串转回十进制数（用于调试）"""
    decimal = 0
    for char in zws:
        decimal = decimal * 5 + zero_width_chars.index(char)
    return decimal


def decimal_to_zws(decimal_num):
    """将十进制数转换为零宽字符串"""
    # 零宽字符集合（相当于5进制数的0-4）

    if decimal_num == 0:
        return zero_width_chars[0]

    zws = ''
    # 将十进制数转换为5进制数，并映射到零宽字符
    while decimal_num:
        decimal_num, remainder = divmod(decimal_num, 5)
        zws = zero_width_chars[remainder] + zws
    return zws

# 测试代码
def test_zws_conversion():
    # 测试一些数字
    test_numbers = [0, 5, 25, 100, 1000000]
    for num in test_numbers:
        zws = decimal_to_zws(num)
        restored = zws_to_decimal(zws)
        print(f"原始数字: {num}")
        print(f"零宽字符长度: {len(zws)}")
        print(f"还原后数字: {restored}")
        print(f"转换是否正确: {num == restored}")
        print("---")



def debug_url(url):
    """用于调试的函数，显示URL中的零宽字符"""
    parts = []
    for char in url:
        if ord(char) in [0x200b, 0x200c, 0x200d, 0x2060, 0xfeff]:
            parts.append(f'U+{ord(char):04X}')
        else:
            parts.append(char)
    return ' '.join(parts)



if __name__ == '__main__':
    # 使用示例
    url = f"{SERVER_URL}/{ZWSPaths.VIEW}/{hash}"
    print(f"Debug URL: {debug_url(url)}")
    # test_zws_conversion()
