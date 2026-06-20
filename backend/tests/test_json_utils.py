import pytest

from app.services.json_utils import coerce_types, extract_json, safe_parse_json


class TestExtractJson:
    def test_plain_json(self):
        assert extract_json('{"a": 1}') == '{"a": 1}'

    def test_markdown_wrapped(self):
        assert extract_json('```json\n{"a": 1}\n```') == '{"a": 1}'

    def test_trailing_text(self):
        result = extract_json('Here is the result:\n{"a": 1}\nHope this helps!')
        assert result == '{"a": 1}'

    def test_leading_text(self):
        result = extract_json('The JSON is: {"key": "value"}')
        assert result == '{"key": "value"}'

    def test_array_json(self):
        result = extract_json('```json\n[{"q": 1}, {"q": 2}]\n```')
        assert result == '[{"q": 1}, {"q": 2}]'

    def test_nested_braces(self):
        text = '{"a": {"b": 1}, "c": 2}'
        assert extract_json(text) == text

    def test_no_json(self):
        assert extract_json("no json here") == "no json here"


class TestSafeParseJson:
    def test_clean_json(self):
        assert safe_parse_json('{"a": 1}') == {"a": 1}

    def test_markdown_wrapped(self):
        assert safe_parse_json('```json\n{"a": 1}\n```') == {"a": 1}

    def test_trailing_comma(self):
        assert safe_parse_json('{"a": 1, "b": 2,}') == {"a": 1, "b": 2}

    def test_array(self):
        result = safe_parse_json('[{"q": 1}]')
        assert result == [{"q": 1}]

    def test_fallback_on_invalid(self):
        assert safe_parse_json("not json", fallback={}) == {}

    def test_raises_without_fallback(self):
        with pytest.raises(ValueError):
            safe_parse_json("not json")

    def test_trailing_text(self):
        result = safe_parse_json('{"consistent": true}\n\nThis is my analysis.')
        assert result == {"consistent": True}


class TestCoerceTypes:
    def test_bool_string(self):
        data = {"consistent": "true", "safe": "false"}
        result = coerce_types(data, {"consistent": bool, "safe": bool})
        assert result["consistent"] is True
        assert result["safe"] is False

    def test_float_string(self):
        data = {"score": "0.85"}
        result = coerce_types(data, {"score": float})
        assert result["score"] == 0.85

    def test_list_from_string(self):
        data = {"weak_points": "algebra, geometry, calculus"}
        result = coerce_types(data, {"weak_points": list})
        assert result["weak_points"] == ["algebra", "geometry", "calculus"]

    def test_already_correct_types(self):
        data = {"consistent": True, "score": 0.9}
        result = coerce_types(data, {"consistent": bool, "score": float})
        assert result["consistent"] is True
        assert result["score"] == 0.9

    def test_missing_key_ignored(self):
        data = {"a": 1}
        result = coerce_types(data, {"missing": bool})
        assert result == {"a": 1}

    def test_non_dict_passthrough(self):
        data = [1, 2, 3]
        assert coerce_types(data, {"a": bool}) == [1, 2, 3]
