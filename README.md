<img src="website/static/img/mobx-state-tree-logo-gradient.png" alt="logo" height="120" align="right" />

# Header

Some text or graphics

## Header 2

Intro text with a [link](https://www.google.com).

This text is **bold** and there's also *em* and _underline_.

👉 Icon? how do you do that?

Some code:

<code>*statement_name* *args*+ *tags*? *if_clause*?</code>

### Javascript:

```js
import { types } from "mobx-state-tree"

// Define a couple models
const Author = types.model({
    id: types.identifier,
    firstName: types.string,
    lastName: types.string
})
const Tweet = types.model({
    id: types.identifier,
    author: types.reference(Author), // stores just the `id` reference!
    body: types.string,
    timestamp: types.number
})

```

### Python:

```python
from typing import NamedTuple

def myfn(x: str) -> None:
    print(x)

```