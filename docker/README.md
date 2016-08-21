# Docker continer for java9 notebook
This is a proof of concept of docker container for java9 notebook.

### It is not production ready. Although it is fully functional by the time this file is written
It just brings a lot of not relevant stuff inherited from "jupyter/base-notebook".

### Make sure to use build-image script in order to create docker image.
"docker build" will fail because of the relative path to javakernel folder

### To build docker image
from docker directory run

```
sudo ./build-image
```
and to re-create docker container listening on port 18888

```
sudo ./recreate-container
```
