---
sidebar_position: 2
---

# Program of Thought

!!! warning "This page is outdated and may not be fully accurate in DSPy 2.5"


## Background

DSPy supports the Program of Thought (PoT) prompting technique, integrating an advanced module capable of problem-solving with program execution capabilities. PoT builds upon Chain of Thought by translating reasoning steps into executable programming language statements through iterative refinement. This enhances the accuracy of the output and self-corrects errors within the generated code. Upon completing these iterations, PoT delegates execution to a program interpreter. Currently, this class supports the generation and execution of Python code.

## Instantiating Program of Thought 

Program of Thought is instantiated based on a user-defined DSPy Signature, which can take a simple form such as `input_fields -> output_fields`. Users can also specify a `max_iters` to set the maximum number of iterations for the self-refinement process of the generated code. The default value is 3 iterations. Once the maximum iterations are reached, PoT will produce the final output.

```python
import dsp
import dspy
from ..primitives.program import Module
from ..primitives.python_interpreter import PythonInterpreter
import re

class ProgramOfThought(Module):
    def __init__(self, signature, max_iters=3):
        ...
```

```python
#Example Usage

#Define a simple signature for basic question answering
generate_answer_signature = dspy.Signature("question -> answer")
generate_answer_signature.attach(question=("Question:", "")).attach(answer=("Answer:", "often between 1 and 5 words"))

# Pass signature to ProgramOfThought Module
pot = dspy.ProgramOfThought(generate_answer_signature)
```

## Under the Hood

Program of Thought operates in 3 key modes: generate, regenerate, and answer. Each mode is a Chain of Thought module encapsulating signatures and instructions for each mode's individual purpose. These are dynamically created as the PoT iterations complete, accounting for the user's input and output fields internally.

**Generate mode:**

Initiates the generation of Python code with the signature `(question -> generated_code)` for the initial code generation.

**Regenerate mode:**

Used for refining the generation of Python code, considering the previously generated code and existing errors, with the signature `(question, previous_code, error -> generated_code)`. If errors persist past the maximum iterations, the user is alerted and the output is returned as `None`.

**Answer mode:**

Executes the last stored generated code and outputs the final answer, with the signature `(question, final_generated_code, code_output -> answer)`.

**Key internals:**
- **Code Parsing:**
    Program of Thought internally processes each code generation as a string and filters out extraneous bits to ensure the code block conforms to executable Python syntax. If the code is empty or does not match these guidelines, the parser returns an error string, signaling the PoT process for regeneration.
- **Code Execution:**
    Program of Thought relies on a sandboxed environment Python interpreter using Deno and Pyodide adapted by [this tutorial](https://til.simonwillison.net/deno/pyodide-sandbox). This adaptation is present in [DSPy primitives](https://github.com/stanfordnlp/dspy/blob/main/dspy/primitives/python_interpreter.py).

## Tying It All Together
Using ProgramOfThought mirrors the simplicity of the base `Predict` and `ChainOfThought` modules. Here is an example call:

```python
#Call the ProgramOfThought module on a particular input
question = 'Sarah has 5 apples. She buys 7 more apples from the store. How many apples does Sarah have now?'
result = pot(question=question)

print(f"Question: {question}")
print(f"Final Predicted Answer (after ProgramOfThought process): {result.answer}")
```
```
Question: Sarah has 5 apples. She buys 7 more apples from the store. How many apples does Sarah have now?
Final Predicted Answer (after ProgramOfThought process): 12
```

Let's take a peek at how ProgramOfThought functioned internally by inspecting its history, up to maximum iterations (+ 1 to view the final generation). (This assumes the initial DSPy setup and configurations of LMs and RMs). 

`lm.inspect_history(n=4)`

```
You will be given `question` and you will respond with `generated_code`.
Generating executable Python code that programmatically computes the correct `generated_code`.
After you're done with the computation, make sure the last line in your code evaluates to the correct value for `generated_code`.

---

Follow the following format.

Question: 
Reasoning: Let's think step by step in order to ${produce the generated_code}. We ...
Code: python code that answers the question

---

Question: Sarah has 5 apples. She buys 7 more apples from the store. How many apples does Sarah have now?
Reasoning: Let's think step by step in order to produce the generated_code. We start with the initial number of apples that Sarah has, which is 5. Then, we add the number of apples she buys from the store, which is 7. Finally, we compute the total number of apples Sarah has by adding these two quantities together.
Code: 

apples_initial = 5
apples_bought = 7

total_apples = apples_initial + apples_bought
total_apples

Given the final code `question`, `final_generated_code`, `code_output`, provide the final `answer`.

---

Follow the following format.

Question: 

Code: python code that answers the question

Code Output: output of previously-generated python code

Reasoning: Let's think step by step in order to ${produce the answer}. We ...

Answer: often between 1 and 5 words

---

Question: Sarah has 5 apples. She buys 7 more apples from the store. How many apples does Sarah have now?

Code:
apples_initial = 5
apples_bought = 7

total_apples = apples_initial + apples_bought
total_apples

Code Output: 12

Reasoning: Let's think step by step in order to produce the answer. We start with the initial number of apples Sarah has, which is 5. Then, we add the number of apples she bought, which is 7. The total number of apples Sarah has now is 12.

Answer: 12

```
