# coding=utf-8
from PIL import  Image
import argparse

#命令行输入行
parse = argparse.ArgumentParser()
parse.add_argument('file') #input file
parse.add_argument('-o','--output') #output file
parse.add_argument('--width',type=int,default=50) #input char width
parse.add_argument('--height',type=int,default=40) #inpurt char height

#get arguments
args = parse.parse_args()
IMG = args.file
OUTPUT = args.output
WIDTH = args.width
HEIGHT = args.height

ascii_char = list("$@B%8&amp;WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~&lt;&gt;i!lI;:,\"^`'. ")
# 将256灰度映射到70个字符上
def get_char(r,g,b,alpha = 256):
    if alpha == 0:
        return ' '
    length = len(ascii_char)
    gray = int(0.2126 * r + 0.7152 * g + 0.0722 * b)

    unit = (256.0 + 1)/length
    return ascii_char[int(gray/unit)]

if __name__ == '__main__':

    im = Image.open(IMG)
    im = im.resize((WIDTH,HEIGHT), Image.NEAREST)

    txt = ""

    for i in range(HEIGHT):
        for j in range(WIDTH):
            txt += get_char(*im.getpixel((j,i)))
        txt += '\n'

    print txt

    #字符画输出到文件
    if OUTPUT:
        with open(OUTPUT,'w') as f:
            f.write(txt)
    else:
        with open("output.txt",'w') as f:
            f.write(txt)