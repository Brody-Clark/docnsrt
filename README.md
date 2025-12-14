> [!NOTE]
> This project is a work in progress. As such, some features may be missing or incomplete

<h1 align="center">docnsrt</h1><h2 align="center"> Documentation Generation Framework</h2>

<p align="center">
Supported Languages:
  <em>
    Python, C#
  </em>
</p>

## Intro

docnsrt is a CLI-based multi-language source code docstring template insertion tool. It is designed to streamline the process of writing consistently formatted soure code documentation. Major docstring formats are supported out-of-the-box with the ability to also define custom formats.

### Example Usage

#### Original function (no docstring)

```py
# example_script.py
def calculate_rectangle_area(length, width, unit="meters"):
  if length < 0 or width < 0:
    raise ValueError("Length and width must be non-negative.")
  return length * width
```

#### Input

```bash
docnsrt --write --file example_script.py --function claculate_rectangle_area --style "PEP"
```

#### Output (with generated docstring)

```py
def calculate_rectangle_area(length, width, unit="meters"):
  # example_script.py
  """ __SUMMARY__

  Args:
    length: __DESC__
    width: __DESC__
    unit: __DESC__

  Returns:
    __RETURNS__

  Raises:
    __RAISES__

  """
  if length < 0 or width < 0:
    raise ValueError("Length and width must be non-negative.")
  return length * width
```

---

**[Documentation](docs/)**

[Install](docs/Install.md) ·
[Configuration](docs/Configuration.md)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
