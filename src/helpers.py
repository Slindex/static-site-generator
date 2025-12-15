import re
from .textnode import TextNode
from .htmlnode import LeafNode, ParentNode
from .enums import TextType, BlockType


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

def block_to_blocktype(block:str):
    headings = ("# ", "## ", "### ", "#### ", "##### ", "###### ")
    lines = block.split("\n")

    if block.startswith(headings):
        return BlockType.HEADING
    
    if block.startswith("```") and block.endswith("```"):
        return BlockType.CODE
    
    if block.startswith(">"):
        for line in lines:
            if not line.startswith(">"):
                raise Exception("All block lines must start with '>'")
        
        return BlockType.QUOTE
    
    if block.startswith("- "):
        for line in lines:
            if not line.startswith("- "):
                raise Exception("All block lines must start with '- '")
        
        return BlockType.UNORDERED_LIST
    
    if block.startswith("1. "):
        for i in range(2, len(lines)+1):
            if not lines[i-1].startswith(f"{i}. "):
                raise Exception("All block lines must start with proper sequence: (1. ,2. ,3. , etc...)")
        
        return BlockType.ORDERED_LIST
    
    return BlockType.PARAGRAPH

def markdown_to_html_node(markdown:str):
    blocks = markdown_to_blocks(markdown)
    root_node = ParentNode("div", [])

    for block in blocks:
        block_type = block_to_blocktype(block)
        text_nodes = text_to_textnodes(block)
        md_children = []

        for text_node in text_nodes:
            html_child = text_node_to_html_node(text_node)
            md_children.append(html_child)
    
        if block_type == BlockType.PARAGRAPH:
            for node in md_children:
                node.value = node.value.replace("\n", " ")
            block_node = ParentNode("p", md_children)

        elif block_type == BlockType.HEADING:
            syntax = block.split(" ")[0]
            h_type = len(syntax)

            for node in md_children:
                node.value = node.value[h_type+1:]
            block_node = ParentNode(f"h{h_type}", md_children)
        
        elif block_type == BlockType.QUOTE:
            for node in md_children:
                lines = node.value.split("\n")
                text = ""

                for line in lines:
                    line = line.replace("> ", "") + " "
                    text += line

                node.value = text.strip()
            block_node = ParentNode("blockquote", md_children)
        
        elif block_type == BlockType.UNORDERED_LIST:
            for node in md_children:
                lines = node.value.split("\n")
                text = ""

                for line in lines:
                    line = line.replace("- ", "<li>") + "</li>"
                    text += line

                node.value = text.strip()
            block_node = ParentNode("ul", md_children)

        elif block_type == BlockType.ORDERED_LIST:
            for node in md_children:
                lines = node.value.split("\n")
                text = ""

                for i in range(1,len(lines)+1):
                    line = lines[i-1]
                    line = line.replace(f"{i}. ", "<li>") + "</li>"
                    text += line

                node.value = text.strip()
            block_node = ParentNode("ol", md_children)

        else:
            continue
        
        root_node.add_child(block_node)

    return root_node
