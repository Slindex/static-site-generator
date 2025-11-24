import unittest
from htmlnode import LeafNode
from textnode import TextNode, TextType
from helpers import text_node_to_html_node, split_nodes_delimiter


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
            
        