jConnect
====================
Check service on target

# Installation
- `$ git clone https://github.com/j3ssie/jConnect.git `
- `$ pip install pysmb`
- `$ cd jConnect/`
- `$ echo 'your_API_KEY' > SHODAN_API_KEY`
- `$ python jConnect.py`

# How to use
```$sudo python jConnect.py --target="14.171.21.132/24" --port="445" --write="test" ```
```$sudo python jConnect.py --raw_input="data.txt" --port="445" --write="data" ```

![jConnect screenshot](https://github.com/j3ssie/jConnect/blob/master/screenshots/1.png)
![jConnect screenshot](https://github.com/j3ssie/jConnect/blob/master/screenshots/2.png)

# Required
- Python 2.7
- Pip
- Shodan API key
- [Shodan](http://shodan.readthedocs.io/en/latest/index.html)
- [pysmb](https://pythonhosted.org/pysmb/api/smb_SMBConnection.html)
- [masscan](https://github.com/robertdavidgraham/masscan)

# Contact
- [j3ssiej.co.nf](http://j3ssiej.co.nf)
