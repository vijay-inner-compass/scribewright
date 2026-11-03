# Code examples and labs (C# and Python)

Every chapter with practical content delivers working examples in both Python and C#, following the running example. The code exists to build understanding, so it must run, be small enough to read, and match the explanation.

## Rules

1. **Both languages, same behaviour.** Show the Python version and the C# version of each key example side by side or in consecutive blocks, with the same inputs and the same expected output. Note where the languages differ idiomatically (for example LINQ vs list comprehension, nullable reference types, async models).
2. **Run everything.** Mark runnable blocks `data-run="yes"` and give `data-expect` text from the real output. Execute with `python scripts/run_snippets.py <doc>.html`. Fix failures before rendering. If a block cannot run (needs credentials, cloud, hardware, or a package that is not installed), do not mark it runnable and add a one-line note: "Not executed here: needs X."
3. **Self-contained.** Python: standard library by default; if a package is needed, state it and the install command and keep the snippet small. C#: use .NET 10 file-based apps (a single `.cs` file with top-level statements, runnable with `dotnet run file.cs`); NuGet references go in `#:package Name@version` directives at the top of the file.
4. **Pin and date.** State language and package versions used, and the date the code was last run. APIs drift; say so when it matters.
5. **Short and readable.** 10 to 40 lines per block; split bigger programs into steps. Comment the why, not the what. Descriptive names. No clever tricks.
6. **Show the output** in a `pre.code.out` block right after, so a learner can compare without running it.
7. **Secrets.** Never embed keys or tokens; read from environment variables and show how to set them.
8. **Tests as teaching.** Include at least one small assertion-based check (Python `assert`, C# `Debug.Assert` or a simple comparison with an exception) so the reader learns how to validate results.
9. **When code is not natural** for the topic (law, strategy, soft skills), provide the nearest honest equivalent: a calculation, a scoring model, a small simulation, or automation of a checklist, in both languages, and say why.

## Ship the code as files

Add `data-file="python/01_neuron.py"` (and `data-title`, and `data-pip="numpy"` when a package is needed) to each runnable block, then run `python scripts/extract_labs.py chapter.html -o labs/`. This writes the real files plus a README with setup steps, a `run_all.py` that checks every expected output, and `requirements.txt`. See `practical-implementation.md` for exercises, solutions and seeded-fault labs.

## Lab structure (practical application section)

Each lab follows this shape:

| Part | Content |
|---|---|
| Goal | One sentence: what the learner will have at the end |
| Prerequisites | Tools, versions, data; a check command that proves the setup works |
| Steps | Numbered; each step has the action, the expected result, and a way to confirm it |
| Troubleshooting | Table of symptom, likely cause, fix |
| Validation | How to prove the result is right (assertions, expected numbers, comparison to the worked example) |
| Extension | One harder variation for the next level |

## Template for a paired example

```html
<h4>Python</h4>
<pre class="code" data-lang="python" data-run="yes" data-expect="Total: 6">
items = [1, 2, 3]
print(f"Total: {sum(items)}")
</pre>
<h4>C#</h4>
<pre class="code" data-lang="csharp" data-run="yes" data-expect="Total: 6">
int[] items = { 1, 2, 3 };
Console.WriteLine($"Total: {items.Sum()}");
</pre>
<pre class="code out">Total: 6</pre>
```

Escape `<`, `>` and `&` inside code as `&lt;`, `&gt;`, `&amp;`.

## Environment check before writing code

Run `python --version` and `dotnet --version`. .NET 10 or newer is needed for file-based apps (`dotnet run file.cs`). If the SDK is missing, still write the C# but state that it was not executed.
