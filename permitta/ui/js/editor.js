// import {EditorState} from "@codemirror/state"
// import {EditorView, keymap} from "@codemirror/view"
// import {defaultKeymap} from "@codemirror/commands"
//
// document.body.addEventListener("load_codemirror", function(evt){
//   let startState = EditorState.create({
//     doc: "Hello World",
//     extensions: [keymap.of(defaultKeymap)]
//   })
//
//   let element = document.getElementById("editor");
//
//   let view = new EditorView({
//     state: startState,
//     parent: element
//   })
//   console.log("Codemirror loaded", element)
// });
// console.log("Codemirror imported")

import { EditorState } from '@codemirror/state';
import { highlightSelectionMatches } from '@codemirror/search';
import { indentWithTab, history, defaultKeymap, historyKeymap } from '@codemirror/commands';
import { foldGutter, indentOnInput, indentUnit, bracketMatching, foldKeymap, syntaxHighlighting, defaultHighlightStyle } from '@codemirror/language';
import { closeBrackets, autocompletion, closeBracketsKeymap, completionKeymap } from '@codemirror/autocomplete';
import { lineNumbers, highlightActiveLineGutter, highlightSpecialChars, drawSelection, dropCursor, rectangularSelection, crosshairCursor, highlightActiveLine, keymap, EditorView } from '@codemirror/view';
import { isDarkMode } from './dark-mode.js'

// Theme
import { oneDark } from "@codemirror/theme-one-dark";

// Language
import { javascript } from "@codemirror/lang-javascript";



document.body.addEventListener("load_codemirror", function(evt){
    let readonly = evt.detail.readonly === "true";

    let extensions = [
        lineNumbers(),
        highlightActiveLineGutter(),
        highlightSpecialChars(),
        history(),
        foldGutter(),
        drawSelection(),
        indentUnit.of("    "),
        EditorState.allowMultipleSelections.of(true),
        indentOnInput(),
        bracketMatching(),
        closeBrackets(),
        autocompletion(),
        rectangularSelection(),
        crosshairCursor(),
        highlightActiveLine(),
        highlightSelectionMatches(),
        keymap.of([
            indentWithTab,
            ...closeBracketsKeymap,
            ...defaultKeymap,
            ...historyKeymap,
            ...foldKeymap,
            ...completionKeymap,
        ]),
        javascript(),
        syntaxHighlighting(defaultHighlightStyle, { fallback: true }),
        EditorState.readOnly.of(readonly)
    ];

    // enables dark mode
    if (isDarkMode()) {
        extensions.push(oneDark);
    }

    let contentElement = document.getElementById("dsl-content");

    let startState= EditorState.create({
        doc: contentElement.innerText,
        extensions
    });

    let editorElement = document.getElementById("editor");

    let view = new EditorView({
      state: startState,
      parent: editorElement
    });
    console.log("Codemirror loaded with config: readonly=", evt.detail.readonly);
});