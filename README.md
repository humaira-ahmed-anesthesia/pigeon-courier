# WWII Pigeon Courier

**[Play it in your browser](https://humaira-ahmed-anesthesia.github.io/pigeon-courier/)**

A lane-dodging arcade game written in Python with Pygame. You fly a carrier pigeon through ten World War II missions, avoiding hawks and anti-aircraft fire. Each delivered message unlocks a short note about the real history behind it.

## How to play

Play it on a computer or a phone.

- **Computer:** left and right arrow keys (or A and D) change lanes. Dragging with the mouse works too.
- **Phone or tablet:** swipe left or right to change lanes. A long swipe crosses several lanes. Held upright, the game switches to a tall portrait layout that fits the phone: the same six lanes, more of each background visible, the pigeon about a third of the way up the screen, and big buttons. To force phone controls on any device, add `?mobile=1` to the address; add `?portrait=1` to preview the portrait layout on a computer.
- **Esc** or the pause button: open settings.
- Collect worms and medpacks to restore health, and coins to spend in The Coop.
- **Story Mode** has ten missions, from the V-2 rocket sites to the Dutch famine of 1944–45. **Endless Flight** gets harder the longer you survive.

Your progress saves automatically: missions completed, total coins and your best Endless Flight score. In the browser it's kept in that browser's storage; on desktop it's written to `save.json` next to the game.

## The history

During World War II, homing pigeons carried messages when radio was unsafe or out of range. Some, such as G.I. Joe and Paddy, received the Dickin Medal for animal bravery. That medal is the game's victory award.

## How it's built

- `main.py`: the whole game (about 1,600 lines of Python), structured as a state machine for the menus, gameplay, story messages and store.
- Pseudo-3D lanes: the six flight lanes narrow toward the horizon, and sprites move along them.
- Difficulty: hazard spawn rates and limits scale with the mission number, or with time survived in Endless Flight.
- Web version: packaged with [pygbag](https://github.com/pygame-web/pygbag), which runs Python and Pygame in the browser through WebAssembly. A GitHub Actions workflow rebuilds and republishes the game on every update.

## Run it locally

```bash
pip install pygame-ce
python main.py
```

## Author

Humaira Ahmed, BSN, RN. [Portfolio](https://humaira-ahmed-anesthesia.github.io/Electronic-Portfolio/)
