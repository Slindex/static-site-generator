import unittest
from htmlnode import HTMLNode, LeafNode


class TestHTMLNode(unittest.TestCase):
    def test_no_props(self):
        node = HTMLNode("<p>", "Hola! Soy texto")
        self.assertEqual(node.props, None)
    
    def test_no_children(self):
        node = HTMLNode("<p>", "Hola! Soy texto")
        self.assertEqual(node.children, None)
    
    def test_props_to_html(self):
        props = {
            "href": "https://www.google.com",
            "target": "_blank",
        }
        node = HTMLNode("<p>", "Hola! Soy texto", props=props)
        self.assertEqual(
            node.props_to_html(), 
            ' href="https://www.google.com" target="_blank"'
        )
    
    def no_props_to_html(self):
        node = HTMLNode("<p>", "Hola! Soy texto")
        self.assertEqual(node.props_to_html(), "")

class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_a(self):
        props = {
            "href": "https://www.google.com",
            "target": "_blank",
        }
        node = LeafNode("a", "Click me!", props)
        self.assertEqual(node.to_html(), '<a href="https://www.google.com" target="_blank">Click me!</a>')