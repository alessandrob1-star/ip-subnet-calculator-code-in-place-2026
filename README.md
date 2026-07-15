# IP Subnet Calculator

[![Python tests](https://github.com/alessandrob1-star/ip-subnet-calculator-code-in-place-2026/actions/workflows/python-tests.yml/badge.svg?branch=main)](https://github.com/alessandrob1-star/ip-subnet-calculator-code-in-place-2026/actions/workflows/python-tests.yml)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A graphical IPv4 subnet calculator and learning tool built with Python and Tkinter. This was created as the final project for Stanford Code in Place 2026.

## Highlights

- Calculate network address, broadcast address, subnet mask, address scope, IP class, usable hosts, and host range.
- Divide an IPv4 network into equal-size subnets.
- Support RFC 3021 `/31` point-to-point networks and `/32` single-host routes.
- Identify RFC 1918, globally routable, CGNAT, TEST-NET, loopback, link-local, multicast, and reserved address scopes.
- Ask IPv4 and subnetting questions through the built-in offline tutor.
- Optionally use the OpenAI API for online tutor answers.
- Keep the interface responsive while online requests run in background threads.
- Run without third-party runtime dependencies.

## Requirements

- Python 3.10 or newer
- Tkinter

Tkinter is included with standard Python installations on Windows and macOS. Some Linux distributions provide it as a separate package, commonly named `python3-tk`.

## Quick start

```bash
git clone https://github.com/alessandrob1-star/ip-subnet-calculator-code-in-place-2026.git
cd ip-subnet-calculator-code-in-place-2026
python main.py
```

The application opens three tabs:

1. **Calculate Subnet** — inspect one IPv4 network.
2. **Subnetting** — divide a network into equal-size subnets.
3. **AI Chatbot** — ask the online AI or offline tutor about IPv4 concepts.

## CIDR behavior

CIDR notation is recommended whenever the intended network range matters:

```text
192.168.1.25/24 -> 192.168.1.0/24
```

When no prefix is supplied, the calculator infers one from trailing zero octets:

```text
10.0.0.0     -> /8
172.16.0.0   -> /16
192.168.1.0  -> /24
192.168.1.25 -> /32
```

Therefore, enter an explicit CIDR prefix when using a host address to represent a larger network.

## Optional online tutor

The chatbot works offline by default. To enable online answers, set `OPENAI_API_KEY` before starting the application.

PowerShell:

```powershell
$env:OPENAI_API_KEY="your-api-key"
python main.py
```

macOS or Linux:

```bash
export OPENAI_API_KEY="your-api-key"
python main.py
```

Online questions are sent to the OpenAI API using your configured key. Every answer is labeled as either `Online AI` or `Offline tutor`; API failures fall back to the offline tutor with a visible reason.

## Testing

Run the complete test suite:

```bash
python -m unittest discover -s tests -v
```

Check that the application compiles:

```bash
python -m py_compile main.py
```

GitHub Actions runs both commands automatically on Python 3.10 and 3.13 for every pull request and push to `main`.

## Project structure

```text
.
|-- main.py                         # Application, GUI, and IPv4 logic
|-- tests/                          # Unit and regression tests
|-- .github/workflows/python-tests.yml
|-- certificates/                   # Code in Place certificate
|-- LICENSE
`-- README.md
```

## Scope and limits

- The application intentionally supports IPv4 only.
- Equal-size subnet counts must be powers of two.
- The GUI displays at most 1,024 subnets per operation to remain responsive.
- The offline tutor is deterministic and focused on common IPv4 concepts; it is not presented as a model-generated answer.

## Project links

- [Video demonstration](https://youtu.be/5RuhGwCnxY8)
- [Code in Place certificate](certificates/code-in-place-certificate.pdf)
- [Author's GitHub profile](https://github.com/alessandrob1-star)
- [Author's LinkedIn profile](https://www.linkedin.com/in/alessandrobenevelliopit/)

## License

Released under the [MIT License](LICENSE).
