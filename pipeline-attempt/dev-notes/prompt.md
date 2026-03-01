### **Project Context: Forester Knowledge Graph Visualization**

**Goal:** Create an interactive, hierarchical graph visualization for a Zettelkasten-style knowledge base using Cytoscape.js.

**Key Features Implemented:**

1. **3-Card FIFO Stack:**
* Clicking a node opens a Detail Card on the right.
* Max 3 cards. Newest card pushes out the oldest.
* Re-clicking an open node moves it to the newest position (bottom).
* **Content:** Fetches XML, parses it, serializes text (handling lists/math/HTML tags), and ignores transclusions (`fr:tree`).


2. **Custom Sugiyama Layout (Hierarchical):**
* **BFS Layering:** Assigns ranks based on distance from the root.
* **Polyline Edges:** Edges spanning multiple ranks are split into segments using **invisible dummy nodes**.
* **Ordering:** Uses a Barycenter heuristic to minimize edge crossings.
* **Coordinates:** nodes are placed on a strict grid (`preset` layout).


3. **Advanced Interaction:**
* **Smart Centering:** Centers the node in the *visible* canvas space (accounting for the width of the open card stack).
* **Event Isolation:** `cy.userZoomingEnabled(false)` triggers when hovering over cards to prevent scroll bleed-through.
* **Chain Highlighting:** Clicking a node highlights the *entire* polyline chain (Source  Dummy...  Target) using a custom traversal helper.
* **Labels:** Semantic relation text appears **only** on the middle segment of the polyline to avoid clutter.
* **Shortcuts:** "Close All" button (bottom center) and `Esc` key support.

---

### **Current Codebase**

#### **1. CSS (`theme/style.css`)**

```css
/* SPDX-License-Identifier: CC0-1.0 */

.katex {
 font-size: 1.15em !important;
}

/* inria-sans-300 - latin_latin-ext */
@font-face {
  font-display: swap;
  /* Check https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face/font-display for other options. */
  font-family: 'Inria Sans';
  font-style: normal;
  font-weight: 300;
  src: url('fonts/inria-sans-v14-latin_latin-ext-300.woff2') format('woff2');
  /* Chrome 36+, Opera 23+, Firefox 39+, Safari 12+, iOS 10+ */
}

/* inria-sans-300italic - latin_latin-ext */
@font-face {
  font-display: swap;
  /* Check https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face/font-display for other options. */
  font-family: 'Inria Sans';
  font-style: italic;
  font-weight: 300;
  src: url('fonts/inria-sans-v14-latin_latin-ext-300italic.woff2') format('woff2');
  /* Chrome 36+, Opera 23+, Firefox 39+, Safari 12+, iOS 10+ */
}

/* inria-sans-regular - latin_latin-ext */
@font-face {
  font-display: swap;
  /* Check https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face/font-display for other options. */
  font-family: 'Inria Sans';
  font-style: normal;
  font-weight: 400;
  src: url('fonts/inria-sans-v14-latin_latin-ext-regular.woff2') format('woff2');
  /* Chrome 36+, Opera 23+, Firefox 39+, Safari 12+, iOS 10+ */
}

/* inria-sans-italic - latin_latin-ext */
@font-face {
  font-display: swap;
  /* Check https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face/font-display for other options. */
  font-family: 'Inria Sans';
  font-style: italic;
  font-weight: 400;
  src: url('fonts/inria-sans-v14-latin_latin-ext-italic.woff2') format('woff2');
  /* Chrome 36+, Opera 23+, Firefox 39+, Safari 12+, iOS 10+ */
}

/* inria-sans-700 - latin_latin-ext */
@font-face {
  font-display: swap;
  /* Check https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face/font-display for other options. */
  font-family: 'Inria Sans';
  font-style: normal;
  font-weight: 700;
  src: url('fonts/inria-sans-v14-latin_latin-ext-700.woff2') format('woff2');
  /* Chrome 36+, Opera 23+, Firefox 39+, Safari 12+, iOS 10+ */
}

/* inria-sans-700italic - latin_latin-ext */
@font-face {
  font-display: swap;
  /* Check https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face/font-display for other options. */
  font-family: 'Inria Sans';
  font-style: italic;
  font-weight: 700;
  src: url('fonts/inria-sans-v14-latin_latin-ext-700italic.woff2') format('woff2');
  /* Chrome 36+, Opera 23+, Firefox 39+, Safari 12+, iOS 10+ */
}

:root {
  --content-gap: 15px;
  --radius: 5px;
}

h1,
h2,
h3,
h4,
h5,
h6 {
  line-height: 1.2;
  margin-bottom: 0;
}

h5,
h6,
p {
  margin-top: 0;
}

h1,
h2,
h3,
h4 {
  margin-top: .5em;
}

pre,
img,
.katex-display,
section,
center {
  overflow-y: hidden;
}

pre {
  border-radius: var(--radius);
  background-color: rgba(0, 100, 100, 0.04);
  padding: .5em;
  font-size: 11pt;
  margin-top: 0em;
  overflow-x: auto;
  white-space: pre-wrap;
  white-space: -moz-pre-wrap;
  white-space: -pre-wrap;
  white-space: -o-pre-wrap;
  word-wrap: break-word;
}

code {
  border-radius: var(--radius);
  background-color: rgba(0, 100, 100, 0.04);
  padding: 0.2em;
  font-size: 0.9em;
}

body {
  font-family: "Inria Sans";
  font-size: 12pt;
  line-height: 1.55;
}

math {
 font-size: 1.12em;
}

mrow:hover {
 background-color: rgba(0, 100, 255, 0.04);
}

.logo {
  font-weight: 1000;
  font-size: 24px;
}

.logo a {
  color: #666;
  text-decoration: none;
}

.logo a:hover {
  color: #aaa;
}

.block.hide-metadata>details>summary>header>.metadata {
  display: none;
}

article>section>details>summary>header>h1>.taxon {
  display: block;
  font-size: .9em;
  color: #888;
  padding-bottom: 5pt;
}

section section[data-taxon="Reference"]>details>summary>header>h1>.taxon,
section section[data-taxon="Person"]>details>summary>header>h1>.taxon {
  display: none;
}

footer>section {
  margin-bottom: 1em;
}

footer h2 {
  font-size: 14pt;
}

.metadata>address {
  display: inline;
}

@media only screen and (max-width: 1000px) {
  body {
    margin-top: 1em;
    margin-left: .5em;
    margin-right: .5em;
    transition: ease all .2s;
  }

  /* Hide the floating TOC on mobile screens */
  #grid-wrapper>details.floating-toc {
    display: none;
    transition: ease all .2s;
  }
}

@media only screen and (min-width: 1000px) {
  body {
    margin-top: 2em;
    margin-left: 2em;
    transition: ease all .2s;
  }

  #grid-wrapper {
    display: grid;
    grid-template-columns: 90ex 1fr; /* Revert to single column */
    column-gap: 2em;
    min-height: 90vh;
  }
}

#grid-wrapper>article {
  grid-column: 1;
}

/* Graph Panel Styling with Light Yellow Grid Paper */
#graph-panel {
  grid-column: 2;
  grid-row: 1 / span 2;
  border-radius: var(--radius);
  border: 1px solid #ccc;
  background-color: #ffffe0; 
  background-image: 
    repeating-linear-gradient(transparent, transparent 19px, #e5e5c3 19px, #e5e5c3 20px),
    repeating-linear-gradient(90deg, transparent, transparent 19px, #e5e5c3 19px, #e5e5c3 20px);
  
  /* Make the panel stay in view while scrolling the document */
  position: sticky;
  top: 2em;
  align-self: start; /* Critical: stops the element from stretching to the article's full height */
  height: calc(100vh - 4em);
  overflow: hidden;
}

#grid-wrapper>header {
  grid-column: 1;
  margin-bottom: 0.5em;
}

#grid-wrapper>article {
  max-width: 90ex;
  margin-right: auto;
  grid-column: 1; /* Place article in the single column */
}

/* Floating TOC Styles */
details.floating-toc {
  position: fixed;
  top: 2em;
  left: 0; /* Anchored flush to the left edge */
  z-index: 1000;
}

summary.toc-toggle {
  cursor: pointer;
  background-color: white;
  border: 1px solid #ccc;
  border-left: none; /* Remove left border so it connects to the screen edge */
  
  /* Make it a square */
  width: 40px;
  height: 40px;
  
  /* Center the icon */
  display: flex;
  align-items: center;
  justify-content: center;
  
  /* Round only the right corners to look like a tab */
  border-radius: 0 var(--radius) var(--radius) 0;
  box-shadow: 2px 2px 4px rgba(0,0,0,0.1);
  font-size: 1.2em;
  font-weight: bold;
  list-style-type: none;

  transform: translateX(-50%);
  transition: transform 0.2s ease-out, background-color 0.2s ease;
}

summary.toc-toggle::-webkit-details-marker {
  display: none;
}

summary.toc-toggle:hover {
  /* Changed from transparent rgba to a solid, opaque light-blue */
  background-color: #e6f2ff;
  transform: translateX(0);
}

details.floating-toc nav#toc {
  margin-top: 5pt;
  margin-left: 10pt; /* Push the menu slightly off the edge */
  background-color: white;
  border: 1px solid #ccc;
  padding: 15pt;
  border-radius: var(--radius);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  max-height: 80vh;
  width: 300px;
  overflow-y: auto;
}

details>summary>header {
  display: inline;
}

a.heading-link {
  box-shadow: none;
}

details h1 {
  font-size: 13pt;
  display: inline;
}

section .block[data-taxon] details>summary>header>h1 {
  font-size: 12pt;
}

span.taxon {
  color: #444;
  font-weight: bolder;
}


.link-list>section>details>summary>header h1 {
  font-size: 12pt;
}


article>section>details>summary>header>h1 {
  font-size: 1.5em;
}

details>summary {
  list-style-type: none;
}

details>summary::marker,
details>summary::-webkit-details-marker {
  display: none;
}

article>section>details>summary>header {
  display: block;
  margin-bottom: .5em;
}

section.block>details {
  margin-bottom: 0.4em;
}


section.block>details[open] {
  margin-bottom: 1em;
}


.link-list>section.block>details {
  margin-bottom: .25em;
}

nav#toc {
  margin-left: 1em;
}

nav#toc h1 {
  margin-top: 0;
  font-size: 16pt;
}

nav#toc,
nav#toc a {
  color: #555;
}

nav#toc .link {
 box-shadow: none;
 text-decoration: none;
}

nav#toc a.bullet {
 opacity: 0.7;
 margin-left: 0.4em;
 margin-right: 0.3em;
 padding-left: 0.2em;
 padding-right: 0.2em;
 text-decoration: none;
}

nav#toc h2 {
  font-size: 1.1em;
}

nav#toc ul {
  list-style-type: none;
}

nav#toc li > ul {
 padding-left: 1em;
}

nav#toc li {
 list-style-position: inside;
}

.block {
  border-radius: var(--radius)
}

.block:hover {
  background-color: rgba(0, 100, 255, 0.04);
}

.block.highlighted {
  border-style: solid;
  border-width: 1pt;
}

.highlighted {
  background-color: rgba(255, 255, 140, .3);
  border-color: #ccc;
}

.highlighted:hover {
  background-color: rgba(255, 255, 140, .6);
  border-color: #aaa;
}

.slug,
.doi,
.orcid {
  color: gray;
  font-weight: 200;
}

.edit-button {
  color: rgb(180, 180, 180);
  font-weight: 200;
}

.block {
  padding-left: 5px;
  padding-right: 10px;
  padding-bottom: 2px;
  border-radius: 5px;
}

.link.external {
  text-decoration: underline;
}

a.link.local,
.link.local a,
a.slug {
  box-shadow: none;
  text-decoration-line: underline;
  text-decoration-style: dotted;
 }

ninja-keys::part(ninja-action) {
  white-space: nowrap;
}

body {
  hyphens: auto;
}

table {
  margin-bottom: 1em;
}

table.macros {
  overflow-x: visible;
  overflow-y: visible;
  font-size: 0.9em;
}

table.macros td {
  padding-left: 5pt;
  padding-right: 15pt;
  vertical-align: baseline;
}

th {
  text-align: left;
}

th,
td {
  padding: 0 15px;
  vertical-align: top;
}

td.macro-name,
td.macro-body {
  white-space: nowrap;
}

td.macro-doc {
  font-size: .9em;
}

.enclosing.macro-scope>.enclosing {
  border-radius: 2px;
}

.enclosing.macro-scope>.enclosing:hover {
  background-color: rgba(0, 100, 255, 0.1);
}

[aria-label][role~="tooltip"]::after {
  font-family: "Inria Sans";
}

.tooltip {
  position: relative;
}

.inline.tooltip {
  display: inline-block;
}

.display.tooltip {
  display: block;
}


/* The tooltip class is applied to the span element that is the tooltip */

.tooltip .tooltiptext {
  visibility: hidden;
  white-space: nowrap;
  min-width: fit-content;
  background-color: black;
  color: #fff;
  padding-left: 5px;
  padding-top: 5px;
  padding-right: 10px;
  border-radius: 6px;
  position: absolute;
  z-index: 1;
  top: 100%;
  left: 50%;
  margin-left: -60px;
  opacity: 0;
  transition: opacity 0.3s;
}

.tooltip .tooltiptext::after {
  content: "";
  position: absolute;
  top: 100%;
  left: 50%;
  margin-left: -5px;
  border-width: 5px;
}


/* Show the tooltip */

.tooltip:hover .tooltiptext {
  visibility: visible;
  opacity: 1;
}

.tooltiptext a {
  color: white
}

.macro-doc {
  font-style: italic;
}

.macro-name {
  white-space: nowrap;
}

.macro-is-private {
  color: var(--secondary);
}

blockquote {
  border-inline-start: 1px solid var(--secondary);
}

a.slug:hover,
a.bullet:hover,
.edit-button:hover,
.link:hover {
  background-color: rgba(0, 100, 255, .1);
}

.link {
 cursor: pointer;
}

a {
  color: black;
  text-decoration: inherit;
}

.nowrap {
  white-space: nowrap;
}

.nocite {
  display: none
}

blockquote {
  font-style: italic;
}



address {
  display: inline;
}


.metadata ul {
  padding-left: 0;
  display: inline;
}

.metadata li::after {
  content: " · ";
}

.metadata li:last-child::after {
  content: "";
}

.metadata ul li {
  display: inline
}

img {
  object-fit: cover;
  max-width: 100%;
}

figure {
  text-align: center;
}

figcaption {
  font-style: italic;
  padding: 3px;
}

mark {
  background-color: rgb(255, 255, 151);
}

hr {
  margin-top: 10px;
  margin-bottom: 20px;
  background-color: gainsboro;
  border: 0 none;
  width: 100%;
  height: 2px;
}

ul, ol {
 padding-bottom: .5em;
}

ol {
 list-style-type: decimal;
}

ol li ol {
 list-style-type: lower-alpha;
}

ol li ol li ol {
 list-style-type: lower-roman;
}

.error, .info {
  border-radius: 4pt;
  padding-left: 3pt;
  padding-right: 3pt;
  padding-top: 1pt;
  padding-bottom: 2pt;
  font-weight: bold;
}

.error {
 background-color: red;
 color: white;
}


.info {
 background-color: #bbb;
 color: white;
}

/* Graph Card Stack Container */
#graph-card-stack {
  position: absolute;
  top: 20px;
  bottom: 20px;
  right: 20px;
  width: 350px; /* Wider card as requested */
  display: flex;
  flex-direction: column;
  gap: 15px;
  z-index: 100;
  pointer-events: none; /* Let clicks pass through empty spaces to the canvas */
}

/* Individual Graph Card */
.graph-card {
  display: flex;
  flex-direction: column;
  flex: 1; /* Auto-divide available vertical space equally */
  min-height: 0; /* Critical for Flexbox scrolling */
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid #ccc;
  border-radius: var(--radius);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  pointer-events: auto; /* Re-enable clicks on the card itself */
  font-size: 0.9em;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  border-bottom: 1px solid #eee;
  flex-shrink: 0; /* Freeze title */
  background: #fff;
}

.card-header h3 {
  margin: 0;
  font-size: 1.1em;
}

.close-card {
  background: none;
  border: none;
  font-size: 1.5em;
  line-height: 1;
  cursor: pointer;
  color: #888;
}

.close-card:hover {
  color: #e74c3c;
}

.card-body {
  padding: 15px;
  overflow-y: auto; /* Scrollable content */
  flex-grow: 1;
}

.card-body p {
  margin-top: 0;
  color: #333;
}

.card-footer {
  padding: 10px 15px;
  border-top: 1px solid #eee;
  flex-shrink: 0; /* Freeze footer */
  background: #fafafa;
}

.card-footer a {
  font-size: 0.9em;
  color: #0064ff;
  text-decoration: none;
}

/* Close All Cards Button */
#close-all-cards {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 8px 16px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
  z-index: 101;
  display: none; /* Hidden by default */
  font-size: 0.9em;
  font-weight: bold;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

#close-all-cards:hover {
  background: #c0392b;
}

```

#### **2. JavaScript (`theme/graph.js`)**

```JavaScript
// Helper function to robustly extract the Tree ID from any Forester URL or path
function extractIdFromPath(path) {
    if (!path) return '';
    
    // Remove hash and query parameters
    const cleanPath = path.split('#')[0].split('?')[0];
    
    // Split by slash and remove any empty strings (handles trailing slashes)
    const segments = cleanPath.split('/').filter(Boolean);
    if (segments.length === 0) return '';
    
    let lastSegment = segments[segments.length - 1];
    
    // If the last segment is the index file, the ID is the parent directory
    if (lastSegment === 'index.html' || lastSegment === 'index.xml') {
        if (segments.length > 1) {
            return segments[segments.length - 2];
        } else {
            return '';
        }
    }
    
    // Otherwise, the ID is the last segment (remove .html if present)
    return lastSegment.replace(/\.html$/, '');
}

document.addEventListener('DOMContentLoaded', () => {
    const graphContainer = document.getElementById('graph-panel');
    if (!graphContainer) return;

    const baseUrl = document.documentElement.getAttribute('data-base-url') || './';

    // 1. Use the new helper to extract the current page ID
    const currentTreeId = extractIdFromPath(window.location.pathname);

    fetch(baseUrl + 'graph.json')
        .then(response => {
            if (!response.ok) throw new Error("Could not load graph.json");
            return response.json();
        })
        .then(data => {
            initGraph(data.edges, data.nodes, currentTreeId, graphContainer, baseUrl);
        })
        .catch(error => {
            console.warn("Graph initialization failed:", error);
            graphContainer.innerHTML = "<p style='padding: 1rem; color: #888;'>Graph data not available.</p>";
        });
});

function initGraph(allEdges, allNodesDict, currentId, container, baseUrl) {
    allNodesDict = allNodesDict || {};

    const isNodeInGraph = allEdges.some(edge => edge.source === currentId || edge.target === currentId);
    let filteredEdges = [];
    let highlightNodeId = null;

    if (isNodeInGraph) {
        console.log(`[Graph] State 2: Modular Learning for ${currentId}`);
        filteredEdges = allEdges.filter(edge => edge.source === currentId || edge.target === currentId);
        highlightNodeId = currentId;
    } else {
        console.log(`[Graph] State 1: Default State for ${currentId}`);
        
        const transcludedIds = new Set();
        const localLinks = document.querySelectorAll('article a.link.local, article a.slug');
        
        localLinks.forEach(link => {
            const href = link.getAttribute('href');
            const cleanId = extractIdFromPath(href);
            if (cleanId) {
                transcludedIds.add(cleanId);
                // Dynamically harvest the text from the link to use as the title if it isn't in JSON
                if (!allNodesDict[cleanId]) {
                    // Remove brackets if it's a slug, otherwise take text content
                    allNodesDict[cleanId] = link.textContent.replace(/^\[|\]$/g, '').trim(); 
                }
            }
        });

        if (transcludedIds.size === 0) {
            container.innerHTML = "<p style='padding: 1rem; color: #888; font-style: italic; text-align: center; margin-top: 2rem;'>No graph relations or transclusions found for this page.</p>";
            return;
        }

        allEdges.forEach(edge => {
            if (transcludedIds.has(edge.source) || transcludedIds.has(edge.target)) {
                filteredEdges.push(edge);
            }
        });

        if (filteredEdges.length === 0) {
            container.innerHTML = "<p style='padding: 1rem; color: #888; font-style: italic; text-align: center; margin-top: 2rem;'>Transclusions found, but they have no defined relations.</p>";
            return;
        }
    }

    // --- Format for Cytoscape ---
    const cyElements = [];
    const uniqueNodes = new Set();

    filteredEdges.forEach(edge => {
        // Look up the human-readable title, fallback to ID
        if (!uniqueNodes.has(edge.source)) {
            uniqueNodes.add(edge.source);
            const sourceTitle = allNodesDict[edge.source] || edge.source;
            cyElements.push({ data: { id: edge.source, label: sourceTitle } });
        }
        if (!uniqueNodes.has(edge.target)) {
            uniqueNodes.add(edge.target);
            const targetTitle = allNodesDict[edge.target] || edge.target;
            cyElements.push({ data: { id: edge.target, label: targetTitle } });
        }
        
        cyElements.push({
            data: {
                id: `${edge.source}-${edge.target}`,
                source: edge.source,
                target: edge.target,
                relation: edge.relation,
                label: edge.relation
            }
        });
    });
    
    // --- Initialize Cytoscape ---
    const cy = cytoscape({
        container: container,
        elements: cyElements,

        minZoom: 0.6,
        maxZoom: 1.2,

        style: [
            {
                selector: 'node',
                style: {
                    // 1. Card Layout
                    'shape': 'round-rectangle',
                    'background-color': '#ffffff',
                    'border-width': 2,
                    'border-color': '#4a90e2', // Default Blue Stroke
                    
                    // 2. Dynamic Sizing
                    'width': 'label',
                    'height': 'label',
                    'padding': '10px',
                    
                    // 3. Node Typography (Mimicking details h1)
                    'label': 'data(label)',
                    'color': '#000000',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'font-family': '"Inria Sans", sans-serif',
                    'font-size': '17px',
                    'font-weight': 'bold',
                    'text-wrap': 'wrap',
                    'text-max-width': '150px',
                    
                    'transition-property': 'border-color, border-width',
                    'transition-duration': '0.2s'
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 2,
                    'line-color': '#ccc',
                    'target-arrow-color': '#ccc',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier',
                    
                    // 4. Edge Typography (Mimicking p)
                    'label': '', // Hidden by default
                    'font-family': '"Inria Sans", sans-serif',
                    'font-size': '16px',
                    'font-weight': 'normal',
                    'color': '#444444',
                    
                    'text-rotation': 'none',
                    'text-background-opacity': 1,
                    'text-background-color': '#ffffe0', // Match grid background
                    'text-background-padding': '3px',
                    'text-border-opacity': 1,
                    'text-border-width': 1,
                    'text-border-color': '#ccc'
                }
            },
            {
                selector: 'node.dummy',
                style: {
                    'width': 1,       // Virtually invisible
                    'height': 1,
                    'padding': 0,
                    'border-width': 0,
                    'opacity': 0,     // Completely transparent
                    'label': '',
                    'events': 'no'    // Unclickable
                }
            },
            {
                selector: 'edge.dummy-edge',
                style: {
                    'width': 2,
                    'line-color': '#ccc',
                    'target-arrow-shape': 'none', // Hide arrow for intermediate segments
                    'curve-style': 'straight',
                    'line-cap': 'round',

                    // Restore Label visibility
                    'label': '',
                    'font-family': '"Inria Sans", sans-serif',
                    'font-size': '16px',
                    'font-weight': 'normal',
                    'color': '#444',
                    'text-rotation': 'none', 
                    'text-background-opacity': 1,
                    'text-background-color': '#ffffe0',
                    'text-background-padding': '3px'
                }
            },
            // Restore arrows only for the final segment connected to a real node
            {
                selector: 'edge.dummy-edge[target !*= "dummy"]', 
                style: {
                    'target-arrow-shape': 'triangle',
                    'target-arrow-color': '#ccc'
                }
            },
            // State 2: Center node highlighting (Red Stroke)
            {
                selector: `node[id = "${highlightNodeId}"]`,
                style: {
                    'border-color': '#e74c3c',
                    'border-width': 3
                }
            },
            // State 3: Selected Node (Green Stroke)
            {
                selector: 'node.selected',
                style: {
                    'border-color': '#2ecc71',
                    'border-width': 3
                }
            },
            // State 3: Reveal Semantic Label on Connected Edges
            {
                selector: 'edge.show-label',
                style: {
                    'label': 'data(relation)',
                    'line-color': '#2ecc71',
                    'target-arrow-color': '#2ecc71'
                }
            },
        ],
        layout: { name: 'preset' }
    });

    // Center the graph on the main node if in State 2
    if (highlightNodeId) {
        runSugiyamaLayout(highlightNodeId);
        cy.ready(() => {
            const mainNode = cy.getElementById(highlightNodeId);
            if (mainNode.length > 0) {
                cy.center(mainNode);
                // mainNode.connectedEdges().addClass('show-label');
                getFullPolylineEdges(mainNode).addClass('show-label');
            }
        });
    } else {
        if (cy.nodes().length > 0) {
            runSugiyamaLayout(cy.nodes()[0].id());
        }
    }

    // --- Card Stack Initialization ---
    let cardStack = document.getElementById('graph-card-stack');
    let closeAllBtn = document.getElementById('close-all-cards');

    if (!cardStack) {
        cardStack = document.createElement('div');
        cardStack.id = 'graph-card-stack';
        container.appendChild(cardStack);
        
        // Event delegation for closing individual cards
        cardStack.addEventListener('click', (e) => {
            if (e.target.classList.contains('close-card')) {
                const card = e.target.closest('.graph-card');
                if (card) {
                    card.remove();
                    updateCloseAllBtn();
                }
            }
        });

        // fixes the "clicking through to nodes behind" issue.
        const stopEvents = [
            'mousedown'
        ];
        stopEvents.forEach(evt => {
            cardStack.addEventListener(evt, (e) => {
                e.stopPropagation();
            });
        });
    }

    if (!closeAllBtn) {
        closeAllBtn = document.createElement('button');
        closeAllBtn.id = 'close-all-cards';
        closeAllBtn.textContent = 'Close All Documents';
        container.appendChild(closeAllBtn);

        // Logic to close all cards at once
        closeAllBtn.addEventListener('click', closeAllCardsAction);

        // Prevent zooming when hovering the Close All button
        closeAllBtn.addEventListener('mouseenter', () => {
            cy.userZoomingEnabled(false);
            cy.userPanningEnabled(false);
        });
        closeAllBtn.addEventListener('mouseleave', () => {
            cy.userZoomingEnabled(true);
            cy.userPanningEnabled(true);
        });
    }

    // --- Global Shortcut for Closing All ---
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && cardStack.children.length > 0) {
            // Trigger the same cleanup logic as the button
            closeAllCardsAction();
        }
    });

    // Extracted "Close All" logic to reuse for Button and Esc key
    function closeAllCardsAction() {
        cardStack.innerHTML = ''; 
        updateCloseAllBtn();
        cy.elements().removeClass('selected show-label'); 
        
        // Restore State 2 defaults (Smart Center not needed here, use default)
        if (highlightNodeId) {
            const mainNode = cy.getElementById(highlightNodeId);
            if (mainNode.length > 0) {
                mainNode.connectedEdges().addClass('show-label');
                cy.animate({ center: { eles: mainNode }, duration: 300 });
            }
        }
    }

    // Helper to sync button visibility with stack count
    function updateCloseAllBtn() {
        if (cardStack.children.length > 0) {
            closeAllBtn.style.display = 'block';
        } else {
            closeAllBtn.style.display = 'none';
        }
    }

    // --- Smart Centering Logic ---
    function smartCenter(node) {
        // Calculate the width of the card stack (350px width + 20px right margin = 370px)
        // We assume the stack is open if we are calling this function during a tap
        const stackOffset = 370; 
        
        const w = cy.width();
        const h = cy.height();
        
        // The target "center" x-coordinate is the middle of the remaining free space
        const targetX = (w - stackOffset) / 2;
        const targetY = h / 2;

        // Calculate the pan required to move the node to that screen position
        // Formula: Pan = TargetScreenPos - (NodeModelPos * Zoom)
        const zoom = cy.zoom();
        const pos = node.position();
        
        const finalPan = {
            x: targetX - (pos.x * zoom),
            y: targetY - (pos.y * zoom)
        };

        cy.animate({
            pan: finalPan,
            zoom: zoom, // Keep zoom level constant or set a specific level
            duration: 300
        });
    }

    // Recursive function to extract text and structure while skipping transclusions
    function serializeNode(node) {
        const name = node.nodeName ? node.nodeName.toLowerCase() : '';
        
        // Explicitly ignore transcluded trees
        if (name === 'fr:tree' || name === 'tree') return '';
        
        if (node.nodeType === Node.TEXT_NODE) return node.nodeValue;
        
        if (node.nodeType === Node.ELEMENT_NODE) {
            // Preserve LaTeX formatting
            if (name === 'f:tex' || name === 'fr:tex') {
                const isBlock = node.getAttribute('display') === 'block';
                return isBlock ? '\\[' + node.textContent + '\\]' : '\\(' + node.textContent + '\\)';
            }
            
            // Format paragraphs
            if (name === 'html:p' || name === 'p') {
                let html = '<p>';
                for (let i = 0; i < node.childNodes.length; i++) html += serializeNode(node.childNodes[i]);
                return html + '</p>';
            }

            // <html:em>
            if (name === 'html:em' || name === 'em') {
                let html = '<em>';
                for (let i = 0; i < node.childNodes.length; i++) html += serializeNode(node.childNodes[i]);
                return html + '</em>';
            }

            // <html:strong>
            if (name === 'html:strong' || name === 'strong') {
                let html = '<strong>';
                for (let i = 0; i < node.childNodes.length; i++) html += serializeNode(node.childNodes[i]);
                return html + '</strong>';
            }

            // <html:mark>
            if (name === 'html:mark' || name === 'mark') {
                let html = '<mark>';
                for (let i = 0; i < node.childNodes.length; i++) html += serializeNode(node.childNodes[i]);
                return html + '</mark>';
            }

            // Format Unordered Lists
            if (name === 'html:ul' || name === 'ul') {
                let html = '<ul style="margin-top: 0; padding-left: 20px;">';
                for (let i = 0; i < node.childNodes.length; i++) html += serializeNode(node.childNodes[i]);
                return html + '</ul>';
            }

            // Format Ordered Lists
            if (name === 'html:ol' || name === 'ol') {
                let html = '<ol style="margin-top: 0; padding-left: 20px;">';
                for (let i = 0; i < node.childNodes.length; i++) html += serializeNode(node.childNodes[i]);
                return html + '</ol>';
            }

            // Format List Items
            if (name === 'html:li' || name === 'li') {
                let html = '<li style="margin-bottom: 5px;">';
                for (let i = 0; i < node.childNodes.length; i++) html += serializeNode(node.childNodes[i]);
                return html + '</li>';
            }
            
            // Fallback: extract inner content of other unrecognized tags
            let innerHTML = '';
            for (let i = 0; i < node.childNodes.length; i++) innerHTML += serializeNode(node.childNodes[i]);
            return innerHTML;
        }
        return '';
    }

    // --- SUGIYAMA LAYOUT ALGORITHM ---
    function runSugiyamaLayout(rootId) {
        if (!rootId) {
            const nodes = cy.nodes();
            if (nodes.length > 0) rootId = nodes[0].id();
            else return;
        }

        const visited = new Set();
        const ranks = new Map(); // Map<NodeID, IntegerRank>
        const queue = [];

        // --- STEP 1: Layering (BFS) ---
        ranks.set(rootId, 0);
        visited.add(rootId);
        queue.push(rootId);

        while (queue.length > 0) {
            const uId = queue.shift();
            const currentRank = ranks.get(uId);
            const uNode = cy.getElementById(uId);

            // Outgoing (Rank + 1)
            uNode.outgoers('edge').forEach(edge => {
                const targetId = edge.target().id();
                if (!visited.has(targetId)) {
                    visited.add(targetId);
                    ranks.set(targetId, currentRank + 1);
                    queue.push(targetId);
                }
            });

            // Incoming (Rank - 1)
            uNode.incomers('edge').forEach(edge => {
                const sourceId = edge.source().id();
                if (!visited.has(sourceId)) {
                    visited.add(sourceId);
                    ranks.set(sourceId, currentRank - 1);
                    queue.push(sourceId);
                }
            });
        }

        // Handle disconnected nodes (put them at Rank 0)
        cy.nodes().forEach(node => {
            if (!ranks.has(node.id())) ranks.set(node.id(), 0);
        });

        // --- STEP 2: Normalization (Insert Dummy Nodes) ---
        const edges = cy.edges().toArray();
        
        edges.forEach(edge => {
            const sourceId = edge.source().id();
            const targetId = edge.target().id();
            const relationText = edge.data('label') || '';
            const r1 = ranks.get(sourceId);
            const r2 = ranks.get(targetId);
            const diff = r2 - r1;

            // If edge spans more than 1 layer (e.g. Rank 0 -> Rank 2)
            if (Math.abs(diff) > 1) {
                // Remove original edge
                cy.remove(edge);

                let currentSource = sourceId;
                const direction = diff > 0 ? 1 : -1;
                const totalSegments = Math.abs(diff);
                const middleSegmentIndex = Math.floor(totalSegments / 2);
                
                // Create chain of dummy nodes
                for (let i = 1; i < Math.abs(diff); i++) {
                    const rankOfDummy = r1 + (i * direction);
                    const dummyId = `dummy_${sourceId}_${targetId}_${i}`;
                    
                    // Add invisible dummy node
                    cy.add({
                        group: 'nodes',
                        data: { id: dummyId, label: '' },
                        classes: 'dummy' // Mark for styling
                    });
                    ranks.set(dummyId, rankOfDummy);

                    const currentSegmentIndex = i - 1;
                    const isMiddle = (currentSegmentIndex === middleSegmentIndex)
                    
                    // const segmentLabel = (i === middleSegmentIndex) ? relationText : '';

                    // Connect previous node to dummy
                    cy.add({
                        group: 'edges',
                        data: { 
                            source: currentSource,
                            target: dummyId,
                            // label: segmentLabel,
                            relation: isMiddle ? relationText : '',
                        },
                        classes: 'dummy-edge'
                    });
                    
                    currentSource = dummyId;
                }

                // Final segment connects to the real target
                // If there was only 1 dummy node (2 segments), label might go here
                const finalLabel = (totalSegments === 1) ? relationText : '';
                const currentSegmentIndex = totalSegments - 1;
                const isMiddle = (currentSegmentIndex === middleSegmentIndex);

                
                cy.add({
                    group: 'edges',
                    data: { 
                        source: currentSource, 
                        target: targetId,
                        // label: finalLabel,
                        relation: isMiddle ? relationText : '',
                    },
                    classes: 'dummy-edge' 
                });
            } else {
                edge.data('relation', relationText)
            }
        });

        // --- STEP 3: Ordering (Crossing Minimization - Barycenter Heuristic) ---
        // Group nodes by rank
        const layers = new Map();
        ranks.forEach((rank, nodeId) => {
            if (!layers.has(rank)) layers.set(rank, []);
            layers.get(rank).push(nodeId);
        });

        // Get min and max rank to iterate
        const minRank = Math.min(...layers.keys());
        const maxRank = Math.max(...layers.keys());

        // Simple single-pass sort (Top -> Down)
        for (let r = minRank + 1; r <= maxRank; r++) {
            const layerNodes = layers.get(r) || [];
            
            // Sort nodes in this layer based on average X of their parents in (r-1)
            // (Note: Since we haven't assigned X yet, we use the *order* in the previous array as a proxy)
            layerNodes.sort((aId, bId) => {
                const getAvgParentIndex = (nodeId) => {
                    const parents = cy.getElementById(nodeId).incomers('node');
                    if (parents.length === 0) return 0;
                    
                    let sum = 0;
                    parents.forEach(p => {
                        const pRank = ranks.get(p.id());
                        // Only consider parents in the immediate previous layer
                        if (pRank === r - 1) {
                            const parentLayer = layers.get(pRank);
                            sum += parentLayer.indexOf(p.id());
                        }
                    });
                    return sum / parents.length;
                };

                return getAvgParentIndex(aId) - getAvgParentIndex(bId);
            });
        }

        // --- STEP 4: Coordinate Assignment ---
        const verticalSpacing = 150;
        const horizontalSpacing = 200;
        const positions = {};

        layers.forEach((nodeIds, rank) => {
            const rowWidth = (nodeIds.length - 1) * horizontalSpacing;
            let currentX = -rowWidth / 2;

            nodeIds.forEach(id => {
                positions[id] = { x: currentX, y: rank * verticalSpacing };
                currentX += horizontalSpacing;
            });
        });

        // --- STEP 5: Draw ---
        cy.layout({
            name: 'preset',
            positions: positions,
            animate: true,
            animationDuration: 500,
            padding: 50
        }).run();
    }

    // Helper: Traverse dummy nodes to find all segments of a polyline
    function getFullPolylineEdges(node) {
        let allEdges = cy.collection();
        const immediateEdges = node.connectedEdges();

        immediateEdges.forEach(edge => {
            allEdges = allEdges.add(edge);

            // 1. Forward Traversal (Source -> Target -> Dummy...)
            if (edge.source().id() === node.id()) {
                let currNode = edge.target();
                while (currNode.hasClass('dummy')) {
                    const nextEdges = currNode.outgoers('edge');
                    if (nextEdges.length > 0) {
                        const nextEdge = nextEdges[0]; // Dummy nodes usually have 1 outgoing
                        allEdges = allEdges.add(nextEdge);
                        currNode = nextEdge.target();
                    } else {
                        break;
                    }
                }
            }

            // 2. Backward Traversal (Target -> Source -> Dummy...)
            else if (edge.target().id() === node.id()) {
                let currNode = edge.source();
                while (currNode.hasClass('dummy')) {
                    const prevEdges = currNode.incomers('edge');
                    if (prevEdges.length > 0) {
                        const prevEdge = prevEdges[0]; // Dummy nodes usually have 1 incoming
                        allEdges = allEdges.add(prevEdge);
                        currNode = prevEdge.source();
                    } else {
                        break;
                    }
                }
            }
        });
        return allEdges;
    }

    // --- STATE 3 LOGIC: Event Listeners & Content Fetching ---
    cy.on('tap', 'node', function(evt) {
        const node = evt.target;
        const nodeId = node.id();
        const nodeTitle = node.data('label') || nodeId;

        cy.elements().removeClass('selected show-label'); 
        node.addClass('selected');
        const connectedChain = getFullPolylineEdges(node);
        connectedChain.addClass('show-label'); 
        
        smartCenter(node);

        // Goal 1: Check if card already exists in the stack
        const existingCard = cardStack.querySelector(`.graph-card[data-node-id="${nodeId}"]`);
        if (existingCard) {
            // Reinserting an existing node moves it to the bottom of the flex container automatically
            cardStack.appendChild(existingCard);
            return; // Stop here. Do not create a new card or fetch data again.
        }

        // Feature 4: FIFO Limit to 3 cards
        if (cardStack.children.length >= 3) {
            cardStack.removeChild(cardStack.firstElementChild);
        }

        // Create the new card UI
        const targetUrl = baseUrl + nodeId + '/index.xml';
        const card = document.createElement('div');
        card.className = 'graph-card';
        card.dataset.nodeId = nodeId;
        
        card.innerHTML = `
            <div class="card-header">
                <h3>${nodeTitle}</h3>
                <button class="close-card">×</button>
            </div>
            <div class="card-body">
                <p><em>Loading definition...</em></p>
            </div>
            <div class="card-footer">
                <a href="${baseUrl}${nodeId}/index.html">Read full note →</a>
            </div>
        `;

        // Directly tell Cytoscape to stop listening when mouse is over this specific card
        card.addEventListener('mouseenter', () => {
            cy.userZoomingEnabled(false);
            cy.userPanningEnabled(false); // Also stops drag-panning
        });
        card.addEventListener('mouseleave', () => {
            cy.userZoomingEnabled(true);
            cy.userPanningEnabled(true);
        });

        cardStack.appendChild(card);

        // Goal 2: Ensure button becomes visible
        updateCloseAllBtn();

        // Fetch XML content
        fetch(targetUrl)
            .then(response => {
                if (!response.ok) throw new Error("Document not found");
                return response.text();
            })
            .then(xmlText => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(xmlText, 'text/xml');
                
                const mainmatter = doc.getElementsByTagName('fr:mainmatter')[0] || doc.getElementsByTagName('mainmatter')[0];
                let contentHTML = "<p>No summary available.</p>";
                
                if (mainmatter) {
                    contentHTML = '';
                    for (let i = 0; i < mainmatter.childNodes.length; i++) {
                        contentHTML += serializeNode(mainmatter.childNodes[i]);
                    }
                    if (!contentHTML.trim()) contentHTML = "<p>No summary available.</p>";
                }

                const cardBody = card.querySelector('.card-body');
                cardBody.innerHTML = contentHTML;

                // Render KaTeX for this specific card
                if (window.renderMathInElement) {
                    renderMathInElement(cardBody, {
                        delimiters: [
                            {left: '\\[', right: '\\]', display: true},
                            {left: '\\(', right: '\\)', display: false}
                        ]
                    });
                }
            })
            .catch(err => {
                card.querySelector('.card-body').innerHTML = `<p>Cannot load content details.</p>`;
                console.error(err);
            });
    });

    // Deselection: Click background to restore defaults (but do not delete cards)
    cy.on('tap', function(evt){
        if( evt.target === cy ){
            cy.elements().removeClass('selected show-label');
            
            if (highlightNodeId) {
                const mainNode = cy.getElementById(highlightNodeId);
                if (mainNode.length > 0) {
                    mainNode.connectedEdges().addClass('show-label');
                }
            }
        }
    });
}

```

--- 

### 1. Forester `.tree` File Grammar

A `.tree` file in Forester consists of two main parts: the **Preamble** (Metadata) and the **Body** (Content). The syntax is widely TeX-like but distinct in how it handles text and code.

#### **A. The Preamble**

* `\title{...}`: The title of the node.
* `\taxon{...}`: The type of content (e.g., `Definition`, `Theorem`, `Axiom`, `Reference`).
* `\date{...}`: YYYY-MM-DD.
* `\author{...}`: Author identifier.
* `\meta{key}{value}`: Custom metadata.

#### **B. The Body (`\p` blocks)**

* **Standard Text:** Write normally.
* **Inline Math:** Use `#{ ... }`. Example: `#{f(x) = x^2}`.
* **Block Math:** Use `##{ ... }`. Example: `##{ \int x dx }`.
* **Terminology:** Use `\strong{term}` when defining a new word.
* **Highlighting:** Use `\mark{...}` **only** for critical sentences or core insights.
* **Lists:** `\ul{ \li{...} }` or `\ol{ \li{...} }`.
* **Transclusion:** `\transclude{tree-id}` (usually in index files).
* **Links:** `[Link Text](url)` or `[[tree-id]]`.

---

Here is the summarized logic for file creation.

### 1. File Structure Logic

The file naming and structure follow a strict **Code-Based System** (`XYZ-Title`) to organize themes chronologically or categorically.

#### **A. The Code (`005`, `003`, etc.)**

* **Purpose:** A unique identifier for a specific theme or project, ordered by creation date.
* **Example:** `003` for Reading, `004` for Semantic Tests, `005` for Gemini Examples.
* **Usage:** Every file belonging to this theme must start with this code (e.g., `005-Limit.tree`).

#### **B. The Specific Pages (The "Nodes")**

* **Role:** These are the atomic units of knowledge. They contain the actual definitions, theorems, or explanations.
* **Naming:** `<code>-<kebab-case-title>.tree`
* **Content:**
* Defines **one** specific concept.
* Uses `\taxon{Definition}` (or similar).
* Uses `\strong{term}` for the term being defined.
* Uses `\mark{...}` **only** for the most critical insight.

#### **C. The Index Page (The "Wikipedia Article")**

* **Role:** The entry point and narrative summary of the theme. It reads like a cohesive article.
* **Naming:** `<code>-index.tree`
* **Structure:**
1. **Introduction:** A high-level summary of the topic.
2. **Hyperlinks (`[text](code-slug)`):** Used for *contextual* concepts that are **not** defined within this specific tree (e.g., "Mathematics", "Graph Theory"). These link to separate summary trees (often prefixed with `d-` or similar if they are external definitions, or just their own code).
3. **Transclusions (`\transclude{code-slug}`):** Used for the **core concepts** that *are* defined in this tree. Instead of linking to them, you embed their content directly into the flow of the document so the reader sees the definition immediately.

#### **D. The Relations Page (The "Graph")**

* **Role:** A hidden metadata file that defines the semantic graph structure.
* **Naming:** `<code>-relations.tree`
* **Content:** A list of `\relation{source}{type}{target}` commands.

### Examples of file construction

#### 1. Example: `005-Limit.tree`

**Filename:** `005-Limit.tree`

```tex
\title{Limit}
\taxon{Definition}
\date{2026-02-12}
\author{gemini}
\import{base-macros}

\p{
  A \strong{limit} of a diagram #{F: J \to \mathcal{C}} is a "universal cone" #{(L, \phi)} to #{F}.
}

\p{
  This means that for any other cone #{(N, \psi)} to #{F}, \mark{there exists a unique morphism #{u: N \to L} such that the triangles commute}.
}

\p{
  Formally, we say that there is a natural isomorphism:
  ##{
    \text{Hom}_{\mathcal{C}}(N, \text{Lim } F) \cong \text{Cone}(N, F)
  }
}

```

#### 2. Example: `005-Product.tree`

**Filename:** `005-Product.tree`

```tex
\title{Product}
\taxon{Definition}
\date{2026-02-12}
\author{gemini}
\import{base-macros}

\p{
  A \strong{product} of a family of objects #{\{X_i\}} is the limit of the diagram consisting of these objects with no non-identity morphisms between them (the discrete diagram).
}

\p{
  \mark{The product is the most fundamental example of a limit}, representing the "shared" structure of independent objects.
}

```

#### 3. Example: The Index Page

1. **Hyperlinks**: `category theory` and `morphisms` are linked because they are broad, pre-existing concepts.

2. **Transclusions**: `Limit`, `Product`, etc., are embedded because they are the new definitions provided by this specific document.

**Filename:** `005-index.tree`

```tex
\title{Category Theory: Limits}
\taxon{Reference}
\date{2026-02-12}
\author{gemini}
\import{base-macros}

\p{
  In [mathematics](d-mathematics) and specifically [category theory](d-category-theory), a \strong{limit} is a universal construction that generalizes concepts like products, pullbacks, and inverse limits. It is defined using the language of [diagrams](005-diagram) and [cones](005-cone).
}

\p{
  Limits are central to understanding how mathematical objects relate to one another via [morphisms](d-morphism). A category where all limits exist is called \strong{complete}.
}

\transclude{005-Limit}
\transclude{005-Product}
\transclude{005-Equalizer}
\transclude{005-Pullback}
```

#### 4. Example: The Semantic Relations

**Filename:** `005-relations.tree`

```tex
\title{Relations}
\taxon{Metadata}
\date{2026-02-11}
\author{gemini}
\import{base-macros}

% The Hierarchy of Definition
\relation{005-Category}{contains}{005-Functor}
\relation{005-Functor}{transforms}{005-Natural-Transformation}
\relation{005-Functor}{defines}{005-Diagram}
\relation{005-Diagram}{shapes}{005-Cone}
\relation{005-Cone}{approximates}{005-Limit}

% Specific Examples of Limits
\relation{005-Limit}{generalizes}{005-Product}
\relation{005-Limit}{generalizes}{005-Equalizer}
\relation{005-Limit}{generalizes}{005-Pullback}

% Inter-example connections (Ring structure elements)
\relation{005-Product}{constructs}{005-Pullback}
\relation{005-Equalizer}{constructs}{005-Pullback}

% The outlier node (Reachability check)
\relation{005-Limit}{exemplifies}{005-Universal-Property}
\relation{005-Universal-Property}{characterizes}{005-Category}
```