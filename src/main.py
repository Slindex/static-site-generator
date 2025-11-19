from textnode import TextNode, TextType


def main():
    bootdev = TextNode("Testing text", TextType.BOLD, "https://www.boot.dev")
    print(bootdev)

if __name__ == '__main__':
    main()