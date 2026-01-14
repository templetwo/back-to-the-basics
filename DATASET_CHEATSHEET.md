# BTB Memory Dataset Cheatsheet

Quick reference for generating vast agent memory datasets.

---

## 📋 Quick Template

```python
memories = [
    {'content': 'What happened', 'outcome': 'TYPE', 'tool': 'TOOL', 'METADATA_KEY': 'value', 'summary': 'short_name'},
]
```

---

## 🎯 Outcome Types

| Outcome | Tool | Metadata Required | Example |
|---------|------|------------------|---------|
| **success** | code_interpreter | task_type | `'task_type': 'debug'` |
| **success** | web_search | domain | `'domain': 'technical'` |
| **success** | file_operation | - | No extra metadata |
| **success** | conversation | - | No extra metadata |
| **failure** | code_interpreter | error_type | `'error_type': 'runtime'` |
| **failure** | web_search | reason | `'reason': 'no_results'` |
| **failure** | file_operation | - | No extra metadata |
| **learning** | - | insight_type | `'insight_type': 'pattern'` |
| **interaction** | - | sentiment | `'sentiment': 'positive'` |

---

## 🔧 Metadata Values

### task_type (code_interpreter success)
- `'write'` - New code
- `'debug'` - Bug fixes
- `'refactor'` - Code restructuring
- `'explain'` - Code explanations

### domain (web_search success)
- `'technical'` - Technical docs, APIs
- `'research'` - Academic papers
- `'general'` - General searches

### error_type (code_interpreter failure)
- `'syntax'` - Syntax errors
- `'runtime'` - Runtime errors
- `'logic'` - Logic bugs
- `'timeout'` - Timeouts, infinite loops

### reason (web_search failure)
- `'no_results'` - No results found
- `'blocked'` - Access blocked
- `'irrelevant'` - Irrelevant results

### insight_type (learning)
- `'pattern'` - Observed patterns
- `'correction'` - Learned corrections
- `'preference'` - User preferences
- `'fact'` - Factual knowledge

### sentiment (interaction)
- `'positive'` - Positive feedback
- `'neutral'` - Neutral observation
- `'negative'` - Negative feedback

---

## 📊 Target Distribution

```
Total: 1000 memories

Outcomes:
  success:     600 (60%)
  failure:     200 (20%)
  learning:    120 (12%)
  interaction:  80 (8%)

Tools (in successes):
  code_interpreter: 300
  web_search:       120
  file_operation:    90
  conversation:      90

Error types (in failures):
  runtime:  80
  syntax:   50
  logic:    50
  timeout:  20
```

---

## ⚡ Fast Generation Patterns

### Code Success Block
```python
# 100 debugging successes
[{'content': f'Fixed bug #{i} in module X', 'outcome': 'success',
  'tool': 'code_interpreter', 'task_type': 'debug',
  'summary': f'bug_fix_{i}'} for i in range(100)]
```

### Code Failure Block
```python
# 50 runtime errors
[{'content': f'Runtime error in function {i}', 'outcome': 'failure',
  'tool': 'code_interpreter', 'error_type': 'runtime',
  'summary': f'runtime_err_{i}'} for i in range(50)]
```

### Learning Block
```python
# 30 pattern insights
[{'content': f'Observed pattern #{i} in codebase', 'outcome': 'learning',
  'insight_type': 'pattern', 'summary': f'pattern_{i}'} for i in range(30)]
```

### Interaction Block
```python
# 20 positive interactions
[{'content': f'User happy with result #{i}', 'outcome': 'interaction',
  'sentiment': 'positive', 'summary': f'user_pos_{i}'} for i in range(20)]
```

---

## 🎨 Content Templates

### Realistic Code Success
```
"Implemented {feature} using {technology}"
"Fixed {bug_type} in {component} by {solution}"
"Refactored {module} to use {pattern}"
"Debugged {issue} - root cause was {cause}"
"Optimized {function} reducing latency by {percent}%"
```

### Realistic Code Failure
```
"{ErrorType} when {action} - {reason}"
"Syntax error - {missing/wrong} in {location}"
"Logic error in {function} broke {functionality}"
"Timeout error - {cause} hit max {limit}"
```

### Realistic Learning
```
"Codebase uses {pattern} for {purpose}"
"Learned to always {action} before {another_action}"
"User prefers {option_a} over {option_b}"
"Fact: {technology} {does_what} in {context}"
```

### Realistic Interaction
```
"User {emotion} with {aspect} of {deliverable}"
"User requested {clarification/change/feature}"
"User {praised/criticized} {specific_thing}"
```

---

## 🚀 One-Liner Generator

```python
# 1000 memories in one expression
memories = (
    [{'content': f'Fixed bug #{i}', 'outcome': 'success', 'tool': 'code_interpreter', 'task_type': 'debug', 'summary': f'bug_{i}'} for i in range(300)] +
    [{'content': f'Implemented feature #{i}', 'outcome': 'success', 'tool': 'code_interpreter', 'task_type': 'write', 'summary': f'feat_{i}'} for i in range(200)] +
    [{'content': f'Runtime error #{i}', 'outcome': 'failure', 'tool': 'code_interpreter', 'error_type': 'runtime', 'summary': f'err_{i}'} for i in range(150)] +
    [{'content': f'Syntax error #{i}', 'outcome': 'failure', 'tool': 'code_interpreter', 'error_type': 'syntax', 'summary': f'syn_{i}'} for i in range(50)] +
    [{'content': f'Found docs on topic #{i}', 'outcome': 'success', 'tool': 'web_search', 'domain': 'technical', 'summary': f'research_{i}'} for i in range(120)] +
    [{'content': f'Learned pattern #{i}', 'outcome': 'learning', 'insight_type': 'pattern', 'summary': f'pattern_{i}'} for i in range(100)] +
    [{'content': f'User happy #{i}', 'outcome': 'interaction', 'sentiment': 'positive', 'summary': f'pos_{i}'} for i in range(50)] +
    [{'content': f'User frustrated #{i}', 'outcome': 'interaction', 'sentiment': 'negative', 'summary': f'neg_{i}'} for i in range(30)]
)
```

---

## ✅ Validation Checklist

Before passing to agent:

- [ ] All dicts have `'content'`, `'outcome'`, `'summary'`
- [ ] Summaries are lowercase_with_underscores
- [ ] No duplicate summaries
- [ ] Required metadata present for each outcome/tool combo
- [ ] Distribution matches targets (60/20/12/8)
- [ ] Valid Python syntax (test with `json.dumps(memories)`)

---

## 🔥 Pro Tips

1. **Unique summaries**: Add counter/index to ensure uniqueness
2. **Timestamp spread**: Use `time.sleep(0.001)` when storing
3. **Realistic content**: Mix specific details (function names, error types)
4. **Variety**: Don't just copy-paste - vary the language
5. **Sessions**: Group by theme for realistic workflow

---

## 📦 Storage One-Liner

```python
from memory import MemoryEngine
m = MemoryEngine(root='agent_brain')
[m.remember(**mem) for mem in memories]
```

---

*Copy this cheatsheet to your heavier agent for instant dataset generation.*
