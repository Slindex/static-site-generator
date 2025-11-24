import re
from textnode import TextNode, TextType
from htmlnode import LeafNode


def text_node_to_html_node(text_node: TextNode):
    if not isinstance(text_node, TextNode):
        raise TypeError("argument should be a TextNode object")
    
    match text_node.text_type:
        case TextType.PLAIN:
            return LeafNode(None, text_node.text)
        case TextType.BOLD:
            return LeafNode("b", text_node.text)
        case TextType.ITALIC:
            return LeafNode("i", text_node.text)
        case TextType.CODE:
            return LeafNode("code", text_node.text)
        case TextType.LINK:
            props = {
                "href": text_node.url
            }
            return LeafNode("a", text_node.text, props)
        case TextType.IMAGE:
            props = {
                "src": text_node.url,
                "alt": text_node.text
            }
            return LeafNode("img", "", props)
        case _:
            raise Exception("Text Node has an invalid Text Type")
        
def split_nodes_delimiter(old_nodes:list[TextNode], delimiter:str, text_type:TextType):
    new_nodes = []

    for node in old_nodes:
        if node.text_type is not TextType.PLAIN:
            new_nodes.append(node)
            continue
        
        text = node.text
        plain = ""
        other = ""
        stack = []

        for i in range(len(text)):
            if text[i] == delimiter[0]:
                if plain:
                    new_nodes.append(TextNode(plain, TextType.PLAIN))
                    plain = ""
                if text[i-1] == delimiter[0]:
                    continue
                stack.append(text[i])
                continue
            
            if len(stack) == 2:
                stack = []
                new_nodes.append(TextNode(other, text_type))
                other = ""
                plain += text[i]
                continue

            if stack:
                other += text[i]
            else:
                plain += text[i]

        if plain:
            new_nodes.append(TextNode(plain, TextType.PLAIN))
        
        if stack:
            raise Exception("Invalid markdown syntax")

    return new_nodes

def extract_markdown_images(text:str):
    return re.findall(r"\!\[(.*?)\]\((.*?)\)", text)

def extract_markdown_links(text:str):
    return re.findall(r"(?<!\!)\[(.*?)\]\((.*?)\)", text)
