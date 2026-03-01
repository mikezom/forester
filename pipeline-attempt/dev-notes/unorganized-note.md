TODO List:

1. 鼠标移到左边上面的时候需要显示summary，鼠标（可能加一个快捷键，鼠标+control）点右边，需要实现左边对应的内容

1. 图里需要能找对应的node
2. 进概念再回来需要回到原部分（如果左边能显示summary可能不用）

1. 不一定需要根据文章原有的结构来生成，而希望根据concept里的结构来生成。

1. 原文里的图可以读tex

1. Do not tranclude a definition directly from the main index page.
2. Maybe we should create a summary 
3. Compatibility regarding tex and json. Maybe using YAML?
4. Regarding the definition that are not included in the document, maybe we need to add more additional knowledge.
5. The prerequisite should be using the standard json? yaml? format. However, it includes additional information.
6. need to remove duplicate edge with different semantic conjunction
7. There can only be one relation between two concepts
8. Use & instead of \&, use $ instead of \$

---

We need to continue development based on examples. 

---

不同层级的视觉差异拉开
空行、字体大小、粗细
字体、粗细、衬线、颜色？

标题拉大加粗

希望中文和英文有完全对应的逻辑结构，才好调整

引用卡片化，用户往下扫的时候能知道哪里可以不看

调标题大小/样式

中间可以有个东西表示读了多少。可以走得比预期快一点。

---

为什么我们在读一些数学文章的时候比较舒服？

- 没有大段的文字
- 数学公式的缩进可以给用户一种视觉上的刺激，减少无聊感
- 定义、证明、交互、备注、推论、以及数学公式交替出现。如果你不想阅读一个Lemma的证明，那么你可以跳过。提供一种交互的阅读体验。
- 并不一定只有三层（文章、章节、备注），而是需要有一个更加复杂的层级关系
- 数学文章具有强逻辑性，并且结构常常和推导过程有关，所以会自然地产生和概念图的关联。

目前中文文章的缺陷

- 过多使用了加粗。这使得层级变得不够清晰。

---
### 如何在 Pipeline 中使用此 Prompt

1.  **Step 1 (Ingestion)**: 依然保持不变，将文章切块。
2.  **Step 2 (Analysis)**:
    * 将切块后的 Markdown 喂给 LLM。
    * 使用上述 System Prompt。
    * 得到 JSON list。
3.  **Step 3 (Synthesis - Python Script)**:
    * 解析 JSON。
    * 对于每一个 Unit，生成一个独立的 `.tree` 文件。
    * 文件头部的 `\taxon{}` 直接使用 JSON 中的 `taxon` (e.g., `\taxon{Theorem}`).
    * 如果是 `Proof` 或 `Remark`，你可以在 Forester 的 CSS 中给它们设定特定的样式（例如：Proof 默认灰色，Definition 默认高亮）。

---

Markdown Theory

- Headings are used to define the structural hierarchy of a document.
- There should only be one `H1`, in our case, the index tree. 
- Bold the few words of a list item to make it a structural list (
    - since trancluding text auto includes the title, and the titles are bolded, we make the following correction:
    - Incorrect:
        ```
            \p{
                \strong{Important Concept}
            }
            \tranclude{important-concept}
        ```
    - Correct:
        ```
            \tranclude{important-concept}
        ```

---

Correct:

```
\table{
  \tr{
    \th{Layer Type}
    \th{Complexity}
    \th{Sequential}
    \th{Path Length}
  }
  \tr{
    \td{Self-Attention}
    \td{#{O(n^2 \cdot d)}}
    \td{#{O(1)}}
    \td{#{O(1)}}
  }
  \tr{
    \td{Recurrent}
    \td{#{O(n \cdot d^2)}}
    \td{#{O(n)}}
    \td{#{O(n)}}
  }
  \tr{
    \td{Convolutional}
    \td{#{O(k \cdot n \cdot d^2)}}
    \td{#{O(1)}}
    \td{#{O(\log_k(n))}}
  }
  \tr{
    \td{Self-Attention (restricted)}
    \td{#{O(r \cdot n \cdot d)}}
    \td{#{O(1)}}
    \td{#{O(n/r)}}
  }
}
```

Incorrect:

```
\p{
  ##{
    \begin{array}{|l|c|c|c|}
    \hline
    \text{Layer Type} & \text{Complexity} & \text{Sequential} & \text{Path Length} \\
    \hline
    \text{Self-Attention} & O(n^2 \cdot d) & O(1) & O(1) \\
    \text{Recurrent} & O(n \cdot d^2) & O(n) & O(n) \\
    \text{Convolutional} & O(k \cdot n \cdot d^2) & O(1) & O(\log_k(n)) \\
    \text{Self-Attention (restricted)} & O(r \cdot n \cdot d) & O(1) & O(n/r) \\
    \hline
    \end{array}
  }
}
```

---

Alread done:

1. Use \aside{...} for conjunctions 
2. 原文里的%应该换成\%
3. definition里的D要大写
4. Conjunction应该降低一个层级
5. use \table macro instead of tex array environment
6. [Solved] tex rendering 有问题: array里不能有引用like`[content](007-content)`