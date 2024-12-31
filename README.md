# TurtleThread
TurtleThread is a Python library inspired by [TurtleStitch](https://www.turtlestitch.org/). The goal of TurtleThread is to provide an easy-to-use turtle based interface to making embroidery patterns and learn about Python programming and art. To accomplish this, we use the excellent [PyEmbroidery](https://github.com/EmbroidePy/pyembroidery) library, which implements all the embroidery specific logic (e.g. exporting the patterns as embroidery files).

## Lisense
The code is licensed under a GPLv3 license, which means that you can use it for anything you'd like. However, if you use it to make your own tools, your tool must be open source and licensed with the GPLv3 license. For more information, see this [guide](https://www.gnu.org/licenses/quick-guide-gplv3.en.html).

## Development
This is a fork of TurtleThread by AppVenture, NUS High's Computer Science Interest Group. The three contributors from AppVenture are Wong Yue Heng, Tan Junheng, and Yu Simu. A majority of TurtleThread was developed by Marie Roald and Yngve Mardal Moe.  

TurtleThread is still under development, so we appreciate any issues about eventual bugs you may encounter. We are also happy for community contributions, so if you want to add some functionality, then we encourage you to describe it in an issue and submit a pull request with the feature.  

## Installation
As this is a fork of TurtleThread, it must be installed via the following command, and **NOT** from PyPI.

```bash
pip install git+https://github.com/appventure-nush/TurtleThread
``` 

## Example 
```python
from turtlethread import Turtle

pen = Turtle()
with pen.running_stitch(stitch_length=20):
    for side in range(4):
        pen.forward(80)
        pen.right(90)

with pen.jump_stitch():
    pen.forward(160)

with pen.running_stitch(stitch_length=20):
    for side in range(3):
        pen.forward(80)
        pen.right(120)

pen.save("pattern.png")
pen.save("pattern.exp")
```

