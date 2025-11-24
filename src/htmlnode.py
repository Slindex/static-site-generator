class HTMLNode():
    def __init__(
            self, 
            tag: str | None = None, 
            value: str | None = None, 
            children: list | None = None, 
            props: dict | None = None
    ):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props
    
    def to_html(self):
        raise NotImplementedError
    
    def props_to_html(self):
        if not self.props:
            return ""
        
        html = ""

        for key, value in self.props.items():
            html += f' {key}="{value}"'
        
        return html
    
    def __repr__(self):
        lines = [
            "HTMLNode(",
            f"  tag: {self.tag}",
            f"  value: {self.value}",
            f"  children: {self.children}",
            f"  props: {self.props}",
            ")"
        ]

        return "\n".join(lines)
    
    def __eq__(self, other):
        if not isinstance(other, HTMLNode):
            return NotImplemented
        
        return (
            self.tag == other.tag and
            self.value == other.value and
            self.children == other.children and
            self.props == other.props
        )
    

class LeafNode(HTMLNode):
    def __init__(self, tag:str|None, value:str, props:dict|None = None):
        if value is None:
            raise ValueError("LeafNode must contain a value")

        super().__init__(tag=tag, value=value, children=None, props=props)
    
    def to_html(self):
        if self.tag is None:
            return self.value

        tag = self.tag
        value = self.value
        props = self.props_to_html()

        return f"<{tag}{props}>{value}</{tag}>"


class ParentNode(HTMLNode):
    def __init__(self, tag:str, children:list, props:dict|None = None):
        if tag is None or children is None:
            raise ValueError("ParentNode must have a tag and a children")
        
        super().__init__(tag=tag, children=children, props=props)
    
    def to_html(self):
        if self.tag is None:
            raise ValueError("ParentNode must have a tag")
        if not self.children:
            raise ValueError("ParentNode must have at least one children")
        
        html = f"<{self.tag}>"

        for child in self.children:
            html += child.to_html()
        
        html += f"</{self.tag}>"

        return html