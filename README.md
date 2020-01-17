# Data Obfuscator

Data Obfuscator is a simple **python3** tool to obfuscate data inside image-like files. It can obfuscate/deobfuscate files using the following
methods:

- `header`: The obfuscated data consists of a JPEG header followed by the original data. The result is not a valid image
- `append`: The obfuscated data consists of a blank JPEG image followed by the original data. The result is a valid 
image
- `lsb`: The data is obfuscated using Least Significant Byte (LSB) steganography using a blank image. The result is a 
valid image. 

The accepted parameters are the following:
```bash
$ python dataobfuscator.py -h
usage: dataobfuscator.py [-h] -i input [-m method] [-b bits] action

Data Obfuscator

positional arguments:
  action                Action to do (obfuscate or deobfuscate data)

optional arguments:
  -h, --help            show this help message and exit
  -i input, --input input
                        Input to be obfuscated
  -m method, --method method
                        Obfuscation/deobfuscation method. Valid options:
                        header, append, lsb, all (default)
  -b bits, --bits bits  Number of bits of obfuscated payload (only for LSB
                        deobfuscation)
```

## Examples

### Obfuscation
The following command will obfuscate `mimikatz.exe` in using all available methods (header, append and LSB).
```bash
$ python dataobfuscator.py -i examples/mimikatz/mimikatz.exe obfuscate
```

Alternatively, we can only obfuscate the payload using only one method using the `-m` argument, for instance:
```bash
$ python dataobfuscator.py -i examples/mimikatz/mimikatz.exe -m append obfuscate
```

### Deobfuscation

Deobfuscate `mimikatz.exe` obfuscated via the header method:
```bash
$ python dataobfuscator.py -i examples/mimikatz/mimikatz-header.jpg -m header deobfuscate
```

Deobfuscate `mimikatz.exe` obfuscated via the append method:
```bash
$ python dataobfuscator.py -i examples/mimikatz/mimikatz-append.jpg -m append deobfuscate
```

Deobfuscate `mimikatz.exe` obfuscated via the LSB method (note that we need to pass the number of bytes of the original 
Mimikatz binary):
```bash
$  python dataobfuscator.py -i examples/mimikatz/mimikatz-lsb.jpg -m lsb -b 7275776 deobfuscate
```