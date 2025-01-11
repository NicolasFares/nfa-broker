from pydantic import BaseModel


class TestMessage(BaseModel):
    """Test message model"""
    id: int
    content: str

    @classmethod
    def routing_key(cls) -> str:
        return "test.message"


if __name__ == "__main__":
    message = TestMessage(id=1, content="Hello, World!")
    print(message.model_dump())
    print(hash(message))
