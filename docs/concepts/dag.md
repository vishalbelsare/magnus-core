# Dag

Dag or directed acyclic graphs are a way to define your work flows. Its a graph representation of the series of
tasks you want to perform and the order of it.

In magnus, a lot of design emphasis was on making sure that a dag once defined should not change for
deployment purposes. The dag is also version controlled and as part of your code repositories to promote good
software engineering practices. These design decisions should enable experimentation to happen in
*interactive* modes while engineering teams can use their preferred **Continuos Integration** tools to
operationalize experiments once they are mature without changing code or the dag.

We see the dag as a **contract** between the engineering teams and data science teams. While the data science teams
can focus on **what** should be the part of the pipeline, the engineering teams can focus on the
**how** to operationalize it.

The configuration of a dag:
```yaml
dag:
  start_at:
  name: # optional
  description: #optional
  max_time: # Optional
  steps:
```

### description (optional)

A short description of the dag

### max_time (optional)

The maximum compute time that this dag could run in seconds.

---
!!! Note

    Maximum run time is just a definition in the dag and the actual implementation depends upon the mode of execution.

    For example, interactive modes can completely ignore the maximum run time.

    Orchestration modes might have a default if one is not provided. For example: AWS step functions defaults maximum run time for a a state machine to be 86400 seconds.
---

### start_at

The node/step in the steps to start the traversal of the graph.
A node of this name should be present in the steps.

### steps

A mapping of steps with each step belonging to one of the [defined types](nodes.md).

## Example
Assuming this is in dag-concepts.yaml
```yaml
# in dag-concepts.yaml
dag:
  start_at: Hello
  steps:
    Hello:
      type: task
      command: my_module.say_hello
      next: Success
    Success:
      type: success
    Fail:
      type: fail
```

or via the Python SDK:

```python
# in pipeline.py
from magnus import Task, Pipeline

def pipeline():
    first = Task(name='Hello', command='my_module.say_hello')
    pipeline = Pipeline(start_at=first, name='dag-concepts')
    pipeline.construct([first])

    pipeline.execute()

if __name__ == '__main__':
    pipeline()
```

And the following code in my_module.py
```python
# in my_module.py

def say_hello(name=world):
    print(f'Hello {name}')
```

We can execute the dag by:
```shell
export MAGNUS_PRM_name=universe
magnus execute --file dag-concepts.yaml
```

or via the Python SDK:
```
python pipeline.py
```

You should be able to see ```Hello universe``` in the logs.

## Parameterized Definition

Magnus allows dag definitions to be parameterized by using placeholders. We use [python String templates](https://docs.python.org/3.7/library/string.html#template-strings) to enable parameter substitution. As we use, [safe_substitution](https://docs.python.org/3.7/library/string.html#string.Template.safe_substitute) it means that we silently ignore any parameter that is not found.
You should make sure that the parameters are properly defined.

### Example of variables
Assuming this is in dag-variable.yaml
```yaml
dag:
  start_at: Hello
  steps:
    Hello:
      type: task
      command: ${module_name}
      next: Success
    Success:
      type: success
    Fail:
      type: fail
```

Magnus variables can be defined by environmental variables, any string with a prefix ```MAGNUS_VAR_``` is considered a
variable.

```shell
export MAGNUS_VAR_module_name=my_module.say_hello
```
and with the same python code [as before](#example), we can achieve the same result by:
```shell
magnus execute --file dag-variable.yaml --name universe
```

Magnus would resolve the placeholders at the load of the dag definition.

The variables are also applied on the configuration file.

### Design thought behind variables

Variables are a great way to have a generalized definition of the dag and the config parameters, especially if that
value is not known before hand.

For example: consider a containerized execution of the pipeline. The container tag to run might be only known after
building the container and this can be supplied dynamically at run time.
