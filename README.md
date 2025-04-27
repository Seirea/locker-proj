# locker-proj backend

OCSEFHacks project, a system for sharing items between a community

## Building/Developing

1. Clone repo

```sh
git clone https://github.com/Seirea/locker-proj
```

2. Setup virtual environment

```sh
python3 -m venv .venv
# on windows
.venv/Scripts/activate
# on *nix systems
. .venv/Scripts/activate.sh
```

3. install deps

```sh
pip3 install -r requirements.txt
pnpm i
```

4. Run CSS Compiler/Watcher

```sh
pnpm watch:css
```

5. Run (Dev Mode)

```sh
flask --app server run --debug --host=0.0.0.0
```

6.

## Firmware

Firmware can be found at <https://github.com/Seirea/locker-firmware>
