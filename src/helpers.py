import re
from textnode import TextNode, TextType
from htmlnode import LeafNode


def text_node_to_html_node(text_node: TextNode) -> LeafNode:
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
        
def split_nodes_delimiter(old_nodes:list[TextNode], delimiter:str, text_type:TextType) -> list[TextNode]:
    new_nodes = []

    for node in old_nodes:
        if node.text_type is not TextType.PLAIN:
            new_nodes.append(node)
            continue

        if node.text[0] == node.text[-1] == delimiter[0]:
            text = ""

            for char in node.text:
                if char != delimiter[0]:
                    text += char

            new_nodes.append(TextNode(text, text_type))
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

def extract_markdown_images(text:str) -> list[tuple]:
    return re.findall(r"\!\[(.*?)\]\((.*?)\)", text)

def extract_markdown_links(text:str) -> list[tuple]:
    return re.findall(r"(?<!\!)\[(.*?)\]\((.*?)\)", text)

def split_nodes_link(old_nodes:list[TextNode]) -> list[TextNode]:
    new_nodes = []

    for node in old_nodes:
        if node.text_type is not TextType.PLAIN:
            new_nodes.append(node)
            continue
        
        links = extract_markdown_links(node.text)
        texts = re.split(r"(?<!\!)\[.*?\]\(.*?\)", node.text)

        while "" in texts:
            texts.remove("")

        iters = max(len(links), len(texts))

        for i in range(iters):
            if node.text[0] == "[":
                link_node = TextNode(links[i][0], TextType.LINK, links[i][1])
                new_nodes.append(link_node)

                try:
                    text_node = TextNode(texts[i], TextType.PLAIN)
                    new_nodes.append(text_node)
                    continue
                except IndexError:
                    break
            
            text_node = TextNode(texts[i], TextType.PLAIN)
            new_nodes.append(text_node)

            try:
                link_node = TextNode(links[i][0], TextType.LINK, links[i][1])
                new_nodes.append(link_node)
            except IndexError:
                break
    
    return new_nodes

def split_nodes_image(old_nodes:list[TextNode]) -> list[TextNode]:
    new_nodes = []

    for node in old_nodes:
        if node.text_type is not TextType.PLAIN:
            new_nodes.append(node)
            continue
        
        images = extract_markdown_images(node.text)
        texts = re.split(r"\!\[.*?\]\(.*?\)", node.text)

        while "" in texts:
            texts.remove("")

        iters = max(len(images), len(texts))

        for i in range(iters):
            if node.text[0] == "!":
                link_node = TextNode(images[i][0], TextType.IMAGE, images[i][1])
                new_nodes.append(link_node)

                try:
                    text_node = TextNode(texts[i], TextType.PLAIN)
                    new_nodes.append(text_node)
                    continue
                except IndexError:
                    break
            
            text_node = TextNode(texts[i], TextType.PLAIN)
            new_nodes.append(text_node)

            try:
                link_node = TextNode(images[i][0], TextType.IMAGE, images[i][1])
                new_nodes.append(link_node)
            except IndexError:
                break
    
    return new_nodes

def text_to_textnodes(text:str) -> list[TextNode]:
    base_node = TextNode(text, TextType.PLAIN)

    new_nodes = split_nodes_delimiter([base_node], "`", TextType.CODE)
    new_nodes = split_nodes_delimiter(new_nodes, "_", TextType.ITALIC)
    new_nodes = split_nodes_delimiter(new_nodes, "**", TextType.BOLD)
    new_nodes = split_nodes_link(new_nodes)
    new_nodes = split_nodes_image(new_nodes)

    return new_nodes

def markdown_to_blocks(markdown:str) -> list[str]:
    if "\n\n" not in markdown:
        return [markdown.strip()]
    
    blocks = markdown.split("\n\n")

    while "" in blocks:
        blocks.remove("")

    for i in range(len(blocks)):
        blocks[i] = blocks[i].strip()
    
    return blocks