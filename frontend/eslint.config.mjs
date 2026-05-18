// ESLint 9 flat config.
//
// Pinned versions (must match exactly across pre-commit + CI + package.json):
//   eslint              == 9.39.4
//   typescript-eslint   == 8.59.3
//   eslint-config-next  == 15.5.18
//   @eslint/eslintrc    == 3.3.5  (FlatCompat shim — see D-021 tech debt)
//
// `eslint-config-next` v15 still exports in legacy .eslintrc format and
// depends on @rushstack/eslint-patch, which is incompatible with ESLint 9's
// module resolution. FlatCompat bridges the legacy config into flat-config
// shape. Remove the shim (and the @eslint/eslintrc dep) once
// eslint-config-next ships native flat-config support — see D-021.
//
// `eslint-config-next` major version tracks Next.js major (Next 15 →
// eslint-config-next 15). Bump together.

import { FlatCompat } from '@eslint/eslintrc';
import tseslint from 'typescript-eslint';

const compat = new FlatCompat({ baseDirectory: import.meta.dirname });

export default [
  // Global ignores — must be a config object with ONLY `ignores` (ESLint 9
  // semantics). Skip generated/build output and the auto-generated Next types
  // file. `node_modules` is excluded by ESLint by default but listed for clarity.
  {
    ignores: [
      '.next/**',
      'out/**',
      'dist/**',
      'next-env.d.ts',
      'node_modules/**',
    ],
  },
  ...compat.extends('next/core-web-vitals'),
  ...tseslint.configs.recommended,
  {
    rules: {
      '@typescript-eslint/no-explicit-any': 'error',
    },
  },
];
