# BTB Memory Dataset Format Specification

**Purpose:** This document defines the exact format for generating vast, realistic agent memory datasets for BTB MCP server testing.

---

## Memory Entry Format

Each memory is a Python dictionary with the following structure:

```python
{
    'content': str,      # The actual memory content (required)
    'outcome': str,      # One of: 'success', 'failure', 'learning', 'interaction' (required)
    'tool': str,         # Tool used (required for most outcomes)
    'summary': str,      # Brief filename-safe summary (optional, auto-generated if omitted)
    **metadata           # Additional routing keys based on outcome/tool combination
}
```

---

## Outcome Types & Required Metadata

### 1. SUCCESS

**Required:**
- `outcome`: `"success"`
- `tool`: One of tools below
- `content`: Description of what succeeded

**Tools & Their Metadata:**

#### A. code_interpreter
```python
{
    'content': 'Successfully implemented feature X',
    'outcome': 'success',
    'tool': 'code_interpreter',
    'task_type': 'write',    # REQUIRED: 'write', 'debug', 'refactor', 'explain'
    'summary': 'feature_x_impl'
}
```

**task_type values:**
- `'write'` - Writing new code
- `'debug'` - Fixing bugs
- `'refactor'` - Restructuring existing code
- `'explain'` - Explaining code concepts

#### B. web_search
```python
{
    'content': 'Found documentation on OAuth2 flows',
    'outcome': 'success',
    'tool': 'web_search',
    'domain': 'technical',   # REQUIRED: 'technical', 'research', 'general'
    'summary': 'oauth2_docs'
}
```

**domain values:**
- `'technical'` - Technical documentation, API refs
- `'research'` - Academic papers, research articles
- `'general'` - General web searches

#### C. file_operation
```python
{
    'content': 'Successfully migrated data files to new structure',
    'outcome': 'success',
    'tool': 'file_operation',
    'summary': 'data_migration'
}
```

#### D. conversation
```python
{
    'content': 'Explained async/await patterns to user',
    'outcome': 'success',
    'tool': 'conversation',
    'summary': 'async_explanation'
}
```

---

### 2. FAILURE

**Required:**
- `outcome`: `"failure"`
- `tool`: One of tools below
- `content`: Description of what failed

**Tools & Their Metadata:**

#### A. code_interpreter
```python
{
    'content': 'TypeError when calling async function without await',
    'outcome': 'failure',
    'tool': 'code_interpreter',
    'error_type': 'runtime',   # REQUIRED: 'syntax', 'runtime', 'logic', 'timeout'
    'summary': 'async_await_fail'
}
```

**error_type values:**
- `'syntax'` - Syntax errors (missing colons, brackets, etc.)
- `'runtime'` - Runtime errors (TypeError, ValueError, etc.)
- `'logic'` - Logic errors (incorrect behavior, broken tests)
- `'timeout'` - Timeout errors (infinite loops, max recursion)

#### B. web_search
```python
{
    'content': 'Search returned no relevant results for niche topic',
    'outcome': 'failure',
    'tool': 'web_search',
    'reason': 'no_results',   # REQUIRED: 'no_results', 'blocked', 'irrelevant'
    'summary': 'search_fail'
}
```

**reason values:**
- `'no_results'` - No results found
- `'blocked'` - Access blocked or rate limited
- `'irrelevant'` - Results not relevant to query

#### C. file_operation
```python
{
    'content': 'Permission denied on system directory',
    'outcome': 'failure',
    'tool': 'file_operation',
    'summary': 'permission_denied'
}
```

#### D. unknown (fallback)
```python
{
    'content': 'Unclassified failure occurred',
    'outcome': 'failure',
    'tool': 'unknown',
    'summary': 'unknown_fail'
}
```

---

### 3. LEARNING

**Required:**
- `outcome`: `"learning"`
- `content`: What was learned
- `insight_type`: Type of learning (required)

```python
{
    'content': 'User prefers explicit error messages over generic ones',
    'outcome': 'learning',
    'insight_type': 'preference',  # REQUIRED: 'pattern', 'correction', 'preference', 'fact'
    'summary': 'explicit_errors_pref'
}
```

**insight_type values:**
- `'pattern'` - Observed patterns in code/behavior
- `'correction'` - Learned corrections to mistakes
- `'preference'` - User preferences discovered
- `'fact'` - Factual knowledge acquired

---

### 4. INTERACTION

**Required:**
- `outcome`: `"interaction"`
- `content`: User feedback or interaction
- `sentiment`: Emotional valence (required)

```python
{
    'content': 'User frustrated with repeated runtime errors',
    'outcome': 'interaction',
    'sentiment': 'negative',  # REQUIRED: 'positive', 'neutral', 'negative'
    'summary': 'user_frustrated'
}
```

**sentiment values:**
- `'positive'` - Positive user feedback
- `'neutral'` - Neutral observations
- `'negative'` - Negative feedback or frustration

---

## Python List Format for Bulk Generation

For generating vast datasets, use this format:

```python
memories = [
    # Successes
    {
        'content': 'Implemented JWT authentication with refresh tokens',
        'outcome': 'success',
        'tool': 'code_interpreter',
        'task_type': 'write',
        'summary': 'jwt_auth_impl'
    },
    {
        'content': 'Fixed race condition in payment processor',
        'outcome': 'success',
        'tool': 'code_interpreter',
        'task_type': 'debug',
        'summary': 'race_condition_fix'
    },
    {
        'content': 'Found best practices for database pooling',
        'outcome': 'success',
        'tool': 'web_search',
        'domain': 'technical',
        'summary': 'db_pool_research'
    },

    # Failures
    {
        'content': 'Syntax error - forgot to close bracket in comprehension',
        'outcome': 'failure',
        'tool': 'code_interpreter',
        'error_type': 'syntax',
        'summary': 'bracket_fail'
    },
    {
        'content': 'Logic error in refactor broke API contract',
        'outcome': 'failure',
        'tool': 'code_interpreter',
        'error_type': 'logic',
        'summary': 'refactor_break'
    },

    # Learnings
    {
        'content': 'Codebase uses factory pattern extensively',
        'outcome': 'learning',
        'insight_type': 'pattern',
        'summary': 'factory_pattern'
    },
    {
        'content': 'Learned to validate None before string operations',
        'outcome': 'learning',
        'insight_type': 'correction',
        'summary': 'none_validation'
    },

    # Interactions
    {
        'content': 'User praised the debugging explanations',
        'outcome': 'interaction',
        'sentiment': 'positive',
        'summary': 'user_happy'
    },
    {
        'content': 'User confused by complex architecture explanation',
        'outcome': 'interaction',
        'sentiment': 'negative',
        'summary': 'user_confused'
    },
]
```

---

## Storage Script Template

```python
from memory import MemoryEngine
import time

# Initialize memory engine
memory = MemoryEngine(root='agent_brain')

# Load your massive dataset
memories = [
    # ... your vast collection here ...
]

# Store all memories
print(f'Storing {len(memories)} memories...')
for i, mem in enumerate(memories, 1):
    path = memory.remember(**mem)
    if i % 100 == 0:
        print(f'  Stored {i}/{len(memories)}...')
    time.sleep(0.001)  # Ensure unique timestamps

print(f'\nComplete! {len(memories)} memories stored.')
```

---

## Dataset Generation Guidelines

### Scale Targets

**Small:** 50-100 memories (quick testing)
**Medium:** 500-1,000 memories (realistic single agent)
**Large:** 5,000-10,000 memories (multi-agent or long-running)
**Vast:** 50,000+ memories (stress testing, visualization)

### Realistic Distribution

For a balanced, realistic dataset:

```python
# Outcome distribution (target percentages)
success:     55-65%  # Healthy success rate
failure:     15-25%  # Learning from mistakes
learning:    10-15%  # Continuous improvement
interaction: 5-10%   # User feedback

# Tool distribution
code_interpreter: 40-50%  # Primary tool
web_search:       15-20%  # Research
file_operation:   10-15%  # File management
conversation:     5-10%   # Explanations

# Error type distribution (within failures)
runtime:  35-45%  # Most common
syntax:   20-30%  # Common
logic:    20-30%  # Common
timeout:  5-10%   # Less common

# Task type distribution (within code_interpreter successes)
debug:    35-45%  # Primary task
write:    25-35%  # New features
refactor: 15-25%  # Improvements
explain:  5-10%   # Documentation
```

### Content Realism

**Good content examples:**
```python
# Specific, actionable
'Fixed race condition in payment processor by adding mutex lock'
'Implemented OAuth2 authorization code flow with PKCE'
'Refactored database queries to use connection pooling'

# Describes the actual work
'TypeError when passing None to json.dumps() - needs validation'
'Learned that asyncio.gather() runs tasks concurrently, not sequentially'
'User prefers examples with inline comments over separate documentation'
```

**Avoid:**
```python
# Too generic
'Fixed a bug'
'Did some research'
'Learned something'

# Too vague
'Made improvements'
'Looked at code'
'Talked to user'
```

### Summary Guidelines

**Good summaries:**
```python
'jwt_auth_impl'           # Clear, descriptive
'race_condition_fix'      # Identifies the problem
'oauth2_pkce_flow'        # Technical but readable
'async_gather_insight'    # What was learned
```

**Keep summaries:**
- Under 50 characters
- Lowercase with underscores
- No spaces or special chars (except underscore, hyphen)
- Descriptive but concise

---

## Session Structuring (Optional)

For multi-session realism, group memories by time/theme:

```python
session_1_morning = [
    # Initial setup work
    # Feature implementations
    # First bugs encountered
]

session_2_afternoon = [
    # Deep debugging
    # More failures as complexity increases
    # Corrections learned
]

session_3_evening = [
    # Cleanup and refactoring
    # Documentation
    # User interactions
    # Reflections
]

all_memories = session_1_morning + session_2_afternoon + session_3_evening
```

---

## Validation Checklist

Before generating a vast dataset, ensure:

- [ ] All required fields present for each memory
- [ ] `outcome` is one of: success, failure, learning, interaction
- [ ] `tool` matches schema requirements
- [ ] Metadata keys match outcome/tool combination
- [ ] `summary` is filename-safe (no spaces, special chars)
- [ ] `content` is descriptive and realistic
- [ ] Distribution percentages are reasonable
- [ ] No duplicate summaries (will overwrite with same timestamp)

---

## Example: 100-Memory Dataset Template

```python
# Generate 100 memories with realistic distribution
memories = []

# 60 successes
for i in range(30):
    memories.append({
        'content': f'Successfully debugged issue #{1000+i}',
        'outcome': 'success',
        'tool': 'code_interpreter',
        'task_type': 'debug',
        'summary': f'debug_issue_{1000+i}'
    })

for i in range(20):
    memories.append({
        'content': f'Implemented feature #{i}',
        'outcome': 'success',
        'tool': 'code_interpreter',
        'task_type': 'write',
        'summary': f'feature_{i}_impl'
    })

for i in range(10):
    memories.append({
        'content': f'Found documentation on topic {i}',
        'outcome': 'success',
        'tool': 'web_search',
        'domain': 'technical',
        'summary': f'research_topic_{i}'
    })

# 20 failures
for i in range(10):
    memories.append({
        'content': f'Runtime error in module {i}',
        'outcome': 'failure',
        'tool': 'code_interpreter',
        'error_type': 'runtime',
        'summary': f'runtime_error_{i}'
    })

for i in range(10):
    memories.append({
        'content': f'Syntax error in function {i}',
        'outcome': 'failure',
        'tool': 'code_interpreter',
        'error_type': 'syntax',
        'summary': f'syntax_error_{i}'
    })

# 15 learnings
for i in range(15):
    memories.append({
        'content': f'Learned pattern #{i} in codebase',
        'outcome': 'learning',
        'insight_type': 'pattern',
        'summary': f'pattern_insight_{i}'
    })

# 5 interactions
for i in range(3):
    memories.append({
        'content': f'User happy with result #{i}',
        'outcome': 'interaction',
        'sentiment': 'positive',
        'summary': f'user_positive_{i}'
    })

for i in range(2):
    memories.append({
        'content': f'User confused by output #{i}',
        'outcome': 'interaction',
        'sentiment': 'negative',
        'summary': f'user_negative_{i}'
    })

# Total: 100 memories
```

---

## Output Format for Agent

**Copy this template and fill with your vast dataset:**

```python
memories = [
    # START OF DATASET

    # Add your memories here in the exact format specified above

    # END OF DATASET
]
```

Then pass to storage script:

```python
from memory import MemoryEngine
memory = MemoryEngine(root='agent_brain')
for mem in memories:
    memory.remember(**mem)
```

---

## Quick Reference Card

| Outcome | Required Tool | Required Metadata |
|---------|--------------|-------------------|
| success | code_interpreter | task_type: write/debug/refactor/explain |
| success | web_search | domain: technical/research/general |
| success | file_operation | (none) |
| success | conversation | (none) |
| failure | code_interpreter | error_type: syntax/runtime/logic/timeout |
| failure | web_search | reason: no_results/blocked/irrelevant |
| failure | file_operation | (none) |
| failure | unknown | (none) |
| learning | (none) | insight_type: pattern/correction/preference/fact |
| interaction | (none) | sentiment: positive/neutral/negative |

---

*This specification ensures all generated memories will route correctly through the BTB Coherence Engine and create a rich, analyzable topology.*
