from pydantic import BaseModel


class Config(BaseModel):
    max_new_tokens: int = 512
    do_sample: bool = True
    temperature: float = 1.2
    top_p: float = 0.9
    repetition_penalty: float = 1.1


class OpenAIConfig(BaseModel):
    model: str = "gemma"
    max_tokens: int = 1024
    temperature: float = 0.1
    top_p: float = 0.9
    frequency_penalty: float = 0.1
