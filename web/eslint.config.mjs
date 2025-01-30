import js from "@eslint/js";
import globals from "globals";
import prettier from "eslint-config-prettier";

/** @type {import('eslint').Linter.Config[]} */
export default [
  js.configs.recommended,
  {
    files: ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx"],
    languageOptions: {
      globals: globals.browser,
      parserOptions: {
        ecmaFeatures: {},
      },
    },
  },
  // Prettier turns off formatting lints, so it always has to be last.
  prettier,
];
