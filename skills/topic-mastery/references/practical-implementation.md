# Practical implementation standard

Learning sticks when the learner builds and runs things. Every chapter with practical content ships a **lab pack** beside the PDF, so anyone can set up, run, break and fix real code without retyping from a document.

## What a chapter ships

```
Chapter_NN_Title/
  Chapter_NN_Title.pdf / .html
  labs/
    README.md          setup, how to run, expected results, troubleshooting (generated)
    run_all.py         one command that runs every lab and checks the output (generated)
    requirements.txt   Python packages (generated)
    python/            runnable Python files
    csharp/            runnable single-file C# programs (.NET 10 file-based apps)
    exercises/         starter files with clearly marked gaps to fill
    solutions/         worked solutions, referenced from the answer key
    data/              small generated or public datasets and the script that makes them
```

Mark code in the chapter with `data-file` (see `code-and-labs.md`), then run
`python scripts/extract_labs.py chapter.html -o labs/ --title "Chapter N labs"` and
`python labs/run_all.py` to prove it works from a clean folder.

## Rules

1. **Start from zero.** Assume a clean machine. The README states every tool, version and install command for Windows, macOS and Linux, and tells the learner how to check it worked (`python --version`, `dotnet --version`). Run `scripts/doctor.py` yourself first so the instructions match real behaviour.
2. **No setup surprises.** Standard library by default. When a package is needed, pin the version, say why, and keep the install to one line. Provide a no-install route (Google Colab or GitHub Codespaces) for learners who cannot install software.
3. **Data included or generated.** Use small synthetic data produced by a seeded script (with the seed documented) or a public dataset with its URL, licence and size. Never depend on private data or paid services.
4. **Checkpoints with expected values.** Every lab step states what the learner should see (a number, a description of a plot, a test passing) so they know whether they are on track. Use assertions, not just printouts.
5. **Starter, then solution.** Exercises come as starter files with `TODO` markers and a failing check; solutions live in `solutions/` and are only referenced from the answer key. The learner tries first.
6. **Seeded faults.** Include at least one deliberately broken program per chapter (wrong loss, leaked data, off-by-one) and the symptom a learner will see, so debugging is practised, not just described. The fault and the fix go in the answer key.
7. **Same behaviour in both languages.** Python and C# versions solve the same task with the same expected output; note idiomatic differences.
8. **Run it, then publish it.** Everything marked runnable must pass `run_all.py` on a fresh copy. If something cannot be executed (needs a GPU, a key or a cloud account), say so and describe the expected result and cost.
9. **Make it a project.** From the practical chapters on, each lab extends the same running-example project so that by the capstone the learner owns a working, tested system, not a pile of snippets. Suggest `git init` and a commit after each lab.
10. **Safety.** No real credentials, personal data or live endpoints. Read secrets from environment variables and show how to set them.

## Lab description pattern (inside the chapter)

| Part | Content |
|---|---|
| Goal | One sentence on what exists at the end |
| Time and prerequisites | Minutes needed, files and versions required |
| Steps | Numbered, each with the action, the expected result and why it works |
| Checkpoint | A concrete check (assert or expected output) |
| If it fails | Table of symptom, likely cause, fix |
| Extension | A harder variation for the next level |
