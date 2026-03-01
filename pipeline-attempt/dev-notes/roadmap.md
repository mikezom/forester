# Forester Foundry

## Road Map

Initial Input: Lengthy Books, Papers, Videos

Final Output: A Forester-based, structural Study Map

### Step 1: Ingestion (The Harvester)

- Goal: Normalize desparate inputs into a clean, chunked format (Markdown/JSON) that preserves mathematical notation.
- Tools:
    - PDF/Academic Papers: Use **Nougat**.
    - Viedo: `yt-dlp` (or other download tools) + `OpenAI Whisper` (transcription) + `pyannote` (speaker diarization).
    - Epub/Text: `Pandoc`
- Process:
    1. User drops `GameTheory_Fudenberg.pdf` into `source/`.
    2. Harvester runs.
    3. Output: `intermediate/GameTheory_Fudenberg/` containing:
    * `meta.json` (Title, Author, Year).
    * `01_introduction.md`
    * `02_strategic_form.md`...

### Step 2: Structural Analysis (The Cartographer)

- Goal: Generate a concept dictionary
- Agent B1:
    - **Input:** The full set of `intermediate/*.md` files.
    - **Task:** Identify the terms that appear across the entire work.
    - **Output:** `registry.json`
    ```json
    {
    "prefix": "007",
    "concepts": {
        "Strategic Form Game": "007-strategic-form",
        "Nash Equilibrium": "007-nash-equilibrium",
        "Subgame Perfect": "007-subgame-perfect"
    }
    }
    ```
- *Human Checkpoint:* You review this JSON. Delete trivial terms. Rename IDs if needed. This is where you exert "Content Planning" control.

### Step 3: Synthesis (The Mason)

- **Goal:** Generate the actual `.tree` files using the `registry.json` as a constraint.
- **Agent B2:** A Python script iterating through chapters.
- **The Prompt Strategy:**
    - "You are a Forester Architect. Here is `registry.json`. Here is `02_strategic_form.md`."
    - "Task 1: Write `007-strategic-form.tree`. Use `\taxon{Definition}`. **Only** use `\transclude{...}` for terms found in `registry.json`."
    - "Task 2: Write `007-index.tree` (The Chapter Summary). Integrate the concepts naturally."
    - "Task 3: Append to `007-relations.tree`: `\relation{007-strategic-form}{requires}{007-nash-equilibrium}`."

- **Terminal Output:**
- `trees/007-strategic-form.tree`
- `trees/007-nash-equilibrium.tree`
- `trees/007-index.tree` (Main narrative)

### Step 4: Validation (The Inspector)

- **Goal:** Regex-based linting before the Forester compiler explodes.
- **Common LLM Errors to Fix:**
- **Markdown vs TeX:** Replacing `**text**` with `\strong{text}`.
- **Math Delimiters:** Ensuring `$` becomes `#{}` or `##{}`.
- **Dangling Links:** Checking if `\transclude{X}` actually exists in the `trees/` folder.
- **Metadata:** Ensuring every file has `\title`, `\date`, and `\author`.