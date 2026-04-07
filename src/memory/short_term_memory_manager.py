class ShortTermMemoryManager:
    def __init__(self):
        self.buffer = []

    def add_message(self, role, content):
        self.buffer.append({"role": role, "content": content})

    def get_history(self):
        if not self.buffer:
            return "No previous chat history in this session."

        history_string = ""
        for msg in self.buffer:
            history_string += f"{msg["role"]}: {msg['content']}\n"

        return history_string.strip()

    def get_raw_history(self):
        return list(self.buffer)

    def clear(self):
        self.buffer.clear()