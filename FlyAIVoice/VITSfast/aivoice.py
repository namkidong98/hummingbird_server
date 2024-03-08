from FlyAIVoice import module_test

class AIvoice():
    def __init__(self, vits:module_test) -> None:
        self.generator = vits
    
    def tts(
        self,
        generated_text:str,
    ):
    # ) -> tuple[str, str]: 반환은 원본 오디오 그냥 파일..?
        audio = self.generator.generate(
             generated_text
        )

        return audio