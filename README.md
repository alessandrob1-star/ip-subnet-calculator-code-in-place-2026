# IP Subnet Calculator

**Final Project** for Stanford Code in Place 2026

## Author
**Alessandro Benevelli**

## Project Video
[Watch the demo on YouTube](https://youtu.be/5RuhGwCnxY8)

## Description
My version of a graphical IPv4 Subnet Calculator built with Python and Tkinter.

The goal of this project is to help users calculate subnet information, divide networks into smaller subnets, and better understand IPv4 subnetting concepts.

## Features
- Calculate detailed subnet information, including network address, broadcast address, subnet mask, IP class, total IP addresses, usable hosts, and host range
- Divide a network into multiple subnets
- Automatic CIDR prefix detection when the user enters an address without slash notation
- AI Chatbot tab for questions about IPv4, CIDR, subnet masks, network IDs, broadcast addresses, and usable hosts
- Optional online AI API support through an `OPENAI_API_KEY` environment variable
- Offline chatbot fallback for reliable demos without internet
- Support for Class A, B, C, D, E, and loopback addresses

## Technologies Used
- Python 3
- Tkinter for the graphical user interface
- `ipaddress` module for IPv4 network calculations
- `threading` for chatbot responsiveness
- Optional online API connection using Python's standard library

## How to Run
```bash
python main.py
```
