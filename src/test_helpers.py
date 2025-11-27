import unittest
from htmlnode import LeafNode
from textnode import TextNode, TextType
from helpers import (
    text_node_to_html_node,
    split_nodes_delimiter,
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_link,
    split_nodes_image,
    text_to_textnodes,
    markdown_to_blocks
)


class TestTextNodeToHTML(unittest.TestCase):
    def test_text(self):
        node = TextNode("This is a text node", TextType.PLAIN)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")
    
    def test_bold(self):
        value = "This is a bold node"
        node = TextNode(value, TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node, LeafNode("b", value))
        self.assertEqual(html_node.value, value)
        self.assertEqual(html_node.tag, "b")
    
    def test_link(self):
        value = "This is a link node"
        url = "http://google.com"
        node = TextNode(value, TextType.LINK, url)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node, LeafNode("a", value, {"href": url}))

    def test_image(self):
        value = "perro ladrando"
        url = "http://pinterest.com/landscape"
        props = {
            "src": url,
            "alt": "perro ladrando"
        }
        node = TextNode(value, TextType.IMAGE, url)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node, LeafNode("img", "", props))

class TestSplitNodesDelimiter(unittest.TestCase):
    def test_nodes_no_text(self):
        nodes = [
            TextNode("Click aqui", TextType.LINK, "https://google.com"),
            TextNode("Acerca de", TextType.LINK, "https://google.com"),
            TextNode("Productos", TextType.LINK, "https://google.com")
        ]
        new_nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
        expected_nodes = nodes
        self.assertEqual(new_nodes, expected_nodes)
    
    def test_markdown_exception(self):
        nodes = [
            TextNode("Este `codigo no cierra con un backtick", TextType.PLAIN)
        ]
        
        with self.assertRaises(Exception):
            split_nodes_delimiter(nodes, "`", TextType.CODE)

class TestExtractMarkdownImages(unittest.TestCase):
    def test_standard_case(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)
    
    def test_link(self):
        matches = extract_markdown_images(
            "This is text with an [image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([], matches)

    def test_multiple_groups(self):
        text = (
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) "
            "and a second ![image](https://google.com) "
            "and a third ![image](https://facebook.com)"
        )
        matches = extract_markdown_images(text)
        expected = [
            ("image", "https://i.imgur.com/zjjcJKZ.png"),
            ("image", "https://google.com"),
            ("image", "https://facebook.com"),
        ]
        self.assertListEqual(expected, matches)

class TestExtractMarkdownLinks(unittest.TestCase):
    def test_standard_case(self):
        matches = extract_markdown_links(
            "This is text with an [link](https://i.imgur.com/zjjcJKZ.com)"
        )
        self.assertListEqual([("link", "https://i.imgur.com/zjjcJKZ.com")], matches)
    
    def test_image_and_link(self):
        text = (
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) "
            "and a [link](https://google.com)"
        )
        matches = extract_markdown_links(text)
        self.assertListEqual([("link", "https://google.com")], matches)
    
    def test_multiple_groups(self):
        text = (
            "This is text with an [link](https://i.imgur.com/zjjcJKZ.png) "
            "and a second [link](https://google.com) "
            "and a third [link](https://facebook.com)"
        )
        matches = extract_markdown_links(text)
        expected = [
            ("link", "https://i.imgur.com/zjjcJKZ.png"),
            ("link", "https://google.com"),
            ("link", "https://facebook.com"),
        ]
        self.assertListEqual(expected, matches)

class TestSplitNodes(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.PLAIN,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.PLAIN),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.PLAIN),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )
    
    def test_split_links(self):
        old_nodes = [
            TextNode(
                "[to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
                TextType.PLAIN
            ),
            TextNode(
                "This is a [game](https://friv.com) link",
                TextType.PLAIN
            )
        ]
        new_nodes = split_nodes_link(old_nodes)
        self.assertListEqual(
            [
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.PLAIN),
                TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"),
                TextNode("This is a ", TextType.PLAIN),
                TextNode("game", TextType.LINK, "https://friv.com"),
                TextNode(" link", TextType.PLAIN),
            ],
            new_nodes
        )

class TestTextToTextNodes(unittest.TestCase):
    def test_all_splitting(self):
        text = (
            "This is **text** with an _italic_ word and a `code block` "
            "and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        )
        new_nodes = text_to_textnodes(text)
        self.assertListEqual(
            new_nodes,
            [
                TextNode("This is ", TextType.PLAIN),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.PLAIN),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.PLAIN),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.PLAIN),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.PLAIN),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ]
        )
    
    def test_one_element(self):
        text = "**text**"
        new_nodes = text_to_textnodes(text)
        self.assertListEqual(
            new_nodes,
            [
                TextNode("text", TextType.BOLD)
            ]
        )
    
    def test_one_image(self):
        text = "![Testing](https://google.com)"
        new_nodes = text_to_textnodes(text)
        self.assertListEqual(
            new_nodes,
            [
                TextNode("Testing", TextType.IMAGE, "https://google.com")
            ]
        )        

class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )
    
    def test_one_block(self):
        md = "I'm one block"
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "I'm one block"
            ],
        )

    def test_empty_blocks(self):
        md = """
This is **bolded** paragraph




This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line



- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )
