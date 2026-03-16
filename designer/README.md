# Designer Stable v07 — Codebase Cleanup

This version is a pure cleanup of `designer_stable_v_06`. No runtime behavior has been added or changed.

## Runtime files
- `index.html` — HTML shell
- `styles.css` — stylesheet
- `js/app.js` — application script

## Changes from v06

### app.js
- `var` declarations unified to `const`/`let` throughout (ES2015+, consistent with Map/Set/async already in use)
- All module-level constants moved to top: `FIELD_MIN_CHARS`, `URL_TABLES_PARAM`, `URL_STATE_PARAM`
- `createEl` rewritten using rest parameters and `for-of` loops instead of `arguments[]`
- **Bug fix:** `btnCopyDP`/`btnDownloadDP` case inconsistency in `resetDatapackagePanel` fixed — now correctly uses the cached `btnCopyDp`/`btnDownloadDp` variables
- **Bug fix:** `dpSelectedRequiredOnlyCheckbox` event listener changed from `.onchange =` to `.addEventListener` for consistency
- **Bug fix:** `graphPanel.style.display = "block"` moved inside the `visibleNodeCount > 0` branch — the graph container now stays hidden when no tables are selected
- `CIRCLE_LAYOUT` constant introduced to avoid repeating the Cytoscape layout config object
- Whitespace and indentation normalised throughout

### styles.css
- Duplicate `scroll-margin-top` rule removed
- Duplicate `#graphPanel .panel-head h2` rule consolidated with the other large-heading selectors

### index.html
- Inline styles in the sticky header extracted into CSS classes: `.header-row`, `.header-actions`, `.header-version`
- Inline style on `#linkNotice` (margin + border-left) extracted into CSS class `.link-notice-panel`
- `style="margin:0"` on `<h1>` removed (the `h1` CSS rule already sets `margin: 0 0 10px 0`)
