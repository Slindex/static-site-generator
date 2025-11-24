import unittest
from htmlnode import LeafNode
from textnode import TextNode, TextType
from helpers import (
    text_node_to_html_node,
    split_nodes_delimiter,
    extract_markdown_images,
    extract_markdown_links
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
        