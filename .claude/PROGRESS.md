# Progress Notes

## 2026-03-01: Graph Panel UI Interaction Bugs

Three interaction bugs were fixed in `theme/graph.js`, all related to how Cytoscape.js handles DOM events and user interaction state.

---

### Bug 1: Slider click-through

**Problem:** The core concept slider (range input) could not be dragged. Clicking to select a value worked, but sliding did not — the drag gesture was intercepted by Cytoscape.js for graph panning.

**Root cause:** Cytoscape.js binds event listeners at the **window level**, not just on its container. Only `mousedown` was being stopped via `stopPropagation`, but Cytoscape also listens to `pointerdown`, `pointermove`, `touchstart`, and `touchmove`. During a slider drag, these pointer/touch move events propagated to Cytoscape, which interpreted them as pan gestures.

**Fix:** Stop propagation on all relevant event types on the slider container:
```js
['mousedown', 'pointerdown', 'touchstart',
 'mousemove', 'pointermove', 'touchmove'].forEach(function(evt) {
    sliderContainer.addEventListener(evt, function(e) {
        e.stopPropagation();
    });
});
```

**Lesson:** When overlaying interactive HTML elements on a Cytoscape.js canvas, stopping `mousedown` alone is insufficient. Cytoscape uses pointer events and touch events at the window level. All of `mousedown`, `pointerdown`, `touchstart`, `mousemove`, `pointermove`, `touchmove` must have propagation stopped on the overlay element.

---

### Bug 2: First click on a node shows animation instead of opening card

**Problem:** Clicking a graph node for the first time showed a strange animation (node flying from center to its position) without opening the concept card. The second click worked normally.

**Root cause:** Two issues combined:

1. **Nodes were grabbable** (`grabbable: true`, the Cytoscape.js default). With real mouse clicks, even sub-pixel mouse movement between `mousedown` and `mouseup` turns a click into a **drag** operation. On drag, the node follows the cursor, and the `tap` event never fires — so the card creation handler is skipped. The second, more careful click registers as a proper tap.

2. **Preset layout had `animate: true`** with 500ms duration. Every time the layered layout ran (initial load, slider change, layout toggle), all nodes animated from position (0,0) to their computed positions, creating a "fly from center" visual.

**Fix:**
- Set `autoungrabify: true` on the Cytoscape instance to prevent nodes from being dragged. Nodes in this graph are not meant to be repositioned by the user.
- Set `animate: false` on the preset layout so nodes appear at their positions instantly.

**Lesson:** If graph nodes are not meant to be user-draggable, always set `autoungrabify: true`. The default `grabbable: true` causes subtle issues where clicks with tiny mouse movement become drags instead of taps, making the UI feel broken. Also, animated preset layouts that place nodes at (0,0) first and then animate to target positions create visual noise — only use animation when there's a meaningful transition from one known state to another.

---

### Bug 3: Closing cards via X button disables graph panning

**Problem:** After closing all concept cards one-by-one using their X (close) buttons, the graph entered a "select mode" where panning/dragging was disabled. Clicking another node and then using the "Close All Documents" button restored normal behavior.

**Root cause:** Each card disables `cy.userPanningEnabled` and `cy.userZoomingEnabled` on `mouseenter`, and re-enables them on `mouseleave`. When the X button is clicked, `card.remove()` destroys the DOM element. Since the element no longer exists, the **`mouseleave` event never fires**, leaving panning and zooming permanently disabled.

The "Close All Documents" button didn't have this problem because clicking another node first caused the mouse to leave the card (triggering `mouseleave` and re-enabling panning), and the button's own `mouseleave` handler fired when the button was hidden.

**Fix:** Explicitly re-enable panning and zooming after removing a card:
```js
card.remove();
updateCloseAllBtn();
cy.userZoomingEnabled(true);
cy.userPanningEnabled(true);
```

**Lesson:** When toggling state on `mouseenter`/`mouseleave` (or any paired events), always consider what happens if the element is **removed from the DOM** while the mouse is over it. DOM removal does not reliably fire `mouseleave`. Any cleanup that `mouseleave` would do must also be done at the point of removal. This is a common pattern with:
- Tooltips/popovers that are removed programmatically
- Cards/panels with close buttons
- Any element that disables external behavior on hover

A defensive pattern is to always restore state at the removal site rather than relying solely on `mouseleave`.
