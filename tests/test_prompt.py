"""Tests for the Prompt builder class."""

from philiprehberger_prompt_builder import Message, Prompt


class TestMessage:
    def test_to_dict(self):
        msg = Message(role="user", content="hello")
        assert msg.to_dict() == {"role": "user", "content": "hello"}

    def test_fields(self):
        msg = Message(role="system", content="you are helpful")
        assert msg.role == "system"
        assert msg.content == "you are helpful"


class TestPromptBasic:
    def test_system_message(self):
        result = Prompt().system("Be helpful.").render()
        assert result == [{"role": "system", "content": "Be helpful."}]

    def test_user_message(self):
        result = Prompt().user("Hello").render()
        assert result == [{"role": "user", "content": "Hello"}]

    def test_assistant_message(self):
        result = Prompt().assistant("Hi there").render()
        assert result == [{"role": "assistant", "content": "Hi there"}]

    def test_message_generic(self):
        result = Prompt().message("tool", "result").render()
        assert result == [{"role": "tool", "content": "result"}]

    def test_chaining(self):
        result = (
            Prompt()
            .system("Be helpful.")
            .user("Hi")
            .assistant("Hello!")
            .render()
        )
        assert len(result) == 3
        assert result[0]["role"] == "system"
        assert result[1]["role"] == "user"
        assert result[2]["role"] == "assistant"

    def test_render_messages(self):
        msgs = Prompt().system("test").user("hi").render_messages()
        assert len(msgs) == 2
        assert isinstance(msgs[0], Message)
        assert msgs[0].role == "system"

    def test_messages_property(self):
        p = Prompt().system("a").user("b")
        msgs = p.messages
        assert len(msgs) == 2
        # Ensure it returns a copy
        msgs.append(Message(role="user", content="c"))
        assert len(p.messages) == 2


class TestPlaceholders:
    def test_variable_substitution(self):
        result = Prompt().user("Hello {name}").render(name="World")
        assert result[0]["content"] == "Hello World"

    def test_multiple_variables(self):
        result = (
            Prompt()
            .system("You are a {role}.")
            .user("Tell me about {topic}.")
            .render(role="teacher", topic="Python")
        )
        assert result[0]["content"] == "You are a teacher."
        assert result[1]["content"] == "Tell me about Python."

    def test_unreplaced_placeholder(self):
        result = Prompt().user("Hello {name} and {other}").render(name="A")
        assert result[0]["content"] == "Hello A and {other}"

    def test_no_kwargs(self):
        result = Prompt().user("Hello {name}").render()
        assert result[0]["content"] == "Hello {name}"


class TestExample:
    def test_single_example(self):
        result = Prompt().example("input", "output").render()
        assert len(result) == 2
        assert result[0] == {"role": "user", "content": "input"}
        assert result[1] == {"role": "assistant", "content": "output"}

    def test_multiple_examples(self):
        result = (
            Prompt()
            .example("a", "b")
            .example("c", "d")
            .render()
        )
        assert len(result) == 4


class TestWithExamples:
    def test_batch_examples(self):
        examples = [("in1", "out1"), ("in2", "out2"), ("in3", "out3")]
        result = Prompt().with_examples(examples).render()
        assert len(result) == 6
        assert result[0] == {"role": "user", "content": "in1"}
        assert result[1] == {"role": "assistant", "content": "out1"}
        assert result[2] == {"role": "user", "content": "in2"}
        assert result[3] == {"role": "assistant", "content": "out2"}
        assert result[4] == {"role": "user", "content": "in3"}
        assert result[5] == {"role": "assistant", "content": "out3"}

    def test_empty_examples(self):
        result = Prompt().with_examples([]).render()
        assert result == []

    def test_chaining_with_examples(self):
        result = (
            Prompt()
            .system("Classify sentiment.")
            .with_examples([("I love it", "positive"), ("I hate it", "negative")])
            .user("It's okay")
            .render()
        )
        assert len(result) == 6
        assert result[0]["role"] == "system"
        assert result[5]["role"] == "user"
        assert result[5]["content"] == "It's okay"

    def test_with_examples_supports_placeholders(self):
        result = (
            Prompt()
            .with_examples([("{greeting}", "Hello!")])
            .render(greeting="Hi there")
        )
        assert result[0]["content"] == "Hi there"


class TestConditional:
    def test_include_true(self):
        result = Prompt().conditional(True, "user", "included").render()
        assert len(result) == 1

    def test_include_false(self):
        result = Prompt().conditional(False, "user", "excluded").render()
        assert len(result) == 0

    def test_chaining(self):
        result = (
            Prompt()
            .system("Hi")
            .conditional(True, "user", "yes")
            .conditional(False, "user", "no")
            .user("end")
            .render()
        )
        assert len(result) == 3


class TestMerge:
    def test_basic_merge(self):
        a = Prompt().system("System A").user("User A")
        b = Prompt().user("User B")
        result = a.merge(b).render()
        assert len(result) == 3
        assert result[0]["content"] == "System A"

    def test_system_priority(self):
        a = Prompt().system("A system")
        b = Prompt().system("B system").user("B user")
        result = a.merge(b).render()
        # Self system takes priority
        system_msgs = [m for m in result if m["role"] == "system"]
        assert len(system_msgs) == 1
        assert system_msgs[0]["content"] == "A system"

    def test_fallback_system(self):
        a = Prompt().user("A user")
        b = Prompt().system("B system").user("B user")
        result = a.merge(b).render()
        system_msgs = [m for m in result if m["role"] == "system"]
        assert len(system_msgs) == 1
        assert system_msgs[0]["content"] == "B system"

    def test_merge_does_not_mutate(self):
        a = Prompt().system("A").user("A user")
        b = Prompt().user("B user")
        merged = a.merge(b)
        assert len(a.messages) == 2
        assert len(b.messages) == 1
        assert len(merged.messages) == 3


class TestExpectJson:
    def test_basic(self):
        result = Prompt().system("Help me").expect_json().render()
        assert len(result) == 2
        assert result[1]["role"] == "system"
        assert "JSON" in result[1]["content"]
        assert "No additional text" in result[1]["content"]

    def test_with_description(self):
        result = (
            Prompt()
            .expect_json(description='{"name": string, "age": number}')
            .render()
        )
        assert "Expected structure" in result[0]["content"]
        assert '{"name": string, "age": number}' in result[0]["content"]

    def test_chaining(self):
        result = (
            Prompt()
            .system("Extract data.")
            .user("Parse this: {text}")
            .expect_json()
            .render(text="John is 30")
        )
        assert len(result) == 3
        assert result[2]["role"] == "system"


class TestExpectList:
    def test_basic(self):
        result = Prompt().system("Help me").expect_list().render()
        assert len(result) == 2
        assert result[1]["role"] == "system"
        assert "list" in result[1]["content"]

    def test_with_description(self):
        result = Prompt().expect_list(description="a short phrase").render()
        assert "Each item should be" in result[0]["content"]
        assert "a short phrase" in result[0]["content"]

    def test_chaining(self):
        result = (
            Prompt()
            .system("List items.")
            .user("Give me colors")
            .expect_list()
            .render()
        )
        assert len(result) == 3


class TestEstimateTokens:
    def test_basic_estimate(self):
        p = Prompt().system("Hello world this is a test")
        tokens = p.estimate_tokens()
        assert isinstance(tokens, int)
        assert tokens > 0

    def test_with_variables(self):
        p = Prompt().user("Tell me about {topic}")
        tokens = p.estimate_tokens(topic="artificial intelligence")
        assert tokens > 0

    def test_empty_prompt(self):
        p = Prompt()
        tokens = p.estimate_tokens()
        assert tokens == 0

    def test_longer_prompt_more_tokens(self):
        short = Prompt().user("Hi")
        long = Prompt().user("This is a much longer message with many more words in it")
        assert long.estimate_tokens() > short.estimate_tokens()
