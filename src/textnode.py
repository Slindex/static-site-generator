from .enums import TextType
    

class TextNode():
    def __init__(
            self, 
            text: str, 
            text_type: TextType, 
            url: str | None = None
    ):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        if not isinstance(other, TextNode):
            return NotImplemented

        return (
            self.text == other.text and
            self.text_type == other.text_type and
            self.url == other.url
        )
    
    def __repr__(self):
        TEXT = self.text
        TEXT_TYPE = self.text_type.value
        URL = self.url

        return f"TextNode({TEXT}, {TEXT_TYPE}, {URL})"
