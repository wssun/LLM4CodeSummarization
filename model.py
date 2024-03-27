from threading import Thread
from typing import Iterator
from time import sleep
import openai
import torch
from transformers import pipeline, AutoConfig, AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer

DEFAULT_SYSTEM_PROMPT = """\
You are a helpful, respectful and honest assistant with a deep knowledge of code and software design. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.\n\nIf a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.\
"""

class CodeLLAMA:
    def __init__(self, args=None):
        self.config = AutoConfig.from_pretrained(args.model_name_or_path)
        self.config.pretraining_tp = 1
        self.model = AutoModelForCausalLM.from_pretrained(
            args.model_name_or_path,
            config=self.config,
            torch_dtype=torch.float16,
            load_in_4bit=True,
            device_map='auto',
            use_safetensors=False,
        )
        self.tokenizer = AutoTokenizer.from_pretrained(args.model_name_or_path)
        self.max_new_tokens = args.max_new_tokens
        self.temperature = args.temperature
        self.top_k = args.top_k
        self.top_p = args.top_p
        self.logger = args.logger


    def get_prompt(self, message: str, chat_history, system_prompt: str) -> str:
        texts = [f'<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n']
        do_strip = False
        for user_input, response in chat_history:
            user_input = user_input.strip() if do_strip else user_input
            do_strip = True
            texts.append(f'{user_input} [/INST] {response.strip()} </s><s>[INST] ')
        message = message.strip() if do_strip else message
        texts.append(f'{message} [/INST]')
        return ''.join(texts)


    def run(self, message: str, chat_history, system_prompt: str) -> Iterator[str]:
        prompt = self.get_prompt(message, chat_history, system_prompt)
        self.logger.info('input: '+prompt)
        self.logger.info('Length of input: '+str(len(prompt)))
        inputs = self.tokenizer([prompt], return_tensors='pt', add_special_tokens=False).to('cuda')

        streamer = TextIteratorStreamer(self.tokenizer, timeout=10., skip_prompt=True, skip_special_tokens=True)
        generate_kwargs = dict(inputs, streamer=streamer, max_new_tokens=self.max_new_tokens, do_sample=True,
                               top_p=self.top_p, top_k=self.top_k, temperature=self.temperature, num_beams=1, pad_token_id=2)
        t = Thread(target=self.model.generate, kwargs=generate_kwargs)
        t.start()

        outputs = []
        for text in streamer:
            outputs.append(text)
            yield ''.join(outputs)


    def ask(self, input, history=[], system_prompt=DEFAULT_SYSTEM_PROMPT):
        generator = self.run(message=input, chat_history=history, system_prompt=system_prompt)
        for x in generator:
            pass
        result = x
        self.logger.info('output: '+result)
        return result.strip()


class StarChat:
    def __init__(self, args):
        self.prompt_template = "<|system|>\n{system}<|end|>\n<|user|>\n{query}<|end|>\n<|assistant|>"
        self.pipe = pipeline("text-generation", model=args.model_name_or_path, torch_dtype=torch.bfloat16, device_map="auto")
        self.max_new_tokens = args.max_new_tokens
        self.temperature = args.temperature
        self.top_k = args.top_k
        self.top_p = args.top_p
        self.logger = args.logger

    def ask(self, input, history=[], system_prompt=DEFAULT_SYSTEM_PROMPT):
        prefix = ''
        for his in history:
            q, a = his
            p = q + '<|end|>\n<|assistant|>\n' + a + '<|end|>\n<|user|>\n'
            prefix = prefix + p
        input = prefix + input
        prompt = self.prompt_template.format(system=system_prompt, query=input)
        self.logger.info('input: ' + prompt)
        # self.logger.info('Length of input: ' + str(len(prompt)))
        outputs = self.pipe(prompt, max_new_tokens=self.max_new_tokens, do_sample=True, temperature=self.temperature,
                            top_k=self.top_k, top_p=self.top_p, eos_token_id=49155, pad_token_id=49155)
        generated_text = outputs[0]['generated_text']
        index = generated_text.rfind('<|assistant|>')
        result = generated_text[index + 13:]

        self.logger.info('output: ' + result)
        return result.strip()


class GPT:
    def __init__(self, args):
        self.openai_key = args.openai_key
        self.model_name = args.model_name_or_path
        self.logger = args.logger
        self.temperature = args.temperature
        self.top_p = args.top_p

    def ask(self, input, history=[], system_prompt=DEFAULT_SYSTEM_PROMPT):
        # print(self.temperature)
        openai.api_key = self.openai_key
        message = [{"role": "system", "content": system_prompt}]
        for his in history:
            q, a = his
            message.append({"role": "user", "content": q})
            message.append({"role": "assistant", "content": a})

        message.append({"role": "user","content": input})

        self.logger.info('message:')
        self.logger.info(message)
        response = openai.ChatCompletion.create(model=self.model_name, messages=message, temperature=self.temperature, top_p=self.top_p)
        result = response['choices'][0]['message']['content']
        self.logger.info('result:')
        self.logger.info(result)
        sleep(1)
        return result.strip()
