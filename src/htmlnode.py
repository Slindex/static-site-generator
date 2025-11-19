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