---
description: One-time per repo. Detects the project's stack/tracks (or asks, for an empty repo) and writes .claude/factory/project.json. Does NOT scaffold code.
argument-hint: (no args)
---
Initialise the feature factory for THIS repo by producing `.claude/factory/project.json`.

Steps:
1. Detect build files at the repo root with `ls`: `package.json`, `*.csproj`/`*.sln`, `pom.xml`/`build.gradle`, `Makefile`/`CMakeLists.txt`, `composer.json`.
2. Infer tracks:
   - Frontend if there is a web build (Vite/Next/etc. in package.json) or a `wwwroot`/`public`/`src` web layout.
   - Backend if there is a server framework / API project (.NET, Spring, Express, etc.) or a Makefile/CMake C/C++ build.
   - A repo may have one or both. For each, read the build file to fill `commands` (typecheck/lint/test/build) and identify source `dirs`.
3. If NO build files exist (empty/greenfield repo): read the root `CLAUDE.md` "Tech Stack" section. If it answers the stack, use it. If still unclear, ASK the user: which language/framework, and which tracks (frontend / backend / both). Do NOT scaffold or create source — only record the manifest.
4. Write `.claude/factory/project.json` following the shape of `.claude/factory/project.example.json`. Set `enabled:false` for any absent track. Always include `dist`, `build`, `node_modules`, and any `wwwroot/lib` (or similar vendored dirs) in frontend `protectedDirs`.
5. Print the resulting manifest and ask the user to confirm or correct it. Note any `commands` you left blank because the script (e.g. `test`, `lint`) does not yet exist in the project.

Do not run `/feat-*` build steps here. This command only writes the manifest.
